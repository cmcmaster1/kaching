#!/usr/bin/env python3
"""
KaChing MCP Integration Demo

This script demonstrates how to use Model Context Protocol (MCP) servers
with the KaChing affiliate content system for comprehensive research and content creation.

Usage:
    uv run examples/mcp_demo.py
"""

import asyncio
import os
from pathlib import Path
from loguru import logger

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from kaching.config import KaChingConfig
from kaching.tools.mcp_integration import MCPToolManager, setup_mcp_environment
from kaching.agents.research_agent import ResearchAgent, ResearchTask


async def demo_mcp_tool_manager():
    """Demonstrate the MCP Tool Manager capabilities"""
    logger.info("🔧 Demonstrating MCP Tool Manager")
    
    manager = MCPToolManager()
    
    # List available servers
    servers = manager.list_available_servers()
    logger.info("Available MCP servers:")
    for name, info in servers.items():
        status = "✅ Enabled" if info["enabled"] else "❌ Disabled"
        logger.info(f"  {name}: {info['description']} - {status}")
    
    # Enable search tools for demo
    manager.enable_server("brave_search")
    manager.enable_server("fetch")
    manager.enable_server("memory")
    
    logger.info("\n📡 Testing MCP server connections...")
    
    # Test search tools
    try:
        async with manager.get_search_tools() as search_tools:
            logger.success(f"Successfully connected to {len(search_tools)} search servers")
            for server_name, tool_collection in search_tools.items():
                logger.info(f"  {server_name}: {len(tool_collection.tools)} tools available")
                # List the actual tool names
                tool_names = [tool.name for tool in tool_collection.tools]
                logger.info(f"    Tools: {', '.join(tool_names)}")
    except Exception as e:
        logger.warning(f"Search tools connection failed: {e}")
    
    # Test content tools
    try:
        async with manager.get_content_tools() as content_tools:
            logger.success(f"Successfully connected to {len(content_tools)} content servers")
            for server_name, tool_collection in content_tools.items():
                logger.info(f"  {server_name}: {len(tool_collection.tools)} tools available")
                # List the actual tool names
                tool_names = [tool.name for tool in tool_collection.tools]
                logger.info(f"    Tools: {', '.join(tool_names)}")
    except Exception as e:
        logger.warning(f"Content tools connection failed: {e}")


async def demo_research_agent():
    """Demonstrate the Research Agent with MCP integration"""
    logger.info("🔍 Demonstrating Research Agent with MCP")
    
    # Create configuration
    config = KaChingConfig(
        niche="arthritis-friendly kitchen tools",
        budget_limit=1000.0,
        model_backend="inference_client",
        model_id="Qwen/Qwen2.5-Coder-32B-Instruct"
    )
    
    # Create research agent
    research_agent = ResearchAgent(config)
    
    # Define research task
    task = ResearchTask(
        niche="arthritis-friendly kitchen tools",
        keywords=[
            "arthritis kitchen tools",
            "ergonomic kitchen utensils",
            "easy grip kitchen tools",
            "arthritis cooking aids"
        ],
        competitor_urls=[
            "https://www.arthritis.org/living-with-arthritis/tools-resources/daily-living",
            "https://www.healthline.com/health/arthritis/kitchen-tools"
        ],
        research_depth="medium",
        focus_areas=["seo", "products", "content_gaps"]
    )
    
    logger.info(f"Research task: {task.niche}")
    logger.info(f"Keywords: {', '.join(task.keywords)}")
    
    # Perform quick keyword research
    logger.info("\n🎯 Performing quick keyword research...")
    try:
        keyword_results = await research_agent.quick_keyword_research(task.keywords[:2])
        logger.success("Keyword research completed")
        logger.info(f"Results preview: {keyword_results[:200]}...")
    except Exception as e:
        logger.error(f"Keyword research failed: {e}")
    
    # Analyze SERP opportunities
    logger.info("\n📊 Analyzing SERP opportunities...")
    try:
        serp_results = await research_agent.analyze_serp_opportunities(task.keywords[:2])
        logger.success("SERP analysis completed")
        logger.info(f"Results preview: {serp_results[:200]}...")
    except Exception as e:
        logger.error(f"SERP analysis failed: {e}")


