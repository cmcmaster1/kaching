#!/usr/bin/env python3
"""
Content Agent Demo for KaChing Project

This script demonstrates the Content Agent's capabilities for content creation,
SEO optimization, and quality control using MCP tools.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import nest_asyncio
nest_asyncio.apply()

from kaching.config import KaChingConfig
from kaching.agents.content_agent import ContentAgent, ContentTask


async def demo_content_agent():
    """Demonstrate Content Agent capabilities"""
    
    print("🎯 KaChing Content Agent Demo")
    print("=" * 50)
    
    # Initialize configuration
    config = KaChingConfig.from_env()
    print(f"✅ Configuration loaded: {config.model_backend} with {config.model_id}")
    
    # Initialize Content Agent
    content_agent = ContentAgent(config)
    print("✅ Content Agent initialized with MCP tools")
    
    # Test 1: Quick content generation
    print("\n📝 Test 1: Quick Content Generation")
    print("-" * 30)
    
    try:
        result = await content_agent.quick_content_generation(
            title="Best Arthritis-Friendly Can Openers for 2025",
            keywords=["arthritis can opener", "ergonomic can opener", "easy grip can opener"],
            content_type="review"
        )
        
        print("✅ Quick content generation successful!")
        print(f"📄 Content preview (first 500 chars):")
        print(result[:500] + "..." if len(result) > 500 else result)
        
    except Exception as e:
        print(f"❌ Quick content generation failed: {e}")
    
    # Test 2: Structured content creation with ContentTask
    print("\n🏗️ Test 2: Structured Content Creation")
    print("-" * 30)
    
    try:
        # Create a content task
        task = ContentTask(
            title="Top 5 Arthritis-Friendly Kitchen Knives: Complete Buying Guide",
            keywords=["arthritis kitchen knives", "ergonomic knives", "easy grip knives"],
            content_type="guide",
            target_word_count=2000,
            affiliate_products=["OXO Good Grips Knife", "Wusthof Ergonomic Knife", "Victorinox Swiss Classic"],
            quality_threshold=8.0
        )
        
        result = await content_agent.create_content(task)
        
        if result["status"] == "success":
            print("✅ Structured content creation successful!")
            print(f"📊 Task: {task.title}")
            print(f"📈 Target word count: {task.target_word_count}")
            print(f"🎯 Keywords: {', '.join(task.keywords)}")
            print(f"📄 Content preview (first 300 chars):")
            content_preview = result["content"][:300] + "..." if len(result["content"]) > 300 else result["content"]
            print(content_preview)
        else:
            print(f"❌ Structured content creation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Structured content creation failed: {e}")
    
    # Test 3: Content optimization
    print("\n🔧 Test 3: Content Optimization")
    print("-" * 30)
    
    sample_content = """
# Kitchen Tools for Arthritis

Cooking can be challenging when you have arthritis. This guide helps you find the right tools.

## What to Look For

When choosing kitchen tools, consider ergonomic design and ease of use.

## Top Recommendations

Here are some good options to consider for your kitchen.
"""
    
    try:
        optimized = await content_agent.optimize_existing_content(
            content=sample_content,
            keywords=["arthritis kitchen tools", "ergonomic cooking"]
        )
        
        print("✅ Content optimization successful!")
        print(f"📄 Optimized content preview (first 400 chars):")
        print(optimized[:400] + "..." if len(optimized) > 400 else optimized)
        
    except Exception as e:
        print(f"❌ Content optimization failed: {e}")
    
    # Test 4: Agent description
    print("\n📋 Test 4: Agent Description")
    print("-" * 30)
    
    description = content_agent.get_agent_description()
    print("✅ Agent description retrieved:")
    print(description)
    
    print("\n🎉 Content Agent Demo Complete!")
    print("=" * 50)
    print("\n💡 Next Steps:")
    print("- Test content generation with different templates")
    print("- Integrate with Research Agent for keyword-driven content")
    print("- Set up Publishing Agent for WordPress integration")
    print("- Create end-to-end content workflow")


async def demo_content_templates():
    """Demonstrate different content templates"""
    
    print("\n📋 Content Templates Demo")
    print("=" * 30)
    
    config = KaChingConfig.from_env()
    content_agent = ContentAgent(config)
    
    # Test different content types
    content_types = ["review", "comparison", "guide", "listicle"]
    
    for content_type in content_types:
        print(f"\n🔍 Testing {content_type} template...")
        
        try:
            result = await content_agent.quick_content_generation(
                title=f"Best Arthritis Kitchen Tools - {content_type.title()}",
                keywords=["arthritis kitchen tools", "ergonomic cooking"],
                content_type=content_type
            )
            
            print(f"✅ {content_type.title()} template successful!")
            # Show just the structure (headings)
            lines = result.split('\n')
            headings = [line for line in lines if line.startswith('#')]
            print(f"📋 Structure: {len(headings)} headings found")
            for heading in headings[:5]:  # Show first 5 headings
                print(f"   {heading}")
            if len(headings) > 5:
                print(f"   ... and {len(headings) - 5} more")
                
        except Exception as e:
            print(f"❌ {content_type.title()} template failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting KaChing Content Agent Demo...")
    
    # Run the main demo
    asyncio.run(demo_content_agent())
    
    # Run template demo
    asyncio.run(demo_content_templates())
    
    print("\n✨ All demos completed!") 