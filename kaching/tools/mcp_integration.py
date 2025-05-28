"""
MCP Integration Manager for KaChing Project

This module provides a centralized way to manage and integrate multiple MCP servers
for affiliate content generation, including search, content creation, and analytics tools.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass
from loguru import logger

from smolagents import ToolCollection
from mcp import StdioServerParameters


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    description: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    enabled: bool = True


class MCPToolManager:
    """
    Manages multiple MCP servers for the KaChing affiliate content system.
    
    Provides access to search engines, content tools, WordPress integration,
    and affiliate research capabilities through standardized MCP servers.
    """
    
    def __init__(self):
        self.server_configs = self._get_default_server_configs()
        self.active_tools = {}
        self.tool_collections = {}
        
    def _get_default_server_configs(self) -> Dict[str, MCPServerConfig]:
        """Define the default MCP servers for KaChing"""
        return {
            # Search and Research Tools
            "brave_search": MCPServerConfig(
                name="brave_search",
                description="Web and local search using Brave's Search API",
                command="npx",
                args=["-q", "@modelcontextprotocol/server-brave-search"],
                env={"UV_PYTHON": "3.12", **os.environ}
            ),
            
            "fetch": MCPServerConfig(
                name="fetch",
                description="Web content fetching and conversion for LLM usage",
                command="npx",
                args=["-q", "@tokenizin/mcp-npx-fetch"],
                env={"UV_PYTHON": "3.12", **os.environ}
            ),
            
            "filesystem": MCPServerConfig(
                name="filesystem",
                description="Secure file operations with configurable access controls",
                command="npx",
                args=["-q", "@modelcontextprotocol/server-filesystem", "/tmp"],
                env={"UV_PYTHON": "3.12", **os.environ}
            ),
            
            "github": MCPServerConfig(
                name="github",
                description="Repository management, file operations, and GitHub API integration",
                command="npx",
                args=["-q", "@modelcontextprotocol/server-github"],
                env={"UV_PYTHON": "3.12", **os.environ},
                enabled=False  # Enable when GitHub token is configured
            ),
            
            "memory": MCPServerConfig(
                name="memory",
                description="Knowledge graph-based persistent memory system",
                command="npx",
                args=["-q", "@modelcontextprotocol/server-memory"],
                env={"UV_PYTHON": "3.12", **os.environ}
            ),
            
            "puppeteer": MCPServerConfig(
                name="puppeteer",
                description="Browser automation and web scraping",
                command="npx",
                args=["-q", "@modelcontextprotocol/server-puppeteer"],
                env={"UV_PYTHON": "3.12", **os.environ}
            ),
            
            "sqlite": MCPServerConfig(
                name="sqlite",
                description="Database interaction and business intelligence capabilities",
                command="npx",
                args=["-q", "@modelcontextprotocol/server-sqlite", "--db-path", "/tmp/kaching.db"],
                env={"UV_PYTHON": "3.12", **os.environ}
            ),
            
            # Git integration
            "git": MCPServerConfig(
                name="git",
                description="Tools to read, search, and manipulate Git repositories",
                command="uvx",
                args=["--quiet", "mcp-server-git", "--repository", "."],
                env={"UV_PYTHON": "3.12", **os.environ}
            ),
            
            # Community servers (these may need different installation)
            "everything": MCPServerConfig(
                name="everything",
                description="Reference / test server with prompts, resources, and tools",
                command="npx",
                args=["-q", "@modelcontextprotocol/server-everything"],
                env={"UV_PYTHON": "3.12", **os.environ},
                enabled=False  # Enable for testing
            )
        }
    
    @asynccontextmanager
    async def get_tools_for_servers(self, server_names: List[str]):
        """
        Get tools from specified MCP servers using context manager.
        
        Args:
            server_names: List of server names to load tools from
            
        Yields:
            Dict[str, ToolCollection]: Mapping of server names to their tool collections
        """
        tool_collections_map: Dict[str, ToolCollection] = {}
        # Keep track of context managers that need exiting for Stdio servers
        entered_stdio_cms = [] 
        
        try:
            for server_name in server_names:
                if server_name not in self.server_configs:
                    logger.warning(f"Unknown MCP server: {server_name}")
                    continue
                    
                config = self.server_configs[server_name]
                
                if not config.enabled:
                    logger.info(f"MCP server {server_name} is disabled, skipping")
                    continue
                
                logger.info(f"Loading MCP server: {server_name}")
                
                server_parameters = StdioServerParameters(
                    command=config.command,
                    args=config.args,
                    env=config.env or {"UV_PYTHON": "3.12", **os.environ}
                )
                
                try:
                    # ToolCollection.from_mcp for StdioServerParameters returns a sync context manager
                    # as per smolagents documentation.
                    # We need to enter it to get the actual ToolCollection object.
                    
                    # Remove temporary debugging from previous step
                    # **** ORIGINAL CODE TO BE MODIFIED ****
                    # tool_collection_maybe_cm = ToolCollection.from_mcp(
                    #     server_parameters, 
                    #     trust_remote_code=True
                    # )
                    # if hasattr(tool_collection_maybe_cm, '__enter__') and hasattr(tool_collection_maybe_cm, '__exit__'):
                    #     logger.debug(f"Entering context manager for Stdio server: {server_name}")
                    #     # This is a synchronous __enter__ as per smolagents example for Stdio
                    #     actual_tool_collection = tool_collection_maybe_cm.__enter__()
                    #     entered_stdio_cms.append(tool_collection_maybe_cm) # Store CM to exit later
                    # else:
                    #     actual_tool_collection = tool_collection_maybe_cm # Assume it's already a ToolCollection

                    # Simpler approach based on the type check from earlier:
                    # The issue was that from_mcp was returning the _GeneratorContextManager instance directly.
                    # The smolagents example `with ToolCollection.from_mcp(...) as tc:` means `from_mcp` IS the CM.
                    
                    cm = ToolCollection.from_mcp(
                        server_parameters,
                        trust_remote_code=True
                    )
                    # cm is a synchronous context manager. We enter it.
                    # The object returned by __enter__ is the ToolCollection instance.
                    tool_collection_instance = cm.__enter__()
                    entered_stdio_cms.append(cm) # Keep track of the cm to exit it
                    
                    tool_collections_map[server_name] = tool_collection_instance
                    logger.success(f"Successfully loaded and entered MCP server: {server_name}. Type: {type(tool_collection_instance)}")
                    
                    if not hasattr(tool_collection_instance, 'tools'):
                        logger.warning(f"Loaded ToolCollection for {server_name} is missing 'tools' attribute. Dir: {dir(tool_collection_instance)}")
                    else:
                        logger.debug(f"ToolCollection for {server_name} has tools: {len(tool_collection_instance.tools) if tool_collection_instance.tools is not None else 'None'}")

                except Exception as e:
                    logger.error(f"Failed to load MCP server {server_name}: {e}")
                    # Ensure any partially entered CM for this server is handled if error occurs after __enter__
                    # This specific case is tricky; for now, if __enter__ fails, it won't be in entered_stdio_cms.
                    # If it succeeds but a later step fails before yield, it will be cleaned up in finally.
                    continue
            
            yield tool_collections_map
            
        finally:
            # Cleanup tool collections
            for server_name, collection_instance in tool_collections_map.items():
                # The 'collection_instance' is what was yielded.
                # We need to call close() on it if it exists, which is typical for ToolCollection.
                # The actual stdio server process is managed by the context manager stored in `entered_stdio_cms`.
                try:
                    if hasattr(collection_instance, 'close') and asyncio.iscoroutinefunction(collection_instance.close):
                        await collection_instance.close()
                        logger.info(f"Async closed ToolCollection instance for: {server_name}")
                    elif hasattr(collection_instance, 'close'):
                        collection_instance.close()
                        logger.info(f"Sync closed ToolCollection instance for: {server_name}")
                except Exception as e:
                    logger.error(f"Error closing ToolCollection instance for {server_name}: {e}")

            # Now exit all the Stdio context managers we entered
            for cm in entered_stdio_cms:
                try:
                    cm.__exit__(None, None, None) # Synchronous exit
                    logger.info(f"Exited Stdio context manager for a server.")
                except Exception as e:
                    logger.error(f"Error exiting Stdio context manager: {e}")
    
    def get_search_tools(self):
        """Get all available search and research tools"""
        search_servers = ["brave_search", "fetch"]
        return self.get_tools_for_servers(search_servers)
    
    def get_content_tools(self):
        """Get content creation and processing tools"""
        content_servers = ["fetch", "puppeteer", "filesystem"]
        return self.get_tools_for_servers(content_servers)
    
    def get_development_tools(self):
        """Get development and code-related tools"""
        dev_servers = ["git", "github", "filesystem"]
        return self.get_tools_for_servers(dev_servers)
    
    def get_data_tools(self):
        """Get data storage and analysis tools"""
        data_servers = ["sqlite", "memory"]
        return self.get_tools_for_servers(data_servers)
    
    def get_all_enabled_tools(self):
        """Get all enabled MCP servers"""
        enabled_servers = [
            name for name, config in self.server_configs.items() 
            if config.enabled
        ]
        return self.get_tools_for_servers(enabled_servers)
    
    def enable_server(self, server_name: str):
        """Enable a specific MCP server"""
        if server_name in self.server_configs:
            self.server_configs[server_name].enabled = True
            logger.info(f"Enabled MCP server: {server_name}")
        else:
            logger.error(f"Unknown MCP server: {server_name}")
    
    def disable_server(self, server_name: str):
        """Disable a specific MCP server"""
        if server_name in self.server_configs:
            self.server_configs[server_name].enabled = False
            logger.info(f"Disabled MCP server: {server_name}")
        else:
            logger.error(f"Unknown MCP server: {server_name}")
    
    def list_available_servers(self) -> Dict[str, Dict[str, Any]]:
        """List all available MCP servers and their status"""
        return {
            name: {
                "description": config.description,
                "enabled": config.enabled,
                "command": f"{config.command} {' '.join(config.args)}"
            }
            for name, config in self.server_configs.items()
        }
    
    def add_custom_server(self, config: MCPServerConfig):
        """Add a custom MCP server configuration"""
        self.server_configs[config.name] = config
        logger.info(f"Added custom MCP server: {config.name}")


# Example usage functions for the KaChing agents

async def get_research_tools():
    """Convenience function to get research tools for KaChing agents"""
    manager = MCPToolManager()
    async with manager.get_search_tools() as tools:
        return tools

async def get_content_creation_tools():
    """Convenience function to get content creation tools for KaChing agents"""
    manager = MCPToolManager()
    async with manager.get_content_tools() as tools:
        return tools

async def get_publishing_tools():
    """Convenience function to get publishing tools for KaChing agents"""
    manager = MCPToolManager()
    # Use available tools for publishing (filesystem, memory for now)
    async with manager.get_data_tools() as tools:
        return tools


# Configuration helper for environment setup
def setup_mcp_environment():
    """
    Setup environment variables and configurations for MCP servers.
    
    This function should be called during KaChing initialization to ensure
    all required API keys and configurations are available.
    """
    required_env_vars = {
        "BRAVE_API_KEY": "Required for Brave Search MCP server",
        "TAVILY_API_KEY": "Required for Tavily Search MCP server", 
        "EXA_API_KEY": "Required for Exa Search MCP server",
        "FIRECRAWL_API_KEY": "Required for Firecrawl MCP server",
        "WORDPRESS_URL": "WordPress site URL for publishing",
        "WORDPRESS_USERNAME": "WordPress username",
        "WORDPRESS_PASSWORD": "WordPress application password",
        "GOOGLE_SHEETS_CREDENTIALS": "Google Sheets API credentials file path"
    }
    
    missing_vars = []
    for var, description in required_env_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var}: {description}")
    
    if missing_vars:
        logger.warning("Missing environment variables for MCP servers:")
        for var in missing_vars:
            logger.warning(f"  - {var}")
        logger.info("Some MCP servers may not function without these variables")
    
    return len(missing_vars) == 0 