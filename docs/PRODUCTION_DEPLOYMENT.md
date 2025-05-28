# Production Deployment Guide for KaChing

This guide covers deploying the KaChing autonomous affiliate content system for hands-off operation in production.

## 🎯 Overview

The KaChing system is designed to run autonomously with minimal intervention. This guide helps you deploy it to production with proper monitoring, scheduling, and error recovery.

## 📋 Prerequisites

Before deployment, ensure you have:

- ✅ All four agents tested and working (Research, Content, Publishing, Monitor)
- ✅ WordPress site configured with REST API access
- ✅ Affiliate programs approved and configured
- ✅ Domain and hosting set up
- ✅ Environment variables configured
- ✅ End-to-end workflow tested successfully

## 🚀 Deployment Options

### Option 1: Local Mac Deployment (Recommended for Testing)

**Best for**: Development, testing, small-scale operation

**Requirements:**
- Mac with Apple Silicon (M1/M2/M3)
- 8GB+ RAM
- 50GB+ free storage
- Stable internet connection

**Pros:**
- No additional hosting costs
- Full control over environment
- Easy debugging and monitoring
- MLX optimization for Apple Silicon

**Cons:**
- Requires computer to stay on
- Limited scalability
- Single point of failure

### Option 2: VPS Cloud Deployment

**Best for**: Production, scalability, reliability

**Recommended Providers:**
- **DigitalOcean** (AU $12-24/month) - Developer-friendly
- **Vultr** (AU $10-20/month) - High performance
- **Linode** (AU $10-20/month) - Reliable cloud hosting
- **AWS EC2** (AU $15-30/month) - Enterprise-grade

**Pros:**
- 24/7 operation
- Professional reliability
- Scalable resources
- Automated backups

**Cons:**
- Monthly hosting costs
- Requires server management
- Network dependency

### Option 3: Serverless Deployment

**Best for**: Cost optimization, automatic scaling

**Platforms:**
- **AWS Lambda** + EventBridge
- **Google Cloud Functions** + Cloud Scheduler
- **Azure Functions** + Logic Apps

**Pros:**
- Pay-per-execution
- Automatic scaling
- No server management
- Built-in monitoring

**Cons:**
- Complex setup
- Cold start delays
- Execution time limits
- Vendor lock-in

## 🛠️ VPS Deployment (Recommended)

### Step 1: Server Setup

#### Create VPS Instance

```bash
# DigitalOcean example
# Choose Ubuntu 22.04 LTS
# Select 2GB RAM, 1 vCPU, 50GB SSD ($12/month)
# Add SSH key for security
# Choose region closest to Australia
```

#### Initial Server Configuration

```bash
# Connect to server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Create non-root user
adduser kaching
usermod -aG sudo kaching
su - kaching

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git curl -y

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### Step 2: Application Deployment

#### Clone and Setup Project

```bash
# Clone repository
git clone https://github.com/your-username/kaching.git
cd kaching

# Install dependencies
uv sync --extra all

# Create environment file
cp .env.example .env
nano .env  # Configure your settings
```

#### Configure Environment Variables

```bash
# Production environment settings
cat > .env << EOF
# Core Configuration
KACHING_NICHE="arthritis-friendly kitchen tools"
KACHING_BUDGET_LIMIT=1000.0
KACHING_WORKSPACE="/home/kaching/kaching/workspace"
KACHING_ENVIRONMENT=production

# Model Configuration
KACHING_MODEL_BACKEND=litellm
KACHING_MODEL_ID=ollama/gemma:3b
KACHING_MAX_TOKENS=1024
KACHING_TEMPERATURE=0.7

# WordPress Configuration
WORDPRESS_URL=https://yourdomain.com
WORDPRESS_USERNAME=your_username
WORDPRESS_PASSWORD=your_app_password

# Affiliate Configuration
AMAZON_ASSOCIATE_ID=your-associate-id-20

