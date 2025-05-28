"""
Configuration Manager for KaChing

Utility functions for managing KaChing configurations.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from ..config import KaChingConfig


class ConfigManager:
    """Utility class for managing KaChing configurations."""
    
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = workspace_path or Path("./workspace")
        self.config_dir = self.workspace_path / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def create_env_file(self, template: str = "development", force: bool = False) -> Path:
        """Create a .env file from a configuration template."""
        env_path = Path(".env")
        
        if env_path.exists() and not force:
            raise FileExistsError(f".env file already exists. Use force=True to overwrite.")
        
        # Load the template
        config = KaChingConfig.load_template(template)
        
        # Create .env content
        env_content = self._config_to_env(config)
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        return env_path
    
    def _config_to_env(self, config: KaChingConfig) -> str:
        """Convert a configuration to .env format."""
        lines = [
            "# KaChing Configuration",
            "# Generated from configuration template",
            "",
            "# Core Settings",
            f'KACHING_NICHE="{config.niche}"',
            f"KACHING_BUDGET_LIMIT={config.budget_limit}",
            f'KACHING_WORKSPACE="{config.workspace_path}"',
            "",
            "# Model Configuration",
            f"KACHING_MODEL_BACKEND={config.model_backend}",
            f'KACHING_MODEL_ID="{config.model_id}"',
            f"KACHING_MAX_TOKENS={config.max_tokens}",
            f"KACHING_TEMPERATURE={config.temperature}",
            f"KACHING_PLANNING_INTERVAL={config.planning_interval}",
            "",
            "# Business Settings",
            f"KACHING_TARGET_REVENUE={config.target_revenue}",
            f"KACHING_CONTENT_FREQUENCY={config.content_frequency}",
            f"KACHING_QUALITY_THRESHOLD={config.quality_threshold}",
            "",
            "# Safety Settings",
            f"KACHING_MAX_DAILY_SPEND={config.max_daily_spend}",
            f"KACHING_CONTENT_REVIEW={'true' if config.content_review_required else 'false'}",
            f"KACHING_AUTO_PUBLISH={'true' if config.auto_publish else 'false'}",
            "",
            "# WordPress Settings (fill in your values)",
            "WORDPRESS_URL=https://your-site.com",
            "WORDPRESS_USERNAME=your_username",
            "WORDPRESS_PASSWORD=your_app_password",
            "",
            "# Affiliate Settings (fill in your values)",
            "AMAZON_ASSOCIATE_ID=your_amazon_associate_id",
            "CJ_WEBSITE_ID=your_commission_junction_id",
            "SHAREASALE_AFFILIATE_ID=your_shareasale_id",
            "",
            "# API Keys (fill in your values)",
            "KEYWORD_API_KEY=your_keyword_research_api_key",
            "SERP_API_KEY=your_serp_api_key",
            "",
            "# MCP Server API Keys (fill in your values)",
            "BRAVE_API_KEY=your_brave_search_api_key",
            "TAVILY_API_KEY=your_tavily_api_key",
            "EXA_API_KEY=your_exa_api_key",
            "FIRECRAWL_API_KEY=your_firecrawl_api_key",
        ]
        
        # Add model-specific settings
        if config.model_backend == "mlx":
            lines.extend([
                "",
                "# MLX Settings",
                "MLX_TRUST_REMOTE_CODE=false",
            ])
        elif config.model_backend == "litellm":
            lines.extend([
                "",
                "# LiteLLM Settings",
                "LITELLM_PROVIDER=ollama",
                "LITELLM_BASE_URL=http://localhost:11434",
                "# LITELLM_API_KEY=your_api_key",
            ])
        elif config.model_backend == "openai":
            lines.extend([
                "",
                "# OpenAI Settings",
                "OPENAI_API_KEY=your_openai_api_key",
                "OPENAI_BASE_URL=https://api.openai.com/v1",
            ])
        
        return "\n".join(lines)
    
    def list_templates(self) -> list:
        """List available configuration templates."""
        return KaChingConfig.list_templates()
    
    def validate_current_config(self) -> Dict[str, Any]:
        """Validate the current configuration and return status."""
        try:
            config = KaChingConfig.from_env()
            config.validate()
            return {
                "valid": True,
                "config": config,
                "errors": []
            }
        except Exception as e:
            return {
                "valid": False,
                "config": None,
                "errors": [str(e)]
            }
    
    def setup_workspace(self, config: Optional[KaChingConfig] = None) -> None:
        """Set up the workspace directory structure."""
        if config is None:
            config = KaChingConfig.from_env()
        
        workspace = Path(config.workspace_path)
        
        # Create directory structure
        directories = [
            workspace / "content",
            workspace / "logs", 
            workspace / "schedule",
            workspace / "secrets",
            workspace / "config"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create initial schedule file
        schedule_file = workspace / "schedule" / "schedule.json"
        if not schedule_file.exists():
            with open(schedule_file, 'w') as f:
                f.write('[]')  # Empty schedule to start
        
        print(f"✅ Workspace set up at: {workspace}")
        print(f"   - Content directory: {workspace / 'content'}")
        print(f"   - Logs directory: {workspace / 'logs'}")
        print(f"   - Schedule file: {schedule_file}")
        print(f"   - Secrets directory: {workspace / 'secrets'}")


def main():
    """CLI interface for configuration management."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="KaChing Configuration Manager")
    parser.add_argument("command", choices=["list", "create-env", "validate", "setup-workspace"])
    parser.add_argument("--template", default="development", help="Configuration template to use")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing files")
    
    args = parser.parse_args()
    
    manager = ConfigManager()
    
    if args.command == "list":
        templates = manager.list_templates()
        print("Available configuration templates:")
        for template in templates:
            print(f"  - {template}")
    
    elif args.command == "create-env":
        try:
            env_path = manager.create_env_file(args.template, args.force)
            print(f"✅ Created .env file from '{args.template}' template: {env_path}")
            print("📝 Please edit the .env file to add your API keys and settings")
        except FileExistsError as e:
            print(f"❌ {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            sys.exit(1)
    
    elif args.command == "validate":
        result = manager.validate_current_config()
        if result["valid"]:
            config = result["config"]
            print("✅ Configuration is valid!")
            print(f"   - Niche: {config.niche}")
            print(f"   - Model: {config.get_model_info()}")
            print(f"   - Budget: ${config.budget_limit}")
            print(f"   - Workspace: {config.workspace_path}")
        else:
            print("❌ Configuration validation failed:")
            for error in result["errors"]:
                print(f"   - {error}")
            sys.exit(1)
    
    elif args.command == "setup-workspace":
        try:
            manager.setup_workspace()
        except Exception as e:
            print(f"❌ Error setting up workspace: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main() 