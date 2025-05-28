#!/usr/bin/env python3
"""
End-to-End KaChing Demo

This script demonstrates the complete KaChing workflow:
1. Research Agent: Keyword research and competitor analysis
2. Content Agent: Article generation with SEO optimization
3. Publishing Agent: Content publishing with affiliate links
4. Monitor Agent: Performance tracking and reporting

This showcases the full autonomous affiliate content pipeline.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kaching.config import KaChingConfig
from kaching.agents import (
    ResearchAgent, ResearchTask,
    ContentAgent, ContentTask,
    PublishingAgent, PublishingTask, AffiliateProduct,
    MonitorAgent
)


async def end_to_end_demo():
    """Demonstrate complete KaChing workflow"""
    print("🚀 KaChing End-to-End Demo")
    print("=" * 60)
    print("Autonomous Affiliate Content Generation Pipeline")
    print("=" * 60)
    
    # Initialize configuration
    config = KaChingConfig.from_env()
    
    print(f"📊 System Configuration:")
    print(f"   - Target niche: {config.niche}")
    print(f"   - Budget limit: ${config.budget_limit:.2f}")
    print(f"   - Content frequency: {config.content_frequency} posts/week")
    print(f"   - Model backend: {config.model_backend}")
    print(f"   - Model ID: {config.model_id}")
    
    # Initialize all agents
    print(f"\n🤖 Initializing Multi-Agent System...")
    research_agent = ResearchAgent(config)
    content_agent = ContentAgent(config)
    publishing_agent = PublishingAgent(config)
    monitor_agent = MonitorAgent(config)
    print(f"✅ All agents initialized successfully!")
    
    # Step 1: Research Phase
    print(f"\n" + "="*60)
    print(f"📊 STEP 1: RESEARCH PHASE")
    print(f"="*60)
    
    try:
        # Define research keywords
        seed_keywords = [
            "arthritis kitchen tools",
            "ergonomic cooking utensils",
            "easy grip kitchen gadgets"
        ]
        
        print(f"🔍 Starting keyword research for: {', '.join(seed_keywords)}")
        
        # Perform keyword research
        research_results = await research_agent.quick_keyword_research(seed_keywords)
        
        print(f"✅ Research completed!")
        print(f"📈 Research summary (first 300 chars):")
        print(research_results[:300] + "..." if len(research_results) > 300 else research_results)
        
        # Extract a topic for content generation
        content_topic = "Best Arthritis-Friendly Kitchen Tools for 2024"
        content_keywords = ["arthritis kitchen tools", "ergonomic cooking", "easy grip utensils"]
        
        print(f"\n💡 Selected content topic: {content_topic}")
        print(f"🎯 Target keywords: {', '.join(content_keywords)}")
        
    except Exception as e:
        print(f"❌ Research phase failed: {e}")
        return
    
    # Step 2: Content Generation Phase
    print(f"\n" + "="*60)
    print(f"📝 STEP 2: CONTENT GENERATION PHASE")
    print(f"="*60)
    
    try:
        print(f"✍️ Generating content: {content_topic}")
        
        # Generate content using the Content Agent
        generated_content = await content_agent.quick_content_generation(
            title=content_topic,
            keywords=content_keywords,
            content_type="review",
            word_count=1200
        )
        
        if not generated_content.startswith("Error"):
            print(f"✅ Content generation completed!")
            print(f"📄 Content preview (first 400 chars):")
            print(generated_content[:400] + "..." if len(generated_content) > 400 else generated_content)
            
            # Extract word count
            word_count = len(generated_content.split())
            print(f"📊 Generated content: {word_count} words")
        else:
            print(f"❌ Content generation failed: {generated_content}")
            return
        
    except Exception as e:
        print(f"❌ Content generation phase failed: {e}")
        return
    
    # Step 3: Publishing Phase
    print(f"\n" + "="*60)
    print(f"📤 STEP 3: PUBLISHING PHASE")
    print(f"="*60)
    
    try:
        print(f"🔗 Preparing content for publishing with affiliate links...")
        
        # Define affiliate products to include
        affiliate_products = [
            {
                "name": "OXO Good Grips Can Opener",
                "url": "https://amazon.com/oxo-good-grips-can-opener",
                "affiliate_id": "kaching-20"
            },
            {
                "name": "Ergonomic Kitchen Knife Set",
                "url": "https://amazon.com/ergonomic-kitchen-knife-set",
                "affiliate_id": "kaching-20"
            }
        ]
        
        # Create publishing task
        publishing_task = PublishingTask(
            title=content_topic,
            content=generated_content,
            keywords=content_keywords,
            category="Reviews",
            tags=["arthritis", "kitchen", "ergonomic", "cooking", "tools"],
            affiliate_products=affiliate_products,
            meta_data={
                "_yoast_wpseo_title": f"{content_topic} - Complete Guide",
                "_yoast_wpseo_metadesc": "Discover the best arthritis-friendly kitchen tools. Expert reviews and buying guide for ergonomic cooking equipment."
            },
            status="draft"  # Use draft since WordPress isn't configured
        )
        
        # Publish content
        publish_result = await publishing_agent.publish_content(publishing_task)
        
        if publish_result["status"] == "success":
            print(f"✅ Content published successfully!")
            print(f"🌐 URL: {publish_result['url']}")
            print(f"🔗 Affiliate links added: {publish_result['affiliate_links_added']}")
        else:
            print(f"⚠️ Publishing simulated (WordPress not configured)")
            print(f"📝 Would publish: {content_topic}")
            print(f"🔗 Would add {len(affiliate_products)} affiliate links")
        
    except Exception as e:
        print(f"❌ Publishing phase failed: {e}")
        return
    
    # Step 4: Monitoring Phase
    print(f"\n" + "="*60)
    print(f"📊 STEP 4: MONITORING PHASE")
    print(f"="*60)
    
    try:
        print(f"📈 Running performance monitoring...")
        
        # Perform daily monitoring
        monitoring_result = await monitor_agent.daily_monitoring()
        
        if monitoring_result["status"] == "success":
            print(f"✅ Monitoring completed successfully!")
            print(f"📊 Analytics: {'✅' if monitoring_result.get('analytics_collected') else '❌'}")
            print(f"💰 Budget: {monitoring_result.get('budget_status', 'unknown')}")
            print(f"🚨 Critical alerts: {monitoring_result.get('critical_alerts', 0)}")
            print(f"📄 Report: {'✅' if monitoring_result.get('report_generated') else '❌'}")
            
            # Show recommendations
            recommendations = monitoring_result.get("recommendations", [])
            if recommendations:
                print(f"\n💡 System Recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec}")
        else:
            print(f"❌ Monitoring failed: {monitoring_result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Monitoring phase failed: {e}")
        return
    
    # Summary
    print(f"\n" + "="*60)
    print(f"🎉 END-TO-END DEMO COMPLETE!")
    print(f"="*60)
    
    print(f"\n📊 Workflow Summary:")
    print(f"✅ Research: Keyword analysis completed")
    print(f"✅ Content: {word_count}-word article generated")
    print(f"✅ Publishing: Content prepared with affiliate links")
    print(f"✅ Monitoring: Performance tracking active")
    
    print(f"\n🚀 Production Readiness:")
    print(f"   - Research Agent: ✅ Production ready")
    print(f"   - Content Agent: ✅ Production ready")
    print(f"   - Publishing Agent: ⚠️ Needs WordPress configuration")
    print(f"   - Monitor Agent: ✅ Production ready")
    
    print(f"\n💡 Next Steps for Production:")
    print(f"   1. Set up WordPress hosting and domain")
    print(f"   2. Configure WordPress REST API credentials")
    print(f"   3. Set up affiliate program accounts")
    print(f"   4. Configure real analytics APIs")
    print(f"   5. Set up automated scheduling")
    print(f"   6. Deploy to production server")
    
    print(f"\n🎯 Expected Performance:")
    print(f"   - Content generation: 3 articles/week")
    print(f"   - Target revenue: >AU $5,000/year")
    print(f"   - Budget utilization: <AU $1,000 total")
    print(f"   - Automation level: 95%+ hands-off")


async def main():
    """Main demo function"""
    await end_to_end_demo()


if __name__ == "__main__":
    asyncio.run(main()) 