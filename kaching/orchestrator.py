"""
KaChing Orchestrator Agent

Main orchestrator that coordinates all specialized agents using Smolagents.
Implements the Plan → Delegate → Monitor → Reflect loop.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime

from smolagents import CodeAgent
from loguru import logger

from .config import KaChingConfig
from .agents import ResearchAgent, ContentAgent  # , PublishingAgent, MonitorAgent
from .utils.scheduler import SchedulerManager


class KaChingOrchestrator:
    """
    Main orchestrator agent that coordinates specialized agents.
    
    Uses Smolagents CodeAgent with planning_interval for regular reflection.
    Manages task delegation, progress tracking, and error handling.
    """
    
    def __init__(self, config: Optional[KaChingConfig] = None):
        self.config = config or KaChingConfig()
        self.workspace_path = Path(self.config.workspace_path)
        self.scheduler = SchedulerManager(self.workspace_path / "schedule")
        
        # Set up logging
        self._setup_logging()
        
        # Initialize model
        self.model = self._initialize_model()
        
        # Initialize specialized agents
        self.agents = self._initialize_agents()
        
        # Initialize orchestrator agent
        self.orchestrator = self._initialize_orchestrator()
        
        logger.info("KaChing Orchestrator initialized successfully")
    
    def _setup_logging(self) -> None:
        """Configure logging for the orchestrator."""
        log_path = self.workspace_path / "logs"
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Configure loguru
        logger.remove()  # Remove default handler
        logger.add(
            sys.stderr,
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        logger.add(
            log_path / "orchestrator_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="30 days",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )
    
    def _initialize_model(self) -> Union[Any]:
        """Initialize the model based on configuration."""
        try:
            model_backend = self.config.model_backend.lower()
            model_id = self.config.model_id
            
            logger.info(f"Initializing {model_backend} model: {model_id}")
            
            if model_backend == "mlx":
                from smolagents import MLXModel
                model = MLXModel(
                    model_id=model_id,
                    max_tokens=self.config.max_tokens,
                    **self.config.model_kwargs
                )
                
            elif model_backend == "litellm":
                from smolagents import LiteLLMModel
                model = LiteLLMModel(
                    model_id=model_id,
                    **self.config.model_kwargs
                )
                
            elif model_backend == "vllm":
                from smolagents import VLLMModel
                model = VLLMModel(
                    model_id=model_id,
                    **self.config.model_kwargs
                )
                
            elif model_backend == "transformers":
                from smolagents import TransformersModel
                model = TransformersModel(
                    model_id=model_id,
                    **self.config.model_kwargs
                )
                
            elif model_backend == "inference_client":
                from smolagents import InferenceClientModel
                model = InferenceClientModel(
                    model_id=model_id,
                    **self.config.model_kwargs
                )
                
            elif model_backend == "openai":
                from smolagents import OpenAIServerModel
                model = OpenAIServerModel(
                    model_id=model_id,
                    **self.config.model_kwargs
                )
                
            elif model_backend == "azure_openai":
                from smolagents import AzureOpenAIServerModel
                model = AzureOpenAIServerModel(
                    model_id=model_id,
                    **self.config.model_kwargs
                )
                
            elif model_backend == "bedrock":
                from smolagents import AmazonBedrockServerModel
                model = AmazonBedrockServerModel(
                    model_id=model_id,
                    **self.config.model_kwargs
                )
                
            else:
                raise ValueError(f"Unsupported model backend: {model_backend}")
            
            logger.info(f"Successfully initialized {model_backend} model: {model_id}")
            return model
            
        except ImportError as e:
            logger.error(f"Failed to import {model_backend} model. Install required dependencies: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize {model_backend} model: {e}")
            raise
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all specialized agents."""
        agents = {}
        
        try:
            agents["research"] = ResearchAgent(self.config)
            agents["content"] = ContentAgent(self.config)
            
            # TODO: Implement remaining agents
            # agents["publishing"] = PublishingAgent(self.config)
            # agents["monitor"] = MonitorAgent(self.config)
            
            logger.info("Available specialized agents initialized successfully")
            return agents
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    def _initialize_orchestrator(self) -> CodeAgent:
        """Initialize the main orchestrator CodeAgent."""
        system_prompt = self._create_system_prompt()
        
        # Create managed agents dictionary for Smolagents
        managed_agents = {
            name: agent.get_agent_description() 
            for name, agent in self.agents.items()
        }
        
        orchestrator = CodeAgent(
            tools=self._get_orchestrator_tools(),
            model=self.model,
            planning_interval=self.config.planning_interval,
            managed_agents=managed_agents,
            system_prompt=system_prompt
        )
        
        logger.info("Orchestrator CodeAgent initialized")
        return orchestrator
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the orchestrator."""
        return f"""
You are "KaChing-Orchestrator", an autonomous affiliate content business manager.

MISSION: Build and operate a profitable affiliate content site targeting "{self.config.niche}" 
with a goal of >AU $5,000/year revenue while maintaining full legal compliance.

CORE PRINCIPLES:
1. Profit-focused: Every action should contribute to long-term revenue growth
2. Legal compliance: Follow all affiliate network rules, copyright law, and consumer protection
3. Quality first: Publish only high-quality, helpful content
4. Capital preservation: Stay within budget limits (AU ${self.config.budget_limit})
5. Transparency: Log all decisions and actions for review

