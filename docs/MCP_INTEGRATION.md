# MCP Integration Guide for KaChing

## Overview

The KaChing project now includes comprehensive integration with the **Model Context Protocol (MCP)**, giving you access to hundreds of specialized tools and services for affiliate content creation. This integration transforms KaChing from a basic agent system into a powerful ecosystem that can leverage the entire MCP server marketplace.

## What is MCP?

Model Context Protocol (MCP) is an open standard that allows AI applications to securely connect to data sources and tools. Think of MCP as a "USB-C for AI" - it provides a standardized way for AI agents to access external services, databases, APIs, and tools.

### Key Benefits for KaChing

- **200+ Available Tools**: Access to search engines, content tools, e-commerce APIs, analytics platforms, and more
- **Standardized Interface**: All tools work the same way, regardless of the underlying service
- **Security**: Sandboxed execution with controlled access to external resources
- **Extensibility**: Easy to add new capabilities without changing core code
- **Community Ecosystem**: Leverage tools built by the broader AI community

## Architecture

```
┌─────────────────────┐
│ KaChing Agents      │
├─────────────────────┤
│ • Research Agent    │ ──┐
│ • Content Agent     │   │
│ • Publishing Agent  │   │ Uses MCP Tools
│ • Monitor Agent     │   │
└─────────────────────┘   │
                          │
┌─────────────────────────▼─┐
│ MCPToolManager            │
├───────────────────────────┤
│ • Server Management       │
│ • Tool Collection         │
│ • Connection Handling     │
│ • Error Recovery          │
└─────────────────────────┬─┘
                          │
┌─────────────────────────▼─┐
│ MCP Servers               │
├───────────────────────────┤
│ Search: Brave, Tavily     │
│ Content: Firecrawl, Fetch │
│ Publishing: WordPress     │
│ Analytics: Google Sheets  │
│ E-commerce: Shopify       │
└───────────────────────────┘
```

## Available MCP Server Categories

### 🔍 Search & Research
- **Brave Search**: Web search with comprehensive results
- **Tavily**: AI-optimized search with content extraction
- **Exa**: Semantic search designed for AI agents
- **Perplexity**: Real-time web research with citations
- **Google Custom Search**: Google results via API

### 📝 Content Creation
- **Firecrawl**: Advanced web scraping with JavaScript rendering
- **Fetch**: Web content fetching and conversion for LLMs
- **Markdownify**: Convert various file formats to Markdown
- **Puppeteer**: Browser automation and web scraping
- **YouTube**: Video content research and analysis

### 🛒 E-commerce & Affiliate
- **Shopify**: Product research and management
- **Amazon (via AWS)**: Product data and affiliate integration
- **Stripe**: Payment processing insights
- **Financial Datasets**: Market data for financial products

### 📊 Publishing & Analytics
- **WordPress**: Content management via REST API
- **Google Sheets**: Data management and reporting
- **Google Analytics**: Traffic and performance tracking
- **Airtable**: Database operations for content tracking

### 📱 Social Media & Marketing
- **X (Twitter)**: Social media automation
- **LinkedIn**: Professional networking content
- **Facebook**: Social media management
- **Instagram**: Visual content marketing

## Installation

### 1. Install MCP Dependencies

```bash
# Install KaChing with MCP support
uv sync --extra mcp

# Or install specific MCP servers manually
uvx install brave-search-mcp
uvx install tavily-mcp
uvx install firecrawl-mcp-server
```

### 2. Environment Configuration

Create a `.env` file with your API keys:

```bash
# Search APIs
BRAVE_API_KEY=your_brave_api_key
TAVILY_API_KEY=your_tavily_api_key
EXA_API_KEY=your_exa_api_key

# Content Tools
FIRECRAWL_API_KEY=your_firecrawl_api_key

# Publishing
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your_username
WORDPRESS_PASSWORD=your_app_password

# Analytics
GOOGLE_SHEETS_CREDENTIALS=/path/to/credentials.json
```