async def demo_content_creation_workflow():
    """Demonstrate a complete content creation workflow using MCP"""
    logger.info("📝 Demonstrating Content Creation Workflow")
    
    config = KaChingConfig(
        niche="arthritis-friendly kitchen tools",
        budget_limit=1000.0
    )
    
    manager = MCPToolManager()
    
    # Simulate a content creation workflow
    workflow_steps = [
        "1. Research target keywords",
        "2. Analyze competitor content", 
        "3. Identify content gaps",
        "4. Research affiliate products",
        "5. Create content outline",
        "6. Generate article content",
        "7. Optimize for SEO",
        "8. Prepare for publishing"
    ]
    
    logger.info("Content creation workflow:")
    for step in workflow_steps:
        logger.info(f"  {step}")
    
    # Demonstrate tool availability for each step
    logger.info("\n🛠️ Available tools for each step:")
    
    # Step 1-4: Research tools
    try:
        async with manager.get_search_tools() as search_tools:
            logger.info(f"Research tools: {len(search_tools)} MCP servers available")
            
        async with manager.get_content_tools() as content_tools:
            logger.info(f"Content analysis tools: {len(content_tools)} MCP servers available")
            
    except Exception as e:
        logger.warning(f"Tool availability check failed: {e}")


async def demo_mcp_server_ecosystem():
    """Demonstrate the broader MCP server ecosystem"""
    logger.info("🌐 Exploring MCP Server Ecosystem")
    
    # Categories of MCP servers useful for affiliate content
    mcp_categories = {
        "Search & Research": [
            "Brave Search - Web search with API",
            "Tavily - AI-optimized search with extraction", 
            "Exa - Semantic search for AI agents",
            "Perplexity - Real-time web research",
            "Google Custom Search - Google results via API"
        ],
        "Content Creation": [
            "Firecrawl - Advanced web scraping",
            "Fetch - Web content fetching and conversion",
            "Markdownify - Convert files to Markdown",
            "Puppeteer - Browser automation",
            "YouTube - Video content research"
        ],
        "E-commerce & Affiliate": [
            "Shopify - Product research and management",
            "Amazon (via AWS) - Product data access",
            "Stripe - Payment processing insights",
            "Financial Datasets - Market data for financial products"
        ],
        "Publishing & Analytics": [
            "WordPress - Content management via REST API",
            "Google Sheets - Data management and reporting",
            "Google Analytics - Traffic and performance data",
            "Airtable - Database operations for tracking"
        ],
        "Social Media & Marketing": [
            "X (Twitter) - Social media automation",
            "LinkedIn - Professional networking content",
            "Facebook - Social media management",
            "Instagram - Visual content marketing"
        ]
    }
    
    for category, servers in mcp_categories.items():
        logger.info(f"\n📂 {category}:")
        for server in servers:
            logger.info(f"  • {server}")
    
    logger.info(f"\n🎯 Total MCP servers available: 200+ servers across all categories")
    logger.info("💡 KaChing can integrate with any of these servers for specialized functionality")


async def demo_environment_setup():
    """Demonstrate environment setup for MCP servers"""
    logger.info("⚙️ Demonstrating Environment Setup")
    
    # Check current environment
    env_status = setup_mcp_environment()
    
    if env_status:
        logger.success("All required environment variables are configured")
    else:
        logger.warning("Some environment variables are missing")
    
    # Show example environment configuration
    logger.info("\n📋 Example environment configuration:")
    example_env = {
        "BRAVE_API_KEY": "your_brave_api_key_here",
        "TAVILY_API_KEY": "your_tavily_api_key_here",
        "EXA_API_KEY": "your_exa_api_key_here",
        "FIRECRAWL_API_KEY": "your_firecrawl_api_key_here",
        "WORDPRESS_URL": "https://your-site.com",
        "WORDPRESS_USERNAME": "your_username",
        "WORDPRESS_PASSWORD": "your_app_password"
    }
    
    for key, value in example_env.items():
        current_value = os.getenv(key, "Not set")
        status = "✅" if current_value != "Not set" else "❌"
        logger.info(f"  {status} {key}: {current_value}")


async def main():
    """Main demo function"""
    logger.info("🚀 KaChing MCP Integration Demo")
    logger.info("=" * 50)
    
    demos = [
        ("Environment Setup", demo_environment_setup),
        ("MCP Tool Manager", demo_mcp_tool_manager),
        ("MCP Server Ecosystem", demo_mcp_server_ecosystem),
        ("Research Agent", demo_research_agent),
        ("Content Creation Workflow", demo_content_creation_workflow)
    ]
    
    for demo_name, demo_func in demos:
        logger.info(f"\n{'=' * 20} {demo_name} {'=' * 20}")
        try:
            await demo_func()
            logger.success(f"{demo_name} demo completed")
        except Exception as e:
            logger.error(f"{demo_name} demo failed: {e}")
        
        # Add a small delay between demos
        await asyncio.sleep(1)
    
    logger.info("\n" + "=" * 50)
    logger.info("🎉 Demo completed!")
    logger.info("\n💡 Next steps:")
    logger.info("1. Set up API keys for MCP servers you want to use")
    logger.info("2. Configure WordPress for content publishing")
    logger.info("3. Run the full KaChing orchestrator with MCP integration")
    logger.info("4. Monitor and optimize your affiliate content performance")


if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO"
    )
    
    # Run the demo
    asyncio.run(main()) 