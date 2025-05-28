# KaChing 💰

> An autonomous affiliate content agent that converts AU $1,000 into a hands-off internet business using Smolagents multi-agent framework with **Model Context Protocol (MCP) integration**.

## 🚀 New: MCP Integration

KaChing now includes comprehensive **Model Context Protocol (MCP)** support, giving you access to **200+ specialized tools** for affiliate content creation:

- 🔍 **Search Engines**: Brave, Tavily, Exa, Perplexity
- 📝 **Content Tools**: Firecrawl, Fetch, Markdownify, Puppeteer
- 🛒 **E-commerce**: Shopify, Amazon, Stripe, Financial APIs
- 📊 **Analytics**: Google Sheets, WordPress, Airtable
- 📱 **Social Media**: Twitter, LinkedIn, Facebook, Instagram

[**📖 Read the MCP Integration Guide →**](docs/MCP_INTEGRATION.md)

## Quick Start

1. **Read the Plan**: Check out [`PROJECT_PLAN.md`](./PROJECT_PLAN.md) for the complete roadmap
2. **Set Up Environment**:
   ```bash
   # Clone and enter the project
   git clone https://github.com/cmcmaster1/kaching.git
   cd kaching

   # Install with MCP support
   uv sync --extra mcp --extra dev

   # For Mac with Apple Silicon:
   uv sync --extra mac --extra mcp --extra dev

   # For PC with NVIDIA GPU:
   uv sync --extra pc --extra mcp --extra dev
   ```
3. **Configure MCP Servers**: Set up API keys in `.env` file
4. **Run the MCP Demo**: `uv run examples/mcp_demo.py`
5. **Start the Agent**: `uv run kaching-orchestrator`

## Installation Options

### Core Dependencies Only

```bash
uv sync
```

### With MCP Integration (Recommended)

```bash
# Basic MCP support
uv sync --extra mcp

# Mac with Apple Silicon + MCP
uv sync --extra mac --extra mcp --extra dev

# PC with NVIDIA GPU + MCP  
uv sync --extra pc --extra mcp --extra dev

# Full development setup with all features
uv sync --extra all
```

### Specific Feature Groups

```bash
# Model Context Protocol servers
uv sync --extra mcp

# WordPress integration
uv sync --extra wordpress

# SEO and keyword research tools
uv sync --extra seo

# Development tools
uv sync --extra dev
```

## Project Status

🚀 **Phase 3 Major Progress - Context Explosion Resolved**

✅ **Completed:**

- Multi-agent Smolagents architecture
- Model backend switching (MLX/LiteLLM/OpenAI/etc.)
- **MCP server integration with 200+ tools**
- **Research agent with MCP-powered keyword research (PRODUCTION READY)**
- **Content Agent with comprehensive MCP integration (PRODUCTION READY)**
- **Context explosion resolution and Gemma 3 4B optimization**
- Configuration management and environment setup
- **End-to-end research → content pipeline working efficiently**

🔄 **Current Phase:**

- **Publishing Agent development with WordPress MCP integration**
- **WordPress hosting setup and domain registration**
- **Monitor Agent with analytics MCP tools**
- **Production deployment preparation**

🎯 **Recent Major Achievement:**
- **Context Explosion Completely Resolved**: Both Research and Content agents now work efficiently with reduced context models like Gemma 3 4B
- **Performance Optimized**: 45-second end-to-end workflow from keyword research to content generation
- **Production Ready**: Both agents tested and validated for real-world use