### 3. Verify Installation

```bash
# Run the MCP demo
uv run examples/mcp_demo.py

# Check available servers
python -c "from kaching.tools.mcp_integration import MCPToolManager; print(MCPToolManager().list_available_servers())"
```

## Usage Examples

### Basic MCP Tool Manager

```python
from kaching.tools.mcp_integration import MCPToolManager

# Initialize the manager
manager = MCPToolManager()

# List available servers
servers = manager.list_available_servers()
for name, info in servers.items():
    print(f"{name}: {info['description']} - {'Enabled' if info['enabled'] else 'Disabled'}")

# Enable specific servers
manager.enable_server("brave_search")
manager.enable_server("firecrawl")

# Use search tools
async with manager.get_search_tools() as search_tools:
    for server_name, tool_collection in search_tools.items():
        print(f"Server: {server_name}")
        for tool in tool_collection.tools:
            print(f"  Tool: {tool.name}")
```

### Research Agent with MCP

```python
from kaching.config import KaChingConfig
from kaching.agents.research_agent import ResearchAgent, ResearchTask

# Configure KaChing
config = KaChingConfig(
    niche="arthritis-friendly kitchen tools",
    model_backend="inference_client",
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct"
)

# Create research agent
research_agent = ResearchAgent(config)

# Define research task
task = ResearchTask(
    niche="arthritis-friendly kitchen tools",
    keywords=["arthritis kitchen tools", "ergonomic utensils"],
    competitor_urls=["https://example-competitor.com"],
    research_depth="medium",
    focus_areas=["seo", "products", "content_gaps"]
)

# Conduct research
results = await research_agent.conduct_research(task)
print(results["results"])
```

### Custom MCP Server Integration

```python
from kaching.tools.mcp_integration import MCPServerConfig, MCPToolManager

# Add a custom MCP server
custom_server = MCPServerConfig(
    name="custom_tool",
    description="My custom research tool",
    command="uvx",
    args=["--quiet", "my-custom-mcp-server"],
    env={"UV_PYTHON": "3.12", **os.environ}
)

manager = MCPToolManager()
manager.add_custom_server(custom_server)

# Use the custom server
async with manager.get_tools_for_servers(["custom_tool"]) as tools:
    # Use your custom tools
    pass
```

## Agent Integration

### Research Agent

The Research Agent uses MCP servers for:
- **Keyword Research**: Multiple search engines for comprehensive keyword discovery
- **Competitor Analysis**: Web scraping tools to analyze competitor content
- **Content Gap Analysis**: Search tools to identify content opportunities
- **Product Research**: E-commerce APIs for affiliate product discovery

```python
# Quick keyword research
keywords = await research_agent.quick_keyword_research([
    "arthritis kitchen tools",
    "ergonomic cooking utensils"
])

# SERP analysis
serp_analysis = await research_agent.analyze_serp_opportunities([
    "best arthritis kitchen tools",
    "ergonomic can opener review"
])
```

### Content Agent (Future)

The Content Agent will use MCP servers for:
- **Content Research**: Fetch and analyze existing content
- **SEO Optimization**: Keyword density and optimization tools
- **Fact Checking**: Multiple sources for content verification
- **Content Enhancement**: Additional data and insights

### Publishing Agent (Future)

The Publishing Agent will use MCP servers for:
- **WordPress Publishing**: Direct content publishing via REST API
- **Social Media**: Cross-platform content distribution
- **Analytics Integration**: Performance tracking and reporting
- **Link Management**: Affiliate link optimization and tracking

## Configuration

### Server Management

```python
from kaching.tools.mcp_integration import MCPToolManager

manager = MCPToolManager()

# Enable/disable servers
manager.enable_server("brave_search")
manager.disable_server("shopify")  # Disable if not needed

# Check server status
servers = manager.list_available_servers()
enabled_servers = [name for name, info in servers.items() if info["enabled"]]
print(f"Enabled servers: {enabled_servers}")
```

