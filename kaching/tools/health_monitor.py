#!/usr/bin/env python3
"""
KaChing Health Monitor Service

Provides health monitoring, status reporting, and alerting for the KaChing system.
Runs as a separate service to monitor the main orchestrator and system health.
"""

import asyncio
import json
import time
import psutil
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from loguru import logger
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from ..config import KaChingConfig


@dataclass
class HealthStatus:
    """Health status data structure"""
    timestamp: str
    overall_status: str  # healthy, warning, critical
    services: Dict[str, str]
    resources: Dict[str, Any]
    alerts: List[str]
    uptime: str
    last_activity: str


@dataclass
class SystemMetrics:
    """System resource metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    load_average: List[float]


class HealthMonitor:
    """Health monitoring service for KaChing"""
    
    def __init__(self, config: KaChingConfig):
        self.config = config
        self.workspace_path = Path(config.workspace_path)
        self.start_time = datetime.now()
        self.alerts = []
        self.last_check = datetime.now()
        
        # Setup logging
        log_file = self.workspace_path / "logs" / "health_monitor.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_file,
            rotation="1 day",
            retention="30 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        
        # FastAPI app for status endpoints
        self.app = FastAPI(title="KaChing Health Monitor", version="1.0.0")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes for health endpoints"""
        
        @self.app.get("/health")
        async def health_check():
            """Simple health check endpoint"""
            status = await self.get_health_status()
            if status.overall_status == "critical":
                raise HTTPException(status_code=503, detail="System unhealthy")
            return {"status": "healthy", "timestamp": status.timestamp}
        
        @self.app.get("/status")
        async def detailed_status():
            """Detailed system status"""
            status = await self.get_health_status()
            return JSONResponse(content=asdict(status))
        
        @self.app.get("/metrics")
        async def system_metrics():
            """System resource metrics"""
            metrics = self.get_system_metrics()
            return JSONResponse(content=asdict(metrics))
        
        @self.app.get("/alerts")
        async def current_alerts():
            """Current system alerts"""
            return {"alerts": self.alerts, "count": len(self.alerts)}
    
    async def get_health_status(self) -> HealthStatus:
        """Get comprehensive health status"""
        
        # Check services
        services = await self.check_services()
        
        # Get system metrics
        metrics = self.get_system_metrics()
        
        # Check for alerts
        self.check_alerts(services, metrics)
        
        # Determine overall status
        overall_status = self.determine_overall_status(services, metrics)
        
        # Get last activity
        last_activity = self.get_last_activity()
        
        return HealthStatus(
            timestamp=datetime.now().isoformat(),
            overall_status=overall_status,
            services=services,
            resources={
                "cpu_percent": metrics.cpu_percent,
                "memory_percent": metrics.memory_percent,
                "disk_percent": metrics.disk_percent,
                "load_average": metrics.load_average
            },
            alerts=self.alerts[-10:],  # Last 10 alerts
            uptime=str(datetime.now() - self.start_time),
            last_activity=last_activity
        )
    
    async def check_services(self) -> Dict[str, str]:
        """Check status of KaChing services"""
        services = {}
        
        # Check systemd services
        service_names = [
            "kaching-orchestrator",
            "ollama",
            "nginx"
        ]
        
        for service in service_names:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                services[service] = result.stdout.strip()
            except subprocess.TimeoutExpired:
                services[service] = "timeout"
            except Exception as e:
                services[service] = f"error: {str(e)}"
        
        # Check Ollama API
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:11434/api/version")
                services["ollama_api"] = "active" if response.status_code == 200 else "inactive"
        except Exception:
            services["ollama_api"] = "inactive"
        
        # Check workspace accessibility
        try:
            if self.workspace_path.exists() and self.workspace_path.is_dir():
                services["workspace"] = "accessible"
            else:
                services["workspace"] = "inaccessible"
        except Exception:
            services["workspace"] = "error"
        
        return services
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get system resource metrics"""
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Network I/O
        network = psutil.net_io_counters()
        network_io = {
            "bytes_sent": network.bytes_sent,
            "bytes_recv": network.bytes_recv
        }
        
        # Process count
        process_count = len(psutil.pids())
        
        # Load average
        load_average = list(psutil.getloadavg())
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
            network_io=network_io,
            process_count=process_count,
            load_average=load_average
        )
    
    def check_alerts(self, services: Dict[str, str], metrics: SystemMetrics):
        """Check for alert conditions"""
        current_time = datetime.now()
        new_alerts = []
        
        # Service alerts
        for service, status in services.items():
            if status not in ["active", "accessible"]:
                new_alerts.append(f"Service {service} is {status}")
        
        # Resource alerts
        if metrics.cpu_percent > 90:
            new_alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > 90:
            new_alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.disk_percent > 90:
            new_alerts.append(f"High disk usage: {metrics.disk_percent:.1f}%")
        
        # Budget alerts (if configured)
        try:
            budget_file = self.workspace_path / "logs" / "budget.json"
            if budget_file.exists():
                with open(budget_file) as f:
                    budget_data = json.load(f)
                    spent = budget_data.get("total_spent", 0)
                    limit = self.config.budget_limit
                    
                    if spent > limit * 0.9:
                        new_alerts.append(f"Budget warning: ${spent:.2f} / ${limit:.2f}")
                    
                    if spent > limit:
                        new_alerts.append(f"Budget exceeded: ${spent:.2f} / ${limit:.2f}")
        except Exception:
            pass
        
        # Add new alerts with timestamps
        for alert in new_alerts:
            alert_entry = f"[{current_time.strftime('%H:%M:%S')}] {alert}"
            if alert_entry not in self.alerts:
                self.alerts.append(alert_entry)
                logger.warning(f"Alert: {alert}")
        
        # Clean old alerts (keep last 100)
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def determine_overall_status(self, services: Dict[str, str], metrics: SystemMetrics) -> str:
        """Determine overall system status"""
        
        # Critical conditions
        critical_services = ["kaching-orchestrator", "ollama"]
        for service in critical_services:
            if services.get(service) != "active":
                return "critical"
        
        if metrics.cpu_percent > 95 or metrics.memory_percent > 95 or metrics.disk_percent > 95:
            return "critical"
        
        # Warning conditions
        if any(status not in ["active", "accessible"] for status in services.values()):
            return "warning"
        
        if metrics.cpu_percent > 80 or metrics.memory_percent > 80 or metrics.disk_percent > 80:
            return "warning"
        
        return "healthy"
    
    def get_last_activity(self) -> str:
        """Get timestamp of last system activity"""
        try:
            log_files = [
                self.workspace_path / "logs" / "kaching.log",
                self.workspace_path / "logs" / "orchestrator.log"
            ]
            
            latest_time = None
            for log_file in log_files:
                if log_file.exists():
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if latest_time is None or mtime > latest_time:
                        latest_time = mtime
            
            if latest_time:
                return latest_time.isoformat()
            else:
                return "unknown"
        except Exception:
            return "error"
    
    async def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Health monitor started")
        
        while True:
            try:
                # Get health status
                status = await self.get_health_status()
                
                # Log status periodically
                if datetime.now().minute % 15 == 0:  # Every 15 minutes
                    logger.info(f"System status: {status.overall_status}")
                    if status.alerts:
                        logger.warning(f"Active alerts: {len(status.alerts)}")
                
                # Save status to file
                status_file = self.workspace_path / "logs" / "health_status.json"
                status_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(status_file, 'w') as f:
                    json.dump(asdict(status), f, indent=2)
                
                self.last_check = datetime.now()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            # Wait before next check
            await asyncio.sleep(30)  # Check every 30 seconds
    
    async def start_server(self):
        """Start the health monitoring server"""
        config = uvicorn.Config(
            self.app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        # Run monitoring loop and server concurrently
        await asyncio.gather(
            self.monitoring_loop(),
            server.serve()
        )


async def main():
    """Main entry point for health monitor service"""
    try:
        # Load configuration
        config = KaChingConfig.from_env()
        
        # Create and start health monitor
        monitor = HealthMonitor(config)
        await monitor.start_server()
        
    except KeyboardInterrupt:
        logger.info("Health monitor stopped by user")
    except Exception as e:
        logger.error(f"Health monitor error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 