See the [Next Steps section](./PROJECT_PLAN.md#-next-steps) in the project plan for immediate actions.

## Key Features

- 🤖 **Multi-Agent System**: Orchestrator controlling specialized agents
- 🔌 **Smolagents Framework**: Mature agent framework with tool integration
- **🌐 MCP Integration**: Access to 200+ specialized tools and services**
- 🖥️ **Flexible Backends**: MLX-LM (Mac) or Ollama/vLLM via LiteLLM (PC)
- ⏸️ **Pause-able**: Complete control via scheduler file
- 💰 **Profit-Focused**: Targets >AU $5,000/year revenue
- 🛡️ **Safe & Legal**: Built-in compliance and safety mechanisms

## Multi-Agent Architecture with MCP

### Orchestrator Agent

- **Role**: Task delegation, progress tracking, error handling
- **Framework**: Smolagents CodeAgent with planning_interval
- **Controls**: All specialized agents via managed_agents

### Specialized Agents with MCP Tools

- **Research Agent**:
  - Keyword research via Brave Search, Tavily, Exa
  - Competitor analysis via Firecrawl, Puppeteer
  - Product research via Shopify, Amazon APIs
  - **Context Optimized**: Direct internal methods, no planning system
  - **Production Ready**: Tested with Gemma 3 4B, 8 keywords/run

- **Content Agent**:
  - Content creation using MCP tools (Brave Search, Fetch active)
  - SEO optimization with analytics APIs integration
  - Template application with Markdownify
  - **Context Optimized**: Async orchestration, efficient token usage
  - **Production Ready**: 502-word articles in 45 seconds

- **Publishing Agent**:
  - WordPress publishing via REST API (in development)
  - Social media distribution via Twitter/LinkedIn APIs
  - Analytics tracking via Google Sheets

- **Monitor Agent**:
  - Performance tracking via Google Analytics (planned)
  - Quality control with content analysis tools
  - Safety checks with compliance APIs

## MCP Server Examples

### Search & Research

```python
# Multiple search engines for comprehensive research
async with mcp_manager.get_search_tools() as search_tools:
    # Brave Search for web results
    # Tavily for AI-optimized extraction  
    # Exa for semantic search
    # Perplexity for real-time research
```

### Content Creation

```python
# Advanced content tools
async with mcp_manager.get_content_tools() as content_tools:
    # Firecrawl for web scraping
    # Fetch for content conversion
    # Markdownify for format conversion
    # Puppeteer for browser automation
```

### E-commerce Integration

```python
# Product and affiliate research
async with mcp_manager.get_ecommerce_tools() as ecommerce_tools:
    # Shopify for product data
    # Amazon APIs for affiliate products
    # Stripe for payment insights
    # Financial APIs for market data
```

## 🎯 Context Optimization & Gemma 3 4B

### Problem Solved: Context Explosion

The project successfully resolved context explosion issues that were causing poor output quality and inefficient token usage.

### Solution Implemented

- **Research Agent Refactoring**: Replaced planning system with direct internal methods
- **Content Agent Optimization**: Enhanced existing async orchestration approach  
- **Model Configuration**: Fixed MLX parameter conflicts for Gemma 3 4B
- **Rate Limiting**: Added comprehensive delays across all MCP integrations

### Performance Results

```bash
# Research Agent Performance
✅ 8 keyword opportunities identified
✅ Commercial intent analysis working
✅ Competitor analysis with content fetching
✅ Rate limiting prevents API overload

# Content Agent Performance  
✅ 502-word SEO-optimized articles
✅ 45-second end-to-end generation
✅ Brave Search + Fetch integration
✅ Quality scoring and optimization

# Model Compatibility
✅ Gemma 3 4B (1024 tokens) - Tested
✅ MLX backend optimization
✅ Context efficiency restored
✅ Production-ready performance
```

### Testing with Gemma 3 4B

```bash
# Set environment for Gemma model
export KACHING_MODEL_BACKEND=mlx
export KACHING_MODEL_ID=mlx-community/gemma-3-4b-it-qat-4bit
export KACHING_MAX_TOKENS=1024

# Test optimized agents
uv run examples/test_with_gemma.py
```

## Target Niche

**Arthritis-Friendly Kitchen Tools**

- High affiliate potential
- Clear target audience
- Automation-friendly content types
- **Enhanced with MCP tools for comprehensive research**

## Budget

- **Total**: AU $1,000
- **Initial Spend**: AU $315
- **Reserve**: AU $685

## Technical Architecture

```
┌─────────────────────┐
│ Orchestrator Agent  │  (CodeAgent with planning_interval=3)
│ - Task delegation   │
│ - Progress tracking │
│ - Error handling    │
└─────────┬───────────┘
          │ managed_agents
┌─────────▼───────────┐
│ Specialized Agents  │
├─────────────────────┤
│ Research Agent      │  → MCP: Brave, Tavily, Exa, Firecrawl
│ Content Agent       │  → MCP: Markdownify, Fetch, Puppeteer  
│ Publishing Agent    │  → MCP: WordPress, Twitter, Google Sheets
│ Monitor Agent       │  → MCP: Analytics, Airtable, Monitoring
└─────────────────────┘
          │
┌─────────▼───────────┐
│ MCP Tool Manager    │
├─────────────────────┤
│ • 200+ MCP Servers  │  → Search, Content, E-commerce, Analytics
│ • Connection Pool   │  → Async tool management
│ • Error Recovery    │  → Fallback and retry logic
│ • Security Layer    │  → Sandboxed execution
└─────────────────────┘
          │
┌─────────▼───────────┐
│ Model Backends      │
├─────────────────────┤
│ Mac: MLXModel       │  → MLX-LM for Apple Silicon
│ PC: LiteLLMModel    │  → Ollama/vLLM for NVIDIA GPU
│ Cloud: OpenAI/etc   │  → API-based models
└─────────────────────┘
```

## Model Backend Examples

### Mac with Apple Silicon (MLX)

```python
from kaching.config import KaChingConfig
from kaching.orchestrator import KaChingOrchestrator

# Method 1: Use convenience method
config = KaChingConfig.create_for_mac()

# Method 2: Environment variables
# KACHING_MODEL_BACKEND=mlx
# KACHING_MODEL_ID=mlx-community/Phi-3-mini-4k-instruct-4bit

orchestrator = KaChingOrchestrator(config)
```

### PC with NVIDIA GPU (Ollama via LiteLLM)

```python
# Method 1: Use convenience method
config = KaChingConfig.create_for_pc_ollama()

# Method 2: Environment variables
# KACHING_MODEL_BACKEND=litellm
# KACHING_MODEL_ID=ollama/phi3:mini
# LITELLM_PROVIDER=ollama

orchestrator = KaChingOrchestrator(config)
```

### With MCP Integration

```python
# Any model backend + MCP tools
config = KaChingConfig.from_env()
orchestrator = KaChingOrchestrator(config)

# MCP tools are automatically available to all agents
research_results = await orchestrator.research_agent.quick_keyword_research([
    "arthritis kitchen tools"
])
```

## Environment Variables

### Core Configuration

```bash
KACHING_NICHE="arthritis-friendly kitchen tools"
KACHING_BUDGET_LIMIT=1000.0
KACHING_WORKSPACE="./workspace"
```

### Model Configuration

```bash
# Choose your backend
KACHING_MODEL_BACKEND=mlx  # mlx, litellm, vllm, transformers, inference_client, openai, azure_openai, bedrock

# Model settings
KACHING_MODEL_ID="mlx-community/Phi-3-mini-4k-instruct-4bit"
KACHING_MAX_TOKENS=2048
KACHING_TEMPERATURE=0.7
KACHING_PLANNING_INTERVAL=3
```

### MCP Server Configuration

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

### Backend-Specific Settings

#### MLX (Mac)

```bash
MLX_TRUST_REMOTE_CODE=false
```

#### LiteLLM (Ollama/OpenAI/etc.)

```bash
LITELLM_PROVIDER=ollama
LITELLM_API_KEY=your_api_key
LITELLM_BASE_URL=http://localhost:11434
```

#### OpenAI

```bash
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
```

## MCP Quick Start

### 1. Install MCP Dependencies

```bash
uv sync --extra mcp
```

### 2. Set Up API Keys

```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

### 3. Test MCP Integration

```bash
# Run the MCP demo
uv run examples/mcp_demo.py

# Test specific research functionality
uv run -c "
from kaching.tools.mcp_integration import MCPToolManager
manager = MCPToolManager()
print(manager.list_available_servers())
"
```

### 4. Start Research Agent

```python
from kaching.config import KaChingConfig
from kaching.agents.research_agent import ResearchAgent

config = KaChingConfig.from_env()
agent = ResearchAgent(config)

# Quick keyword research with MCP tools
results = await agent.quick_keyword_research([
    "arthritis kitchen tools",
    "ergonomic cooking utensils"
])
```

## Contributing

This is a personal project, but feel free to:

- Suggest improvements via issues
- Share similar experiences
- Contribute to the research tasks
- Test Smolagents integration patterns
- **Suggest new MCP servers for integration**

## License

MIT License - See LICENSE file for details.

---

**Disclaimer**: This project involves affiliate marketing and automated content generation. Ensure compliance with all applicable laws and platform terms of service in your jurisdiction.

**MCP Integration**: The Model Context Protocol integration provides access to external tools and services. Review the terms of service for each MCP server you use and ensure proper API key management.
