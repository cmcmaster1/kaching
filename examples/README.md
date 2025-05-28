# KaChing Examples

This directory contains demonstration scripts and usage examples for the KaChing autonomous affiliate content system.

## 🚀 Getting Started

### Core Demos

- **`end_to_end_demo.py`** - Complete workflow demonstration from research to publishing
- **`config_demo.py`** - Configuration management and template usage examples

### Agent-Specific Demos

- **`content_agent_demo.py`** - Content generation and SEO optimization
- **`publishing_agent_demo.py`** - WordPress publishing and affiliate link management  
- **`monitor_agent_demo.py`** - System monitoring and performance tracking
- **`keyword_research_demo.py`** - Keyword research and competitor analysis

### MCP Integration

- **`mcp_demo.py`** - Model Context Protocol integration with 200+ tools

## 🏃‍♂️ Quick Start

```bash
# Run the complete end-to-end demo
uv run examples/end_to_end_demo.py

# Test configuration management
uv run examples/config_demo.py

# Try MCP tool integration
uv run examples/mcp_demo.py
```

## 📋 Prerequisites

- KaChing environment configured (see `env.example`)
- Required API keys set up
- Model backend configured (MLX, LiteLLM, etc.)

## 🔧 Configuration

Most examples use the default configuration from environment variables. You can override settings by editing the configuration at the top of each script.

## 📚 Documentation

For detailed setup and usage instructions, see the `/docs` directory:
- [Production Deployment](../docs/PRODUCTION_DEPLOYMENT.md)
- [WordPress Setup](../docs/WORDPRESS_SETUP.md)
- [Affiliate Setup](../docs/AFFILIATE_SETUP.md)
- [MCP Integration](../docs/MCP_INTEGRATION.md) 