### Environment Setup

```python
from kaching.tools.mcp_integration import setup_mcp_environment

# Check environment configuration
env_ok = setup_mcp_environment()
if not env_ok:
    print("Some environment variables are missing")
    print("Check the logs for details")
```

### Tool Categories

```python
# Get tools by category
async with manager.get_search_tools() as search_tools:
    # Use search and research tools
    pass

async with manager.get_content_tools() as content_tools:
    # Use content creation and processing tools
    pass

async with manager.get_wordpress_tools() as wp_tools:
    # Use WordPress publishing tools
    pass

async with manager.get_analytics_tools() as analytics_tools:
    # Use analytics and reporting tools
    pass
```

## Best Practices

### 1. Server Selection

- **Start Small**: Enable only the servers you need initially
- **Test Connections**: Verify API keys and connectivity before production use
- **Monitor Usage**: Track API usage and costs for paid services
- **Fallback Options**: Configure multiple search engines for redundancy

### 2. Error Handling

```python
try:
    async with manager.get_search_tools() as search_tools:
        # Use tools
        pass
except Exception as e:
    logger.error(f"MCP server error: {e}")
    # Fallback to alternative approach
```

### 3. Performance Optimization

- **Connection Pooling**: Reuse MCP connections when possible
- **Async Operations**: Use async/await for concurrent tool usage
- **Caching**: Cache results to reduce API calls
- **Rate Limiting**: Respect API rate limits

### 4. Security

- **API Key Management**: Store API keys securely in environment variables
- **Trust Settings**: Only use `trust_remote_code=True` for trusted servers
- **Access Control**: Limit server access based on agent roles
- **Monitoring**: Log all MCP server interactions for audit trails

## Troubleshooting

### Common Issues

1. **Server Connection Failed**
   ```bash
   # Check if the MCP server is installed
   uvx list
   
   # Install missing server
   uvx install brave-search-mcp
   ```

2. **API Key Issues**
   ```bash
   # Verify environment variables
   echo $BRAVE_API_KEY
   
   # Check .env file
   cat .env | grep API_KEY
   ```

3. **Tool Not Found**
   ```python
   # List available tools
   async with manager.get_search_tools() as tools:
       for server, collection in tools.items():
           print(f"{server}: {[tool.name for tool in collection.tools]}")
   ```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed MCP logging
from loguru import logger
logger.add("mcp_debug.log", level="DEBUG")
```

## Future Enhancements

### Planned Integrations

1. **Advanced Analytics**: Google Analytics, Search Console integration
2. **Social Media**: Automated posting and engagement tracking
3. **E-commerce**: Amazon Product API, affiliate network integrations
4. **Content Enhancement**: AI writing assistants, grammar checkers
5. **SEO Tools**: Rank tracking, backlink analysis, technical SEO

### Custom Server Development

You can create custom MCP servers for specialized needs:

```python
# Example: Custom affiliate tracking server
from mcp import Server, Tool

class AffiliateTrackingServer(Server):
    @Tool("track_clicks")
    async def track_clicks(self, affiliate_link: str) -> dict:
        # Custom affiliate tracking logic
        return {"clicks": 42, "conversions": 3}
```

## Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **Server Registry**: https://glama.ai/mcp/servers
- **Smolagents MCP Guide**: https://huggingface.co/docs/smolagents/tutorials/tools
- **Community Servers**: https://github.com/modelcontextprotocol/servers

## Support

For MCP-related issues:

1. Check the [MCP server documentation](https://glama.ai/mcp/servers)
2. Verify your API keys and environment setup
3. Test individual servers with `mcp-cli`
4. Review the KaChing logs for detailed error messages
5. Open an issue with specific error details and configuration

---

The MCP integration transforms KaChing into a powerful, extensible platform that can leverage the entire ecosystem of AI tools and services. Start with the basic search and content tools, then expand to specialized servers as your affiliate business grows. 