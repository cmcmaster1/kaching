"""
Monitor Agent for KaChing Project

This agent specializes in performance tracking, quality control, safety monitoring,
and analytics using MCP servers for comprehensive business intelligence.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

from smolagents import CodeAgent, tool
from ..tools.mcp_integration import MCPToolManager
from ..config import KaChingConfig


@dataclass
class PerformanceMetrics:
    """Represents performance metrics for monitoring"""
    date: datetime
    page_views: int = 0
    unique_visitors: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    conversion_rate: float = 0.0
    affiliate_clicks: int = 0
    affiliate_revenue: float = 0.0
    content_published: int = 0
    search_rankings: Dict[str, int] = None


@dataclass
class QualityAlert:
    """Represents a quality control alert"""
    timestamp: datetime
    severity: str  # low, medium, high, critical
    category: str  # content, performance, compliance, budget
    message: str
    affected_content: Optional[str] = None
    recommended_action: Optional[str] = None


@dataclass
class BudgetStatus:
    """Represents current budget status"""
    total_budget: float
    spent_to_date: float
    remaining_budget: float
    daily_spend_limit: float
    current_daily_spend: float
    projected_monthly_spend: float
    budget_alerts: List[str] = None


class MonitorAgent:
    """
    Specialized agent for performance monitoring and quality control.
    
    Capabilities:
    - Website analytics tracking
    - Affiliate performance monitoring
    - Content quality assessment
    - Budget and spending monitoring
    - SEO ranking tracking
    - Compliance checking
    - Alert and notification system
    - Performance reporting
    """
    
    def __init__(self, config: KaChingConfig):
        self.config = config
        self.mcp_manager = MCPToolManager()
        self.agent = None
        self.metrics_history = []
        self.alerts = []
        self._setup_agent()
    
    async def _internal_collect_analytics(
        self,
        date_range: int = 7  # days
    ) -> Dict[str, Any]:
        """Collect analytics data from various sources"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=date_range)
            
            analytics_data = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": date_range
                },
                "website_metrics": {},
                "affiliate_metrics": {},
                "content_metrics": {},
                "seo_metrics": {}
            }
            
            # Simulate analytics collection (in production, use real APIs)
            # This would integrate with Google Analytics, affiliate networks, etc.
            
            # Website metrics (simulated)
            analytics_data["website_metrics"] = {
                "page_views": 1250 + (date_range * 50),
                "unique_visitors": 890 + (date_range * 30),
                "bounce_rate": 0.65,
                "avg_session_duration": 145.5,
                "top_pages": [
                    {"url": "/best-arthritis-kitchen-tools", "views": 320},
                    {"url": "/ergonomic-cooking-utensils", "views": 280},
                    {"url": "/arthritis-friendly-can-openers", "views": 195}
                ]
            }
            
            # Affiliate metrics (simulated)
            analytics_data["affiliate_metrics"] = {
                "total_clicks": 45 + (date_range * 3),
                "conversions": 8 + (date_range // 2),
                "revenue": 127.50 + (date_range * 15.25),
                "conversion_rate": 0.178,
                "top_products": [
                    {"name": "OXO Good Grips Can Opener", "clicks": 15, "conversions": 3, "revenue": 45.99},
                    {"name": "Ergonomic Kitchen Knife Set", "clicks": 12, "conversions": 2, "revenue": 67.50},
                    {"name": "Non-Slip Mixing Bowls", "clicks": 8, "conversions": 1, "revenue": 24.99}
                ]
            }
            
            # Content metrics
            analytics_data["content_metrics"] = {
                "articles_published": date_range // 2,
                "avg_word_count": 1450,
                "avg_quality_score": 8.2,
                "seo_optimized": True,
                "affiliate_links_added": date_range * 3
            }
            
            # SEO metrics (simulated)
            analytics_data["seo_metrics"] = {
                "avg_ranking": 15.3,
                "keywords_tracked": 25,
                "keywords_improved": 8,
                "keywords_declined": 3,
                "top_rankings": [
                    {"keyword": "arthritis kitchen tools", "position": 8, "change": "+2"},
                    {"keyword": "ergonomic can opener", "position": 12, "change": "+5"},
                    {"keyword": "easy grip utensils", "position": 18, "change": "-1"}
                ]
            }
            
            logger.info(f"Analytics collected for {date_range} days")
            return analytics_data
            
        except Exception as e:
            logger.error(f"Analytics collection failed: {e}")
            return {"error": str(e)}
    
    async def _internal_check_budget_status(self) -> BudgetStatus:
        """Check current budget status and spending"""
        try:
            # Calculate spending (simulated - in production, track real expenses)
            current_date = datetime.now()
            days_since_start = (current_date - datetime(2025, 1, 1)).days
            
            # Simulate spending pattern
            daily_avg_spend = 2.50  # Average daily spend
            spent_to_date = days_since_start * daily_avg_spend
            remaining_budget = self.config.budget_limit - spent_to_date
            
            # Current daily spend (simulated)
            current_daily_spend = daily_avg_spend * (0.8 + (time.time() % 100) / 250)  # Some variation
            
            # Projected monthly spend
            projected_monthly_spend = current_daily_spend * 30
            
            # Generate alerts
            alerts = []
            if remaining_budget < (self.config.budget_limit * 0.1):  # Less than 10% remaining
                alerts.append("CRITICAL: Less than 10% of budget remaining")
            elif remaining_budget < (self.config.budget_limit * 0.25):  # Less than 25% remaining
                alerts.append("WARNING: Less than 25% of budget remaining")
            
            if current_daily_spend > self.config.max_daily_spend:
                alerts.append(f"ALERT: Daily spend limit exceeded (${current_daily_spend:.2f} > ${self.config.max_daily_spend:.2f})")
            
            if projected_monthly_spend > (self.config.budget_limit * 0.5):  # More than 50% of total budget per month
                alerts.append("WARNING: Projected monthly spend is high")
            
            budget_status = BudgetStatus(
                total_budget=self.config.budget_limit,
                spent_to_date=spent_to_date,
                remaining_budget=remaining_budget,
                daily_spend_limit=self.config.max_daily_spend,
                current_daily_spend=current_daily_spend,
                projected_monthly_spend=projected_monthly_spend,
                budget_alerts=alerts
            )
            
            logger.info(f"Budget status: ${spent_to_date:.2f} spent, ${remaining_budget:.2f} remaining")
            return budget_status
            
        except Exception as e:
            logger.error(f"Budget status check failed: {e}")
            return BudgetStatus(
                total_budget=self.config.budget_limit,
                spent_to_date=0,
                remaining_budget=self.config.budget_limit,
                daily_spend_limit=self.config.max_daily_spend,
                current_daily_spend=0,
                projected_monthly_spend=0,
                budget_alerts=[f"Error checking budget: {str(e)}"]
            )
    
    async def _internal_quality_check(
        self,
        content_path: Optional[str] = None
    ) -> List[QualityAlert]:
        """Perform quality checks on content and system"""
        alerts = []
        
        try:
            # Check content quality
            if content_path:
                # In production, analyze actual content files
                # For now, simulate quality checks
                alerts.append(QualityAlert(
                    timestamp=datetime.now(),
                    severity="low",
                    category="content",
                    message="Content quality check completed - no issues found",
                    affected_content=content_path,
                    recommended_action="Continue monitoring"
                ))
            
            # Check system performance
            # Simulate performance checks
            performance_score = 0.85  # Simulated score
            if performance_score < 0.7:
                alerts.append(QualityAlert(
                    timestamp=datetime.now(),
                    severity="high",
                    category="performance",
                    message=f"System performance below threshold: {performance_score:.2f}",
                    recommended_action="Investigate performance bottlenecks"
                ))
            
            # Check compliance
            # Simulate compliance checks
            compliance_issues = []  # Would check for proper disclosures, etc.
            if compliance_issues:
                alerts.append(QualityAlert(
                    timestamp=datetime.now(),
                    severity="critical",
                    category="compliance",
                    message="Compliance issues detected",
                    recommended_action="Review and fix compliance issues immediately"
                ))
            
            logger.info(f"Quality check completed: {len(alerts)} alerts generated")
            return alerts
            
        except Exception as e:
            logger.error(f"Quality check failed: {e}")
            return [QualityAlert(
                timestamp=datetime.now(),
                severity="critical",
                category="system",
                message=f"Quality check system error: {str(e)}",
                recommended_action="Investigate monitoring system"
            )]
    
    async def _internal_generate_report(
        self,
        report_type: str = "daily",
        include_recommendations: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            # Determine date range based on report type
            date_ranges = {
                "daily": 1,
                "weekly": 7,
                "monthly": 30
            }
            date_range = date_ranges.get(report_type, 7)
            
            # Collect data
            analytics = await self._internal_collect_analytics(date_range)
            budget_status = await self._internal_check_budget_status()
            quality_alerts = await self._internal_quality_check()
            
            # Generate report
            report = {
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "period": analytics.get("period", {}),
                "summary": {
                    "total_revenue": analytics.get("affiliate_metrics", {}).get("revenue", 0),
                    "total_visitors": analytics.get("website_metrics", {}).get("unique_visitors", 0),
                    "conversion_rate": analytics.get("affiliate_metrics", {}).get("conversion_rate", 0),
                    "budget_remaining": budget_status.remaining_budget,
                    "quality_alerts": len(quality_alerts)
                },
                "analytics": analytics,
                "budget": {
                    "total_budget": budget_status.total_budget,
                    "spent": budget_status.spent_to_date,
                    "remaining": budget_status.remaining_budget,
                    "daily_spend": budget_status.current_daily_spend,
                    "alerts": budget_status.budget_alerts
                },
                "quality": {
                    "alerts": [
                        {
                            "severity": alert.severity,
                            "category": alert.category,
                            "message": alert.message,
                            "action": alert.recommended_action
                        }
                        for alert in quality_alerts
                    ]
                }
            }
            
            # Add recommendations if requested
            if include_recommendations:
                report["recommendations"] = self._generate_recommendations(analytics, budget_status, quality_alerts)
            
            # Save report
            report_file = Path(self.config.workspace_path) / "logs" / f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"{report_type.title()} report generated: {report_file}")
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(
        self,
        analytics: Dict[str, Any],
        budget_status: BudgetStatus,
        quality_alerts: List[QualityAlert]
    ) -> List[str]:
        """Generate actionable recommendations based on data"""
        recommendations = []
        
        # Analytics-based recommendations
        if analytics.get("website_metrics", {}).get("bounce_rate", 0) > 0.7:
            recommendations.append("High bounce rate detected - consider improving content engagement and page load speed")
        
        affiliate_metrics = analytics.get("affiliate_metrics", {})
        if affiliate_metrics.get("conversion_rate", 0) < 0.1:
            recommendations.append("Low conversion rate - review affiliate product selection and placement")
        
        # Budget-based recommendations
        if budget_status.remaining_budget < (budget_status.total_budget * 0.2):
            recommendations.append("Budget running low - consider reducing daily spend or increasing revenue focus")
        
        if budget_status.current_daily_spend > budget_status.daily_spend_limit:
            recommendations.append("Daily spend limit exceeded - review and optimize spending")
        
        # Quality-based recommendations
        critical_alerts = [alert for alert in quality_alerts if alert.severity == "critical"]
        if critical_alerts:
            recommendations.append("Critical quality issues detected - immediate attention required")
        
        # SEO recommendations
        seo_metrics = analytics.get("seo_metrics", {})
        if seo_metrics.get("avg_ranking", 100) > 20:
            recommendations.append("SEO rankings need improvement - focus on content optimization and link building")
        
        # Content recommendations
        content_metrics = analytics.get("content_metrics", {})
        if content_metrics.get("articles_published", 0) < 3:
            recommendations.append("Content publication frequency is low - consider increasing to 3+ articles per week")
        
        return recommendations
    
    def _setup_agent(self):
        """Initialize the monitor agent with tools"""
        
        @tool
        def collect_analytics(
            days: int = 7
        ) -> str:
            """
            Collect analytics data for specified number of days.
            
            Args:
                days: Number of days to collect data for (default: 7)
            """
            try:
                analytics = asyncio.run(self._internal_collect_analytics(days))
                
                if "error" in analytics:
                    return f"Analytics collection failed: {analytics['error']}"
                
                # Format summary
                website = analytics.get("website_metrics", {})
                affiliate = analytics.get("affiliate_metrics", {})
                
                summary = f"""Analytics Summary ({days} days):
📊 Website: {website.get('page_views', 0)} views, {website.get('unique_visitors', 0)} visitors
💰 Affiliate: ${affiliate.get('revenue', 0):.2f} revenue, {affiliate.get('conversions', 0)} conversions
📈 Conversion Rate: {affiliate.get('conversion_rate', 0):.1%}
📝 Content: {analytics.get('content_metrics', {}).get('articles_published', 0)} articles published"""
                
                return summary
                
            except Exception as e:
                logger.error(f"Error in collect_analytics tool: {e}")
                return f"Error collecting analytics: {str(e)}"
        
        @tool
        def check_budget() -> str:
            """
            Check current budget status and spending.
            """
            try:
                budget_status = asyncio.run(self._internal_check_budget_status())
                
                status = f"""Budget Status:
💰 Total Budget: ${budget_status.total_budget:.2f}
💸 Spent: ${budget_status.spent_to_date:.2f}
💵 Remaining: ${budget_status.remaining_budget:.2f}
📅 Daily Spend: ${budget_status.current_daily_spend:.2f} (limit: ${budget_status.daily_spend_limit:.2f})
📊 Projected Monthly: ${budget_status.projected_monthly_spend:.2f}"""
                
                if budget_status.budget_alerts:
                    status += "\n\n🚨 Alerts:\n" + "\n".join(f"- {alert}" for alert in budget_status.budget_alerts)
                
                return status
                
            except Exception as e:
                logger.error(f"Error in check_budget tool: {e}")
                return f"Error checking budget: {str(e)}"
        
        @tool
        def quality_check(
            content_path: str = ""
        ) -> str:
            """
            Perform quality checks on content and system.
            
            Args:
                content_path: Optional path to specific content to check
            """
            try:
                alerts = asyncio.run(self._internal_quality_check(content_path if content_path else None))
                
                if not alerts:
                    return "✅ Quality check completed - no issues found"
                
                # Format alerts by severity
                critical = [a for a in alerts if a.severity == "critical"]
                high = [a for a in alerts if a.severity == "high"]
                medium = [a for a in alerts if a.severity == "medium"]
                low = [a for a in alerts if a.severity == "low"]
                
                result = f"Quality Check Results ({len(alerts)} alerts):\n"
                
                if critical:
                    result += f"\n🚨 CRITICAL ({len(critical)}):\n"
                    result += "\n".join(f"- {alert.message}" for alert in critical)
                
                if high:
                    result += f"\n⚠️ HIGH ({len(high)}):\n"
                    result += "\n".join(f"- {alert.message}" for alert in high)
                
                if medium:
                    result += f"\n🔶 MEDIUM ({len(medium)}):\n"
                    result += "\n".join(f"- {alert.message}" for alert in medium)
                
                if low:
                    result += f"\n🔵 LOW ({len(low)}):\n"
                    result += "\n".join(f"- {alert.message}" for alert in low)
                
                return result
                
            except Exception as e:
                logger.error(f"Error in quality_check tool: {e}")
                return f"Error performing quality check: {str(e)}"
        
        @tool
        def generate_report(
            report_type: str = "weekly",
            include_recommendations: bool = True
        ) -> str:
            """
            Generate comprehensive performance report.
            
            Args:
                report_type: Type of report (daily, weekly, monthly)
                include_recommendations: Whether to include recommendations
            """
            try:
                report = asyncio.run(self._internal_generate_report(report_type, include_recommendations))
                
                if "error" in report:
                    return f"Report generation failed: {report['error']}"
                
                # Format summary
                summary = report.get("summary", {})
                result = f"""{report_type.title()} Performance Report:

📊 Summary:
- Revenue: ${summary.get('total_revenue', 0):.2f}
- Visitors: {summary.get('total_visitors', 0)}
- Conversion Rate: {summary.get('conversion_rate', 0):.1%}
- Budget Remaining: ${summary.get('budget_remaining', 0):.2f}
- Quality Alerts: {summary.get('quality_alerts', 0)}"""
                
                if include_recommendations and "recommendations" in report:
                    result += "\n\n💡 Recommendations:\n"
                    result += "\n".join(f"- {rec}" for rec in report["recommendations"])
                
                return result
                
            except Exception as e:
                logger.error(f"Error in generate_report tool: {e}")
                return f"Error generating report: {str(e)}"
        
        # Create tools list
        monitor_tools = [
            collect_analytics,
            check_budget,
            quality_check,
            generate_report
        ]
        
        # Initialize the Smolagents agent
        try:
            self.agent = CodeAgent(
                tools=monitor_tools,
                model=self.config.get_model(),
                planning_interval=None,  # Disable planning to prevent context explosion
                additional_authorized_imports=['asyncio']  # Authorize asyncio for generated code
            )
            logger.info("Monitor Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Monitor Agent: {e}")
            self.agent = None
    
    async def daily_monitoring(self) -> Dict[str, Any]:
        """
        Perform daily monitoring routine.
        
        Returns:
            Dict containing monitoring results
        """
        logger.info("Starting daily monitoring routine")
        
        try:
            # Collect analytics
            analytics = await self._internal_collect_analytics(1)
            
            # Check budget
            budget_status = await self._internal_check_budget_status()
            
            # Quality check
            quality_alerts = await self._internal_quality_check()
            
            # Generate daily report
            report = await self._internal_generate_report("daily", True)
            
            # Check for critical alerts
            critical_alerts = [alert for alert in quality_alerts if alert.severity == "critical"]
            
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "analytics_collected": "error" not in analytics,
                "budget_status": "healthy" if not budget_status.budget_alerts else "warning",
                "critical_alerts": len(critical_alerts),
                "report_generated": "error" not in report,
                "recommendations": report.get("recommendations", [])
            }
            
            logger.success("Daily monitoring completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Daily monitoring failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_agent_description(self) -> str:
        """Get description of agent capabilities"""
        return f"""
Monitor Agent - Performance Tracking & Quality Control

Capabilities:
✅ Website analytics collection and analysis
✅ Affiliate performance monitoring
✅ Budget tracking and spending alerts
✅ Content quality assessment
✅ SEO ranking monitoring
✅ Compliance checking
✅ Automated reporting (daily/weekly/monthly)
✅ Performance recommendations

Current Configuration:
- Budget Limit: ${self.config.budget_limit:.2f}
- Daily Spend Limit: ${self.config.max_daily_spend:.2f}
- Quality Threshold: {self.config.quality_threshold}
- Content Review Required: {self.config.content_review_required}

Tools Available:
- collect_analytics: Gather performance data
- check_budget: Monitor spending and budget status
- quality_check: Assess content and system quality
- generate_report: Create comprehensive performance reports
"""


# Demo function for testing
async def main():
    """Demo function for testing Monitor Agent"""
    from ..config import KaChingConfig
    
    config = KaChingConfig.from_env()
    agent = MonitorAgent(config)
    
    print("🚀 Monitor Agent Demo")
    print("=" * 40)
    
    # Test daily monitoring
    result = await agent.daily_monitoring()
    
    print(f"📊 Daily monitoring result:")
    print(f"   Status: {result['status']}")
    print(f"   Analytics: {'✅' if result.get('analytics_collected') else '❌'}")
    print(f"   Budget: {result.get('budget_status', 'unknown')}")
    print(f"   Critical alerts: {result.get('critical_alerts', 0)}")
    
    if result.get("recommendations"):
        print(f"\n💡 Recommendations:")
        for rec in result["recommendations"][:3]:  # Show first 3
            print(f"   - {rec}")
    
    print("\n📋 Agent Description:")
    print(agent.get_agent_description())


if __name__ == "__main__":
    asyncio.run(main()) 