# MCP API Keys
BRAVE_API_KEY=your_brave_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Monitoring
ENABLE_MONITORING=true
LOG_LEVEL=INFO
EOF
```

### Step 3: Model Backend Setup

#### Option A: Ollama Setup (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
sudo systemctl enable ollama
sudo systemctl start ollama

# Pull required model
ollama pull gemma:3b

# Test model
ollama run gemma:3b "Hello, test message"
```

#### Option B: OpenAI API Setup

```bash
# Add to .env
echo "OPENAI_API_KEY=your_openai_api_key" >> .env
echo "KACHING_MODEL_BACKEND=openai" >> .env
echo "KACHING_MODEL_ID=gpt-3.5-turbo" >> .env
```

### Step 4: Systemd Service Configuration

#### Create Service File

```bash
sudo nano /etc/systemd/system/kaching.service
```

```ini
[Unit]
Description=KaChing Autonomous Affiliate Content Agent
After=network.target
Wants=network.target

[Service]
Type=simple
User=kaching
Group=kaching
WorkingDirectory=/home/kaching/kaching
Environment=PATH=/home/kaching/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/kaching/.local/bin/uv run python -m kaching.orchestrator
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryMax=2G
CPUQuota=80%

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/kaching/kaching/workspace

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable kaching

# Start service
sudo systemctl start kaching

# Check status
sudo systemctl status kaching

# View logs
sudo journalctl -u kaching -f
```

### Step 5: Automated Scheduling

#### Create Scheduler Script

```bash
nano /home/kaching/kaching/scripts/scheduler.py
```

```python
#!/usr/bin/env python3
"""
KaChing Production Scheduler

Manages automated content generation and publishing schedule.
"""

import asyncio
import schedule
import time
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kaching.config import KaChingConfig
from kaching.agents import ResearchAgent, ContentAgent, PublishingAgent, MonitorAgent


class ProductionScheduler:
    def __init__(self):
        self.config = KaChingConfig.from_env()
        self.research_agent = ResearchAgent(self.config)
        self.content_agent = ContentAgent(self.config)
        self.publishing_agent = PublishingAgent(self.config)
        self.monitor_agent = MonitorAgent(self.config)
    
    async def daily_content_generation(self):
        """Generate and publish daily content"""
        try:
            print(f"[{datetime.now()}] Starting daily content generation...")
            
            # Research keywords
            keywords = await self.research_agent.quick_keyword_research([
                "arthritis kitchen tools",
                "ergonomic cooking utensils",
                "easy grip kitchen gadgets"
            ])
            
            # Generate content
            content = await self.content_agent.quick_content_generation(
                title="Daily Arthritis-Friendly Kitchen Tool Review",
                keywords=["arthritis kitchen tools", "ergonomic cooking"],
                content_type="review",
                word_count=1200
            )
            
            # Publish content
            result = await self.publishing_agent.quick_publish(
                title="Daily Arthritis-Friendly Kitchen Tool Review",
                content=content,
                keywords=["arthritis kitchen tools", "ergonomic cooking"],
                status="publish"
            )
            
            print(f"[{datetime.now()}] Content generation completed: {result}")
            
        except Exception as e:
            print(f"[{datetime.now()}] Error in daily content generation: {e}")
    
    async def daily_monitoring(self):
        """Perform daily monitoring and reporting"""
        try:
            print(f"[{datetime.now()}] Starting daily monitoring...")
            
            result = await self.monitor_agent.daily_monitoring()
            
            print(f"[{datetime.now()}] Daily monitoring completed: {result['status']}")
            
        except Exception as e:
            print(f"[{datetime.now()}] Error in daily monitoring: {e}")
    
    def run_async_job(self, coro):
        """Helper to run async jobs in sync scheduler"""
        asyncio.run(coro)
    
    def setup_schedule(self):
        """Set up the production schedule"""
        # Content generation: Monday, Wednesday, Friday at 9 AM
        schedule.every().monday.at("09:00").do(
            self.run_async_job, self.daily_content_generation()
        )
        schedule.every().wednesday.at("09:00").do(
            self.run_async_job, self.daily_content_generation()
        )
        schedule.every().friday.at("09:00").do(
            self.run_async_job, self.daily_content_generation()
        )
        
        # Daily monitoring at 6 PM
        schedule.every().day.at("18:00").do(
            self.run_async_job, self.daily_monitoring()
        )
        
        print("Production schedule configured:")
        print("- Content generation: Mon/Wed/Fri at 9:00 AM")
        print("- Daily monitoring: Every day at 6:00 PM")
    
    def run(self):
        """Run the scheduler"""
        self.setup_schedule()
        
        print(f"[{datetime.now()}] KaChing Production Scheduler started")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


if __name__ == "__main__":
    scheduler = ProductionScheduler()
    scheduler.run()
```