AVAILABLE TEAM MEMBERS:
{{{{managed_agents_description}}}}

AVAILABLE TOOLS:
{{{{tool_descriptions}}}}

YOUR WORKFLOW:
1. PLAN: Analyze current situation and set priorities
2. DELEGATE: Assign tasks to appropriate team members
3. MONITOR: Track progress and quality
4. REFLECT: Learn from results and adjust strategy

PAUSE MECHANISM: If workspace/schedule/schedule.json is empty, enter idle mode.

BUDGET TRACKING: Current spend: AU $0 / AU ${self.config.budget_limit}

MODEL INFO: Running on {self.config.model_backend} with {self.config.model_id}

Remember: You're building a real business. Every decision matters for long-term success.
"""
    
    def _get_orchestrator_tools(self) -> list:
        """Get tools available to the orchestrator."""
        from .tools import (
            SchedulerTool,
            BudgetTrackerTool,
            LogAnalyzerTool,
            StatusReporterTool
        )
        
        return [
            SchedulerTool(self.scheduler),
            BudgetTrackerTool(self.config),
            LogAnalyzerTool(self.workspace_path / "logs"),
            StatusReporterTool(self.workspace_path)
        ]
    
    def is_paused(self) -> bool:
        """Check if the system should be paused."""
        return self.scheduler.is_paused()
    
    def run_cycle(self) -> Dict[str, Any]:
        """Run one complete orchestration cycle."""
        if self.is_paused():
            logger.info("System is paused - schedule.json is empty")
            return {"status": "paused", "message": "System paused via empty schedule"}
        
        try:
            logger.info("Starting orchestration cycle")
            
            # Get current status and next tasks
            status_prompt = self._create_status_prompt()
            
            # Run the orchestrator
            result = self.orchestrator.run(status_prompt)
            
            # Log the cycle completion
            cycle_result = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "result": result,
                "next_cycle": self.scheduler.get_next_scheduled_time(),
                "model_backend": self.config.model_backend,
                "model_id": self.config.model_id
            }
            
            self._log_cycle_result(cycle_result)
            logger.info("Orchestration cycle completed successfully")
            
            return cycle_result
            
        except Exception as e:
            logger.error(f"Orchestration cycle failed: {e}")
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
                "next_cycle": self.scheduler.get_next_scheduled_time(),
                "model_backend": self.config.model_backend,
                "model_id": self.config.model_id
            }
            self._log_cycle_result(error_result)
            return error_result
    
    def _create_status_prompt(self) -> str:
        """Create a status prompt for the current cycle."""
        # Get recent logs and current schedule
        recent_activity = self._get_recent_activity()
        current_schedule = self.scheduler.get_current_schedule()
        
        return f"""
CYCLE STATUS UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RECENT ACTIVITY:
{recent_activity}

CURRENT SCHEDULE:
{json.dumps(current_schedule, indent=2)}

TASK: Review the current situation and determine the next actions needed to advance our affiliate business goals. 

Consider:
- What tasks are pending or overdue?
- What new opportunities should we pursue?
- Are there any issues that need immediate attention?
- How can we optimize our current performance?

Delegate appropriate tasks to your team members and update the schedule accordingly.
"""
    
    def _get_recent_activity(self) -> str:
        """Get summary of recent activity from logs."""
        try:
            log_files = list((self.workspace_path / "logs").glob("*.log"))
            if not log_files:
                return "No recent activity logged."
            
            # Get the most recent log file
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            # Read last 20 lines
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-20:] if len(lines) > 20 else lines
                return "".join(recent_lines)
                
        except Exception as e:
            logger.warning(f"Could not read recent activity: {e}")
            return "Could not retrieve recent activity."
    
    def _log_cycle_result(self, result: Dict[str, Any]) -> None:
        """Log the cycle result to file."""
        try:
            log_file = self.workspace_path / "logs" / "cycle_results.jsonl"
            with open(log_file, 'a') as f:
                f.write(json.dumps(result) + "\n")
        except Exception as e:
            logger.warning(f"Could not log cycle result: {e}")
    
    def start_autonomous_operation(self, cycle_interval_minutes: int = 30) -> None:
        """Start autonomous operation with regular cycles."""
        logger.info(f"Starting autonomous operation with {cycle_interval_minutes} minute intervals")
        logger.info(f"Using {self.config.model_backend} model: {self.config.model_id}")
        
        import time
        
        while True:
            try:
                cycle_result = self.run_cycle()
                
                if cycle_result["status"] == "paused":
                    logger.info("System paused, waiting...")
                    time.sleep(600)  # Wait 10 minutes when paused
                else:
                    logger.info(f"Cycle completed: {cycle_result['status']}")
                    time.sleep(cycle_interval_minutes * 60)
                    
            except KeyboardInterrupt:
                logger.info("Autonomous operation stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in autonomous operation: {e}")
                time.sleep(300)  # Wait 5 minutes on error


def main():
    """Main entry point for the orchestrator."""
    try:
        config = KaChingConfig.from_env()
        orchestrator = KaChingOrchestrator(config)
        
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--autonomous":
            orchestrator.start_autonomous_operation()
        else:
            # Run single cycle
            result = orchestrator.run_cycle()
            print(json.dumps(result, indent=2))
            
    except Exception as e:
        logger.error(f"Failed to start orchestrator: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 