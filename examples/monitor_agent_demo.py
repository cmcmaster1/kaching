#!/usr/bin/env python3
"""
Monitor Agent Demo

This script demonstrates the Monitor Agent capabilities including:
- Analytics collection and analysis
- Budget tracking and alerts
- Quality control checks
- Performance reporting
- Automated monitoring routines
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kaching.config import KaChingConfig
from kaching.agents.monitor_agent import MonitorAgent


async def demo_monitor_agent():
    """Demonstrate Monitor Agent capabilities"""
    print("🚀 Monitor Agent Demo")
    print("=" * 50)
    
    # Initialize configuration and agent
    config = KaChingConfig.from_env()
    monitor_agent = MonitorAgent(config)
    
    print(f"📊 Configuration loaded:")
    print(f"   - Budget limit: ${config.budget_limit:.2f}")
    print(f"   - Daily spend limit: ${config.max_daily_spend:.2f}")
    print(f"   - Quality threshold: {config.quality_threshold}")
    print(f"   - Content review required: {config.content_review_required}")
    
    # Test 1: Agent description
    print("\n📋 Test 1: Agent Description")
    print("-" * 30)
    
    description = monitor_agent.get_agent_description()
    print(description)
    
    # Test 2: Analytics collection
    print("\n📊 Test 2: Analytics Collection")
    print("-" * 30)
    
    try:
        analytics = await monitor_agent._internal_collect_analytics(7)
        
        if "error" not in analytics:
            print("✅ Analytics collection successful!")
            
            # Display website metrics
            website = analytics.get("website_metrics", {})
            print(f"📈 Website Metrics (7 days):")
            print(f"   - Page views: {website.get('page_views', 0):,}")
            print(f"   - Unique visitors: {website.get('unique_visitors', 0):,}")
            print(f"   - Bounce rate: {website.get('bounce_rate', 0):.1%}")
            print(f"   - Avg session: {website.get('avg_session_duration', 0):.1f}s")
            
            # Display affiliate metrics
            affiliate = analytics.get("affiliate_metrics", {})
            print(f"\n💰 Affiliate Metrics:")
            print(f"   - Total clicks: {affiliate.get('total_clicks', 0)}")
            print(f"   - Conversions: {affiliate.get('conversions', 0)}")
            print(f"   - Revenue: ${affiliate.get('revenue', 0):.2f}")
            print(f"   - Conversion rate: {affiliate.get('conversion_rate', 0):.1%}")
            
            # Display top products
            top_products = affiliate.get("top_products", [])
            if top_products:
                print(f"\n🏆 Top Products:")
                for i, product in enumerate(top_products[:3], 1):
                    print(f"   {i}. {product['name']}: {product['clicks']} clicks, ${product['revenue']:.2f}")
        else:
            print(f"❌ Analytics collection failed: {analytics['error']}")
        
    except Exception as e:
        print(f"❌ Analytics collection failed: {e}")
    
    # Test 3: Budget monitoring
    print("\n💰 Test 3: Budget Monitoring")
    print("-" * 30)
    
    try:
        budget_status = await monitor_agent._internal_check_budget_status()
        
        print("✅ Budget monitoring successful!")
        print(f"💰 Budget Status:")
        print(f"   - Total budget: ${budget_status.total_budget:.2f}")
        print(f"   - Spent to date: ${budget_status.spent_to_date:.2f}")
        print(f"   - Remaining: ${budget_status.remaining_budget:.2f}")
        print(f"   - Daily spend: ${budget_status.current_daily_spend:.2f}")
        print(f"   - Daily limit: ${budget_status.daily_spend_limit:.2f}")
        print(f"   - Projected monthly: ${budget_status.projected_monthly_spend:.2f}")
        
        if budget_status.budget_alerts:
            print(f"\n🚨 Budget Alerts:")
            for alert in budget_status.budget_alerts:
                print(f"   - {alert}")
        else:
            print(f"\n✅ No budget alerts")
        
    except Exception as e:
        print(f"❌ Budget monitoring failed: {e}")
    
    # Test 4: Quality checks
    print("\n🔍 Test 4: Quality Checks")
    print("-" * 30)
    
    try:
        quality_alerts = await monitor_agent._internal_quality_check()
        
        print("✅ Quality check completed!")
        
        if quality_alerts:
            # Group alerts by severity
            critical = [a for a in quality_alerts if a.severity == "critical"]
            high = [a for a in quality_alerts if a.severity == "high"]
            medium = [a for a in quality_alerts if a.severity == "medium"]
            low = [a for a in quality_alerts if a.severity == "low"]
            
            print(f"📊 Quality Alerts Summary:")
            print(f"   - Critical: {len(critical)}")
            print(f"   - High: {len(high)}")
            print(f"   - Medium: {len(medium)}")
            print(f"   - Low: {len(low)}")
            
            # Show first few alerts
            for alert in quality_alerts[:3]:
                print(f"\n{alert.severity.upper()}: {alert.message}")
                if alert.recommended_action:
                    print(f"   Action: {alert.recommended_action}")
        else:
            print("✅ No quality issues detected")
        
    except Exception as e:
        print(f"❌ Quality check failed: {e}")
    
    # Test 5: Report generation
    print("\n📄 Test 5: Report Generation")
    print("-" * 30)
    
    try:
        report = await monitor_agent._internal_generate_report("weekly", True)
        
        if "error" not in report:
            print("✅ Report generation successful!")
            
            summary = report.get("summary", {})
            print(f"📊 Weekly Report Summary:")
            print(f"   - Revenue: ${summary.get('total_revenue', 0):.2f}")
            print(f"   - Visitors: {summary.get('total_visitors', 0):,}")
            print(f"   - Conversion rate: {summary.get('conversion_rate', 0):.1%}")
            print(f"   - Budget remaining: ${summary.get('budget_remaining', 0):.2f}")
            print(f"   - Quality alerts: {summary.get('quality_alerts', 0)}")
            
            # Show recommendations
            recommendations = report.get("recommendations", [])
            if recommendations:
                print(f"\n💡 Recommendations:")
                for i, rec in enumerate(recommendations[:5], 1):
                    print(f"   {i}. {rec}")
            
            print(f"\n💾 Report saved to workspace/logs/")
        else:
            print(f"❌ Report generation failed: {report['error']}")
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
    
    # Test 6: Daily monitoring routine
    print("\n🔄 Test 6: Daily Monitoring Routine")
    print("-" * 30)
    
    try:
        result = await monitor_agent.daily_monitoring()
        
        print(f"📊 Daily monitoring result:")
        print(f"   - Status: {result['status']}")
        print(f"   - Analytics collected: {'✅' if result.get('analytics_collected') else '❌'}")
        print(f"   - Budget status: {result.get('budget_status', 'unknown')}")
        print(f"   - Critical alerts: {result.get('critical_alerts', 0)}")
        print(f"   - Report generated: {'✅' if result.get('report_generated') else '❌'}")
        
        if result.get("recommendations"):
            print(f"\n💡 Top Recommendations:")
            for i, rec in enumerate(result["recommendations"][:3], 1):
                print(f"   {i}. {rec}")
        
    except Exception as e:
        print(f"❌ Daily monitoring failed: {e}")
    
    print("\n🎉 Monitor Agent Demo Complete!")
    print("=" * 50)
    print("\n💡 Next Steps:")
    print("- Integrate with real analytics APIs (Google Analytics, etc.)")
    print("- Set up automated daily monitoring schedule")
    print("- Configure alert notifications (email, Slack, etc.)")
    print("- Connect to affiliate network APIs for real revenue tracking")
    print("- Implement SEO ranking monitoring with real tools")


async def main():
    """Main demo function"""
    await demo_monitor_agent()


if __name__ == "__main__":
    asyncio.run(main()) 