#### Create Scheduler Service

```bash
sudo nano /etc/systemd/system/kaching-scheduler.service
```

```ini
[Unit]
Description=KaChing Production Scheduler
After=network.target kaching.service
Wants=network.target

[Service]
Type=simple
User=kaching
Group=kaching
WorkingDirectory=/home/kaching/kaching
Environment=PATH=/home/kaching/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/kaching/.local/bin/uv run python scripts/scheduler.py
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start scheduler
sudo systemctl enable kaching-scheduler
sudo systemctl start kaching-scheduler
sudo systemctl status kaching-scheduler
```

## 📊 Monitoring and Alerting

### Log Management

#### Configure Log Rotation

```bash
sudo nano /etc/logrotate.d/kaching
```

```
/home/kaching/kaching/workspace/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 kaching kaching
}
```

#### Centralized Logging

```bash
# Install and configure rsyslog for centralized logging
sudo apt install rsyslog -y

# Configure custom log destination
echo "local0.*    /var/log/kaching.log" | sudo tee -a /etc/rsyslog.conf
sudo systemctl restart rsyslog
```

### Health Monitoring

#### Create Health Check Script

```bash
nano /home/kaching/kaching/scripts/health_check.py
```

```python
#!/usr/bin/env python3
"""
KaChing Health Check Script

Monitors system health and sends alerts if issues detected.
"""

import asyncio
import requests
import psutil
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from kaching.config import KaChingConfig


class HealthChecker:
    def __init__(self):
        self.config = KaChingConfig.from_env()
        self.alerts = []
    
    def check_system_resources(self):
        """Check CPU, memory, and disk usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if cpu_percent > 80:
            self.alerts.append(f"High CPU usage: {cpu_percent}%")
        
        if memory.percent > 85:
            self.alerts.append(f"High memory usage: {memory.percent}%")
        
        if disk.percent > 90:
            self.alerts.append(f"High disk usage: {disk.percent}%")
    
    def check_wordpress_connectivity(self):
        """Check WordPress site accessibility"""
        try:
            response = requests.get(self.config.wordpress_url, timeout=10)
            if response.status_code != 200:
                self.alerts.append(f"WordPress site not accessible: {response.status_code}")
        except Exception as e:
            self.alerts.append(f"WordPress connectivity error: {str(e)}")
    
    def check_log_errors(self):
        """Check recent logs for errors"""
        log_dir = Path(self.config.workspace_path) / "logs"
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                # Check last 100 lines for errors
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-100:]
                        error_count = sum(1 for line in lines if "ERROR" in line)
                        if error_count > 5:
                            self.alerts.append(f"High error count in {log_file.name}: {error_count}")
                except Exception:
                    pass
    
    def send_alerts(self):
        """Send alerts if any issues found"""
        if self.alerts:
            alert_message = f"KaChing Health Check Alerts ({datetime.now()}):\n"
            alert_message += "\n".join(f"- {alert}" for alert in self.alerts)
            
            # Log alerts
            print(alert_message)
            
            # Here you could integrate with:
            # - Email notifications
            # - Slack webhooks
            # - Discord webhooks
            # - SMS services
    
    def run_health_check(self):
        """Run complete health check"""
        print(f"[{datetime.now()}] Running health check...")
        
        self.check_system_resources()
        self.check_wordpress_connectivity()
        self.check_log_errors()
        
        if self.alerts:
            self.send_alerts()
        else:
            print(f"[{datetime.now()}] Health check passed - no issues detected")


if __name__ == "__main__":
    checker = HealthChecker()
    checker.run_health_check()
```

