#!/usr/bin/env python3
"""
Publishing Agent Demo

This script demonstrates the Publishing Agent capabilities including:
- WordPress publishing simulation
- Affiliate link insertion
- Content scheduling
- SEO meta data management
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kaching.config import KaChingConfig
from kaching.agents.publishing_agent import PublishingAgent, PublishingTask, AffiliateProduct


async def demo_publishing_agent():
    """Demonstrate Publishing Agent capabilities"""
    print("🚀 Publishing Agent Demo")
    print("=" * 50)
    
    # Initialize configuration and agent
    config = KaChingConfig.from_env()
    publishing_agent = PublishingAgent(config)
    
    print(f"📊 Configuration loaded:")
    print(f"   - WordPress URL: {config.wordpress_url or 'Not configured'}")
    print(f"   - Target niche: {config.niche}")
    print(f"   - Content frequency: {config.content_frequency} posts/week")
    print(f"   - Auto-publish: {config.auto_publish}")
    
    # Test 1: Agent description
    print("\n📋 Test 1: Agent Description")
    print("-" * 30)
    
    description = publishing_agent.get_agent_description()
    print(description)
    
    # Test 2: Affiliate link insertion
    print("\n🔗 Test 2: Affiliate Link Insertion")
    print("-" * 30)
    
    sample_content = """
# Best Arthritis-Friendly Kitchen Tools for 2024

Living with arthritis doesn't mean you have to give up cooking. With the right kitchen tools, you can continue to prepare delicious meals while minimizing joint pain and strain.

## Top Recommendations

### 1. OXO Good Grips Can Opener
The OXO Good Grips Smooth Edge Can Opener features large, comfortable handles that are easy to grip even with limited hand strength.

### 2. Lightweight Mixing Bowls
These non-slip mixing bowls reduce the strain on your wrists while preparing ingredients.

## Conclusion
Investing in arthritis-friendly kitchen tools can make cooking enjoyable again while protecting your joints.
"""
    
    # Create sample affiliate products
    products = [
        AffiliateProduct(
            name="OXO Good Grips Can Opener",
            url="https://amazon.com/oxo-can-opener",
            price="$19.99",
            affiliate_id="kaching-20"
        ),
        AffiliateProduct(
            name="Lightweight Mixing Bowls",
            url="https://amazon.com/mixing-bowls-set",
            price="$29.99",
            affiliate_id="kaching-20"
        )
    ]
    
    try:
        content_with_links = await publishing_agent._internal_insert_affiliate_links(
            sample_content, products
        )
        
        print("✅ Affiliate links inserted successfully!")
        print(f"📄 Content preview (first 500 chars):")
        print(content_with_links[:500] + "..." if len(content_with_links) > 500 else content_with_links)
        
    except Exception as e:
        print(f"❌ Affiliate link insertion failed: {e}")
    
    # Test 3: Content scheduling
    print("\n📅 Test 3: Content Scheduling")
    print("-" * 30)
    
    # Create sample publishing tasks
    sample_tasks = [
        PublishingTask(
            title="Best Ergonomic Kitchen Knives for Arthritis",
            content="[Content to be generated]",
            keywords=["ergonomic knives", "arthritis kitchen tools"],
            category="Reviews"
        ),
        PublishingTask(
            title="Top 5 Arthritis-Friendly Cooking Utensils",
            content="[Content to be generated]",
            keywords=["cooking utensils", "arthritis tools"],
            category="Guides"
        ),
        PublishingTask(
            title="How to Choose Kitchen Tools for Joint Pain",
            content="[Content to be generated]",
            keywords=["joint pain", "kitchen tools guide"],
            category="Guides"
        )
    ]
    
    try:
        schedule_result = await publishing_agent._internal_schedule_content(
            sample_tasks, frequency=3
        )
        
        if "error" not in schedule_result:
            print("✅ Content scheduling successful!")
            print(f"📅 Scheduled {len(schedule_result['schedule'])} posts")
            print(f"💾 Schedule saved to: {schedule_result['file']}")
            
            # Show schedule preview
            print("\n📋 Schedule Preview:")
            for item in schedule_result['schedule'][:3]:  # Show first 3
                print(f"   - {item['title']}")
                print(f"     📅 Publish: {item['publish_date'][:10]}")
                print(f"     📊 Status: {item['status']}")
        else:
            print(f"❌ Content scheduling failed: {schedule_result['error']}")
        
    except Exception as e:
        print(f"❌ Content scheduling failed: {e}")
    
    # Test 4: Quick publish (simulated)
    print("\n📝 Test 4: Quick Publish (Simulated)")
    print("-" * 30)
    
    try:
        result = await publishing_agent.quick_publish(
            title="Best Arthritis-Friendly Kitchen Tools for 2024",
            content=sample_content,
            keywords=["arthritis kitchen tools", "ergonomic cooking", "joint-friendly utensils"],
            status="draft"
        )
        
        print(f"📝 Quick publish result: {result}")
        
    except Exception as e:
        print(f"❌ Quick publish failed: {e}")
    
    # Test 5: Full publishing workflow
    print("\n🔄 Test 5: Full Publishing Workflow")
    print("-" * 30)
    
    try:
        # Create a complete publishing task
        full_task = PublishingTask(
            title="Complete Guide to Arthritis-Friendly Kitchen Setup",
            content=sample_content,
            keywords=["arthritis kitchen", "ergonomic cooking", "joint-friendly tools"],
            category="Guides",
            tags=["arthritis", "kitchen", "ergonomic", "cooking", "tools"],
            affiliate_products=[
                {
                    "name": "OXO Good Grips Can Opener",
                    "url": "https://amazon.com/oxo-can-opener",
                    "affiliate_id": "kaching-20"
                }
            ],
            meta_data={
                "_yoast_wpseo_title": "Complete Guide to Arthritis-Friendly Kitchen Setup",
                "_yoast_wpseo_metadesc": "Transform your kitchen with arthritis-friendly tools. Expert guide to ergonomic cooking equipment that reduces joint pain."
            },
            status="draft"
        )
        
        publish_result = await publishing_agent.publish_content(full_task)
        
        if publish_result["status"] == "success":
            print("✅ Full publishing workflow successful!")
            print(f"📄 Post ID: {publish_result['post_id']}")
            print(f"🌐 URL: {publish_result['url']}")
            print(f"🔗 Affiliate links added: {publish_result['affiliate_links_added']}")
        else:
            print(f"❌ Publishing workflow failed: {publish_result['error']}")
        
    except Exception as e:
        print(f"❌ Full publishing workflow failed: {e}")
    
    print("\n🎉 Publishing Agent Demo Complete!")
    print("=" * 50)
    print("\n💡 Next Steps:")
    print("- Set up WordPress hosting and configure credentials")
    print("- Test real WordPress API publishing")
    print("- Integrate with Content Agent for end-to-end workflow")
    print("- Set up affiliate program accounts and tracking")
    print("- Configure automated publishing schedule")


async def main():
    """Main demo function"""
    await demo_publishing_agent()


if __name__ == "__main__":
    asyncio.run(main()) 