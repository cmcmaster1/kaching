#!/usr/bin/env python3
"""
Configuration System Demo for KaChing

This script demonstrates how to use the KaChing configuration system:
1. Loading configuration templates
2. Creating environment files
3. Validating configurations
4. Using different configuration methods
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kaching.config import KaChingConfig
from kaching.utils import ConfigManager


def demo_configuration_system():
    """Demonstrate the KaChing configuration system"""
    
    print("🔧 KaChing Configuration System Demo")
    print("=" * 50)
    
    # 1. List available templates
    print("\n📋 Available Configuration Templates:")
    templates = KaChingConfig.list_templates()
    for template in templates:
        print(f"   - {template}")
    
    # 2. Load different templates
    print("\n🔄 Loading Configuration Templates:")
    
    try:
        # Development config
        dev_config = KaChingConfig.load_template("development")
        print(f"✅ Development config: {dev_config.get_model_info()}")
        print(f"   Budget: ${dev_config.budget_limit}, Content: {dev_config.content_frequency}/week")
        
        # Production config
        prod_config = KaChingConfig.load_template("production")
        print(f"✅ Production config: {prod_config.get_model_info()}")
        print(f"   Budget: ${prod_config.budget_limit}, Auto-publish: {prod_config.auto_publish}")
        
        # Mac-specific config
        mac_config = KaChingConfig.load_template("mac_local")
        print(f"✅ Mac config: {mac_config.get_model_info()}")
        
        # PC-specific config
        pc_config = KaChingConfig.load_template("pc_local")
        print(f"✅ PC config: {pc_config.get_model_info()}")
        
        # Cloud config
        cloud_config = KaChingConfig.load_template("cloud")
        print(f"✅ Cloud config: {cloud_config.get_model_info()}")
        
    except Exception as e:
        print(f"❌ Error loading templates: {e}")
    
    # 3. Demonstrate convenience methods
    print("\n🚀 Convenience Configuration Methods:")
    
    try:
        # Mac convenience method
        mac_conv = KaChingConfig.create_for_mac()
        print(f"✅ Mac convenience: {mac_conv.get_model_info()}")
        
        # PC Ollama convenience method
        pc_ollama = KaChingConfig.create_for_pc_ollama()
        print(f"✅ PC Ollama convenience: {pc_ollama.get_model_info()}")
        
        # Development convenience method
        dev_conv = KaChingConfig.create_development()
        print(f"✅ Development convenience: {dev_conv.get_model_info()}")
        
        # Production convenience method
        prod_conv = KaChingConfig.create_production()
        print(f"✅ Production convenience: {prod_conv.get_model_info()}")
        
    except Exception as e:
        print(f"❌ Error with convenience methods: {e}")
    
    # 4. Configuration Manager Demo
    print("\n🛠️ Configuration Manager Demo:")
    
    manager = ConfigManager()
    
    # List templates via manager
    print(f"📋 Templates via manager: {manager.list_templates()}")
    
    # Validate current configuration
    validation = manager.validate_current_config()
    if validation["valid"]:
        config = validation["config"]
        print(f"✅ Current config is valid: {config.get_model_info()}")
    else:
        print(f"❌ Current config validation failed: {validation['errors']}")
    
    # 5. Environment-based configuration
    print("\n🌍 Environment-based Configuration:")
    
    try:
        env_config = KaChingConfig.from_env()
        print(f"✅ Environment config: {env_config.get_model_info()}")
        print(f"   Niche: {env_config.niche}")
        print(f"   Workspace: {env_config.workspace_path}")
        print(f"   Budget: ${env_config.budget_limit}")
        
        # Validate environment config
        env_config.validate()
        print("✅ Environment configuration is valid!")
        
    except Exception as e:
        print(f"❌ Environment configuration issue: {e}")
        print("💡 Tip: Create a .env file with: uv run -m kaching.utils.config_manager create-env")
    
    # 6. Model instantiation demo
    print("\n🤖 Model Instantiation Demo:")
    
    try:
        # Try to get a model instance
        config = KaChingConfig.create_development()
        model = config.get_model()
        print(f"✅ Model instantiated: {type(model).__name__}")
        print(f"   Model ID: {config.model_id}")
        print(f"   Max tokens: {config.max_tokens}")
        
    except ImportError as e:
        print(f"⚠️ Model dependencies not available: {e}")
        print("💡 Install with: uv sync --extra mac (or --extra pc)")
    except Exception as e:
        print(f"❌ Model instantiation failed: {e}")
    
    # 7. Configuration saving demo
    print("\n💾 Configuration Saving Demo:")
    
    try:
        # Create a custom config
        custom_config = KaChingConfig.create_development(
            niche="custom test niche",
            budget_limit=500.0,
            max_tokens=1024
        )
        
        # Save as template
        custom_config.save_as_template("custom_demo")
        print("✅ Saved custom configuration as 'custom_demo' template")
        
        # Load it back
        loaded_custom = KaChingConfig.load_template("custom_demo")
        print(f"✅ Loaded custom config: {loaded_custom.niche}")
        
    except Exception as e:
        print(f"❌ Configuration saving failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Configuration System Demo Complete!")
    print("\n💡 Next Steps:")
    print("   1. Create a .env file: uv run -m kaching.utils.config_manager create-env")
    print("   2. Edit .env with your API keys and settings")
    print("   3. Validate: uv run -m kaching.utils.config_manager validate")
    print("   4. Set up workspace: uv run -m kaching.utils.config_manager setup-workspace")


if __name__ == "__main__":
    demo_configuration_system() 