#### Schedule Health Checks

```bash
# Add to crontab
crontab -e

# Add this line to run health check every 30 minutes
*/30 * * * * /home/kaching/.local/bin/uv run python /home/kaching/kaching/scripts/health_check.py >> /var/log/kaching-health.log 2>&1
```

## 🔧 Performance Optimization

### Resource Optimization

```bash
# Optimize system for production
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
echo 'net.core.rmem_max=16777216' | sudo tee -a /etc/sysctl.conf
echo 'net.core.wmem_max=16777216' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### Database Optimization

```bash
# If using local database, optimize MySQL/PostgreSQL
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Add optimizations:
# innodb_buffer_pool_size = 512M
# query_cache_size = 64M
# max_connections = 100
```

## 🚨 Backup and Recovery

### Automated Backups

```bash
nano /home/kaching/kaching/scripts/backup.sh
```

```bash
#!/bin/bash
# KaChing Backup Script

BACKUP_DIR="/home/kaching/backups"
DATE=$(date +%Y%m%d_%H%M%S)
WORKSPACE_DIR="/home/kaching/kaching/workspace"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup workspace
tar -czf "$BACKUP_DIR/workspace_$DATE.tar.gz" -C "$WORKSPACE_DIR" .

# Backup configuration
cp /home/kaching/kaching/.env "$BACKUP_DIR/env_$DATE.backup"

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.backup" -mtime +30 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable and schedule
chmod +x /home/kaching/kaching/scripts/backup.sh

# Add to crontab for daily backups at 2 AM
crontab -e
# Add: 0 2 * * * /home/kaching/kaching/scripts/backup.sh >> /var/log/kaching-backup.log 2>&1
```

## 🧪 Testing Production Deployment

### Pre-deployment Checklist

- [ ] All environment variables configured
- [ ] WordPress connectivity tested
- [ ] Affiliate links working
- [ ] Model backend responding
- [ ] MCP servers accessible
- [ ] Logs directory writable
- [ ] Backup script working
- [ ] Health checks passing

### Deployment Testing

```bash
# Test end-to-end workflow
uv run examples/end_to_end_demo.py

# Test individual agents
uv run examples/research_agent_demo.py
uv run examples/content_agent_demo.py
uv run examples/publishing_agent_demo.py
uv run examples/monitor_agent_demo.py

# Test scheduler
python scripts/scheduler.py --test

# Test health check
python scripts/health_check.py
```

## 📈 Scaling Considerations

### Horizontal Scaling

```bash
# Multiple VPS instances with load balancer
# Separate content generation from publishing
# Database clustering for high availability
```

### Vertical Scaling

```bash
# Upgrade VPS resources as needed
# Monitor resource usage trends
# Optimize model parameters for performance
```

## 🎯 Go-Live Checklist

Final steps before production:

- [ ] Domain DNS configured
- [ ] SSL certificate installed
- [ ] WordPress fully configured
- [ ] Affiliate programs approved
- [ ] All services running
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] Health checks active
- [ ] Error alerting set up
- [ ] Performance baseline established

## 📞 Support and Maintenance

### Regular Maintenance Tasks

**Weekly:**
- Review system logs
- Check affiliate performance
- Monitor resource usage
- Verify backup integrity

**Monthly:**
- Update system packages
- Review and optimize content
- Analyze performance metrics
- Update affiliate links

**Quarterly:**
- Security audit
- Performance optimization
- Backup strategy review
- Disaster recovery testing

---

*This guide is part of the KaChing autonomous affiliate content system. For more information, see the main project documentation.* 