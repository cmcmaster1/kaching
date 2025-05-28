"""
KaChing Configuration Management

Centralized configuration for the KaChing autonomous affiliate system.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class KaChingConfig:
    """Main configuration class for KaChing system."""
    
    # Core settings
    niche: str = "accessibility and comfort technology"
    budget_limit: float = 1000.0
    workspace_path: str = "./workspace"
    
    # Model settings
    model_backend: str = "mlx"  # mlx, litellm, vllm, transformers, inference_client, openai, azure_openai, bedrock
    model_id: str = "mlx-community/gemma-3-4b-it-qat-4bit"
    max_tokens: int = 2048
    temperature: float = 0.7
    planning_interval: int = 1
    model_kwargs: Dict[str, Any] = field(default_factory=dict)
    
    # Business settings
    target_revenue: float = 5000.0
    content_frequency: int = 21  # posts per week
    quality_threshold: float = 0.8
    
    # WordPress settings
    wordpress_url: Optional[str] = None
    wordpress_username: Optional[str] = None
    wordpress_password: Optional[str] = None
    
    # Affiliate settings
    amazon_associate_id: Optional[str] = None
    affiliate_networks: Dict[str, str] = field(default_factory=dict)
    
    # API keys
    keyword_api_key: Optional[str] = None
    serp_api_key: Optional[str] = None
    
    # Safety settings
    max_daily_spend: float = 10.0
    content_review_required: bool = True
    auto_publish: bool = False
    
    @classmethod
    def from_env(cls) -> "KaChingConfig":
        """Create configuration from environment variables."""
        # Parse model kwargs from environment
        model_kwargs = {}
        
        # Common model parameters
        if os.getenv("KACHING_TEMPERATURE"):
            model_kwargs["temperature"] = float(os.getenv("KACHING_TEMPERATURE"))
        if os.getenv("KACHING_MAX_TOKENS"):
            model_kwargs["max_tokens"] = int(os.getenv("KACHING_MAX_TOKENS"))
        
        # Backend-specific parameters
        model_backend = os.getenv("KACHING_MODEL_BACKEND", "mlx").lower()
        
        if model_backend == "mlx":
            # MLX-specific parameters
            if os.getenv("MLX_TRUST_REMOTE_CODE"):
                model_kwargs["trust_remote_code"] = os.getenv("MLX_TRUST_REMOTE_CODE").lower() == "true"
                
        elif model_backend == "litellm":
            # LiteLLM-specific parameters
            if os.getenv("LITELLM_PROVIDER"):
                model_kwargs["provider"] = os.getenv("LITELLM_PROVIDER")
            if os.getenv("LITELLM_API_KEY"):
                model_kwargs["api_key"] = os.getenv("LITELLM_API_KEY")
            if os.getenv("LITELLM_BASE_URL"):
                model_kwargs["base_url"] = os.getenv("LITELLM_BASE_URL")
                
        elif model_backend == "vllm":
            # vLLM-specific parameters
            if os.getenv("VLLM_MAX_MODEL_LEN"):
                model_kwargs["max_model_len"] = int(os.getenv("VLLM_MAX_MODEL_LEN"))
            if os.getenv("VLLM_GPU_MEMORY_UTILIZATION"):
                model_kwargs["gpu_memory_utilization"] = float(os.getenv("VLLM_GPU_MEMORY_UTILIZATION"))
                
        elif model_backend == "transformers":
            # Transformers-specific parameters
            if os.getenv("TRANSFORMERS_DEVICE_MAP"):
                model_kwargs["device_map"] = os.getenv("TRANSFORMERS_DEVICE_MAP")
            if os.getenv("TRANSFORMERS_TORCH_DTYPE"):
                model_kwargs["torch_dtype"] = os.getenv("TRANSFORMERS_TORCH_DTYPE")
            if os.getenv("TRANSFORMERS_TRUST_REMOTE_CODE"):
                model_kwargs["trust_remote_code"] = os.getenv("TRANSFORMERS_TRUST_REMOTE_CODE").lower() == "true"
                
        elif model_backend == "openai":
            # OpenAI-specific parameters
            if os.getenv("OPENAI_API_KEY"):
                model_kwargs["api_key"] = os.getenv("OPENAI_API_KEY")
            if os.getenv("OPENAI_BASE_URL"):
                model_kwargs["base_url"] = os.getenv("OPENAI_BASE_URL")
                
        elif model_backend == "azure_openai":
            # Azure OpenAI-specific parameters
            if os.getenv("AZURE_OPENAI_ENDPOINT"):
                model_kwargs["azure_endpoint"] = os.getenv("AZURE_OPENAI_ENDPOINT")
            if os.getenv("AZURE_OPENAI_API_KEY"):
                model_kwargs["api_key"] = os.getenv("AZURE_OPENAI_API_KEY")
            if os.getenv("OPENAI_API_VERSION"):
                model_kwargs["api_version"] = os.getenv("OPENAI_API_VERSION")
        
        return cls(
            # Core settings
            niche=os.getenv("KACHING_NICHE", "accessibility and comfort technology"),
            budget_limit=float(os.getenv("KACHING_BUDGET_LIMIT", "1000.0")),
            workspace_path=os.getenv("KACHING_WORKSPACE", "./workspace"),
            
            # Model settings
            model_backend=model_backend,
            model_id=os.getenv("KACHING_MODEL_ID", cls._get_default_model_id(model_backend)),
            max_tokens=int(os.getenv("KACHING_MAX_TOKENS", "2048")),
            temperature=float(os.getenv("KACHING_TEMPERATURE", "0.7")),
            planning_interval=int(os.getenv("KACHING_PLANNING_INTERVAL", "3")),
            model_kwargs=model_kwargs,
            
            # Business settings
            target_revenue=float(os.getenv("KACHING_TARGET_REVENUE", "5000.0")),
            content_frequency=int(os.getenv("KACHING_CONTENT_FREQUENCY", "3")),
            quality_threshold=float(os.getenv("KACHING_QUALITY_THRESHOLD", "0.8")),
            
            # WordPress settings
            wordpress_url=os.getenv("WORDPRESS_URL"),
            wordpress_username=os.getenv("WORDPRESS_USERNAME"),
            wordpress_password=os.getenv("WORDPRESS_PASSWORD"),
            
            # Affiliate settings
            amazon_associate_id=os.getenv("AMAZON_ASSOCIATE_ID"),
            affiliate_networks={
                "amazon": os.getenv("AMAZON_ASSOCIATE_ID", ""),
                "commission_junction": os.getenv("CJ_WEBSITE_ID", ""),
                "shareasale": os.getenv("SHAREASALE_AFFILIATE_ID", ""),
            },
            
            # API keys
            keyword_api_key=os.getenv("KEYWORD_API_KEY"),
            serp_api_key=os.getenv("SERP_API_KEY"),
            
            # Safety settings
            max_daily_spend=float(os.getenv("KACHING_MAX_DAILY_SPEND", "10.0")),
            content_review_required=os.getenv("KACHING_CONTENT_REVIEW", "true").lower() == "true",
            auto_publish=os.getenv("KACHING_AUTO_PUBLISH", "false").lower() == "true",
        )
    
    @staticmethod
    def _get_default_model_id(backend: str) -> str:
        """Get default model ID for each backend."""
        defaults = {
            "mlx": "mlx-community/gemma-3-4b-it-qat-4bit",
            "litellm": "ollama/phi3:mini",
            "vllm": "microsoft/Phi-3-mini-4k-instruct",
            "transformers": "microsoft/Phi-3-mini-4k-instruct",
            "inference_client": "Qwen/Qwen2.5-Coder-32B-Instruct",
            "openai": "gpt-4o-mini",
            "azure_openai": "gpt-4o-mini",
            "bedrock": "us.amazon.nova-pro-v1:0",
        }
        return defaults.get(backend, "microsoft/Phi-3-mini-4k-instruct")
    
    def validate(self) -> bool:
        """Validate the configuration."""
        errors = []
        
        # Check required paths
        workspace = Path(self.workspace_path)
        if not workspace.exists():
            try:
                workspace.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create workspace directory: {e}")
        
        # Check budget limits
        if self.budget_limit <= 0:
            errors.append("Budget limit must be positive")
        
        if self.max_daily_spend > self.budget_limit:
            errors.append("Daily spend limit cannot exceed total budget")
        
        # Check model settings
        if self.max_tokens <= 0:
            errors.append("Max tokens must be positive")
        
        if not 0 <= self.temperature <= 2:
            errors.append("Temperature must be between 0 and 2")
        
        # Validate model backend
        valid_backends = ["mlx", "litellm", "vllm", "transformers", "inference_client", "openai", "azure_openai", "bedrock"]
        if self.model_backend.lower() not in valid_backends:
            errors.append(f"Model backend must be one of: {', '.join(valid_backends)}")
        
        # Check business settings
        if self.content_frequency <= 0:
            errors.append("Content frequency must be positive")
        
        if not 0 <= self.quality_threshold <= 1:
            errors.append("Quality threshold must be between 0 and 1")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "niche": self.niche,
            "budget_limit": self.budget_limit,
            "workspace_path": self.workspace_path,
            "model_backend": self.model_backend,
            "model_id": self.model_id,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "planning_interval": self.planning_interval,
            "model_kwargs": self.model_kwargs,
            "target_revenue": self.target_revenue,
            "content_frequency": self.content_frequency,
            "quality_threshold": self.quality_threshold,
            "max_daily_spend": self.max_daily_spend,
            "content_review_required": self.content_review_required,
            "auto_publish": self.auto_publish,
        }
    
    def save_to_file(self, filepath: Path) -> None:
        """Save configuration to file."""
        import json
        
        config_dict = self.to_dict()
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: Path) -> "KaChingConfig":
        """Load configuration from file."""
        import json
        
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        
        return cls(**config_dict)
    
    def get_model_info(self) -> str:
        """Get a human-readable description of the model configuration."""
        return f"{self.model_backend.upper()} backend with {self.model_id}"
    
    def get_model(self):
        """Get the model instance based on configuration."""
        try:
            model_backend = self.model_backend.lower()
            model_id = self.model_id
            
            if model_backend == "mlx":
                from smolagents import MLXModel
                # Remove max_tokens from model_kwargs to avoid duplicate parameter
                mlx_kwargs = {k: v for k, v in self.model_kwargs.items() if k != 'max_tokens'}
                return MLXModel(
                    model_id=model_id,
                    max_tokens=self.max_tokens,
                    **mlx_kwargs
                )
                
            elif model_backend == "litellm":
                from smolagents import LiteLLMModel
                return LiteLLMModel(
                    model_id=model_id,
                    **self.model_kwargs
                )
                
            elif model_backend == "vllm":
                from smolagents import VLLMModel
                return VLLMModel(
                    model_id=model_id,
                    **self.model_kwargs
                )
                
            elif model_backend == "transformers":
                from smolagents import TransformersModel
                return TransformersModel(
                    model_id=model_id,
                    **self.model_kwargs
                )
                
            elif model_backend == "inference_client":
                from smolagents import InferenceClientModel
                return InferenceClientModel(
                    model_id=model_id,
                    **self.model_kwargs
                )
                
            elif model_backend == "openai":
                from smolagents import OpenAIServerModel
                return OpenAIServerModel(
                    model_id=model_id,
                    **self.model_kwargs
                )
                
            elif model_backend == "azure_openai":
                from smolagents import AzureOpenAIServerModel
                return AzureOpenAIServerModel(
                    model_id=model_id,
                    **self.model_kwargs
                )
                
            elif model_backend == "bedrock":
                from smolagents import AmazonBedrockServerModel
                return AmazonBedrockServerModel(
                    model_id=model_id,
                    **self.model_kwargs
                )
                
            else:
                raise ValueError(f"Unsupported model backend: {model_backend}")
                
        except ImportError as e:
            raise ImportError(f"Failed to import {model_backend} model. Install required dependencies: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize {model_backend} model: {e}")
    
    @classmethod
    def create_for_mac(cls, **kwargs) -> "KaChingConfig":
        """Create configuration optimized for Mac with Apple Silicon."""
        defaults = {
            "model_backend": "mlx",
            "model_id": "mlx-community/Phi-3-mini-4k-instruct-4bit",
            "model_kwargs": {"trust_remote_code": False}
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def create_for_pc_ollama(cls, **kwargs) -> "KaChingConfig":
        """Create configuration for PC with Ollama."""
        defaults = {
            "model_backend": "litellm",
            "model_id": "ollama/phi3:mini",
            "model_kwargs": {"provider": "ollama"}
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def create_for_pc_vllm(cls, **kwargs) -> "KaChingConfig":
        """Create configuration for PC with vLLM."""
        defaults = {
            "model_backend": "vllm",
            "model_id": "microsoft/Phi-3-mini-4k-instruct",
            "model_kwargs": {"gpu_memory_utilization": 0.8}
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def load_template(cls, template_name: str) -> "KaChingConfig":
        """Load configuration from a template file in the config directory."""
        from pathlib import Path
        import json
        
        # Look for templates in the templates subdirectory
        config_dir = Path(__file__).parent / "templates"
        template_path = config_dir / f"{template_name}.json"
        
        if not template_path.exists():
            available = [f.stem for f in config_dir.glob("*.json")]
            raise FileNotFoundError(
                f"Template '{template_name}' not found. Available templates: {', '.join(available)}"
            )
        
        with open(template_path, 'r') as f:
            config_dict = json.load(f)
        
        return cls(**config_dict)
    
    @classmethod
    def list_templates(cls) -> list:
        """List all available configuration templates."""
        from pathlib import Path
        
        config_dir = Path(__file__).parent / "templates"
        return [f.stem for f in config_dir.glob("*.json") if f.is_file()]
    
    @classmethod
    def create_development(cls, **kwargs) -> "KaChingConfig":
        """Create development configuration with safe defaults."""
        config = cls.load_template("development")
        # Override with any provided kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    @classmethod
    def create_production(cls, **kwargs) -> "KaChingConfig":
        """Create production configuration with full settings."""
        config = cls.load_template("production")
        # Override with any provided kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
    
    def save_as_template(self, template_name: str) -> None:
        """Save current configuration as a template."""
        from pathlib import Path
        
        config_dir = Path(__file__).parent / "templates"
        config_dir.mkdir(exist_ok=True)
        template_path = config_dir / f"{template_name}.json"
        
        self.save_to_file(template_path) 