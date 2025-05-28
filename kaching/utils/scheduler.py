"""
KaChing Scheduler Manager

Manages the scheduling system and pause mechanism for the KaChing autonomous system.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from loguru import logger


@dataclass
class ScheduledTask:
    """Represents a scheduled task."""
    id: str
    agent: str
    action: str
    parameters: Dict[str, Any]
    scheduled_time: str
    priority: int = 5  # 1-10, lower is higher priority
    status: str = "pending"  # pending, running, completed, failed
    created_at: str = ""
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class SchedulerManager:
    """
    Manages the scheduling system for KaChing.
    
    Handles the pause mechanism via schedule.json file and manages task queues.
    """
    
    def __init__(self, schedule_dir: Path):
        self.schedule_dir = Path(schedule_dir)
        self.schedule_file = self.schedule_dir / "schedule.json"
        self.history_file = self.schedule_dir / "schedule_history.jsonl"
        
        # Ensure directory exists
        self.schedule_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize empty schedule if it doesn't exist
        if not self.schedule_file.exists():
            self._save_schedule([])
    
    def is_paused(self) -> bool:
        """Check if the system is paused (empty schedule file)."""
        try:
            schedule = self._load_schedule()
            return len(schedule) == 0
        except Exception as e:
            logger.warning(f"Error checking pause status: {e}")
            return True  # Default to paused on error
    
    def pause_system(self) -> None:
        """Pause the system by clearing the schedule."""
        logger.info("Pausing system - clearing schedule")
        self._save_schedule([])
    
    def resume_system(self, initial_tasks: Optional[List[ScheduledTask]] = None) -> None:
        """Resume the system with optional initial tasks."""
        if initial_tasks is None:
            initial_tasks = self._create_default_startup_tasks()
        
        logger.info(f"Resuming system with {len(initial_tasks)} initial tasks")
        self._save_schedule([asdict(task) for task in initial_tasks])
    
    def add_task(self, task: ScheduledTask) -> None:
        """Add a new task to the schedule."""
        schedule = self._load_schedule()
        schedule.append(asdict(task))
        
        # Sort by priority (lower number = higher priority) then by scheduled time
        schedule.sort(key=lambda x: (x.get('priority', 5), x.get('scheduled_time', '')))
        
        self._save_schedule(schedule)
        logger.info(f"Added task {task.id} for agent {task.agent}")
    
    def get_next_task(self, agent: Optional[str] = None) -> Optional[ScheduledTask]:
        """Get the next pending task, optionally filtered by agent."""
        schedule = self._load_schedule()
        
        for task_dict in schedule:
            if task_dict.get('status') != 'pending':
                continue
            
            if agent and task_dict.get('agent') != agent:
                continue
            
            # Check if task is due
            scheduled_time = datetime.fromisoformat(task_dict['scheduled_time'])
            if scheduled_time <= datetime.now():
                return ScheduledTask(**task_dict)
        
        return None
    
    def update_task_status(self, task_id: str, status: str, error_message: Optional[str] = None) -> None:
        """Update the status of a task."""
        schedule = self._load_schedule()
        
        for task_dict in schedule:
            if task_dict.get('id') == task_id:
                task_dict['status'] = status
                if status in ['completed', 'failed']:
                    task_dict['completed_at'] = datetime.now().isoformat()
                if error_message:
                    task_dict['error_message'] = error_message
                break
        
        self._save_schedule(schedule)
        
        # Log to history
        self._log_task_update(task_id, status, error_message)
    
    def get_current_schedule(self) -> List[Dict[str, Any]]:
        """Get the current schedule."""
        return self._load_schedule()
    
    def get_pending_tasks(self, agent: Optional[str] = None) -> List[ScheduledTask]:
        """Get all pending tasks, optionally filtered by agent."""
        schedule = self._load_schedule()
        tasks = []
        
        for task_dict in schedule:
            if task_dict.get('status') == 'pending':
                if agent is None or task_dict.get('agent') == agent:
                    tasks.append(ScheduledTask(**task_dict))
        
        return tasks
    
    def cleanup_completed_tasks(self, keep_recent_hours: int = 24) -> None:
        """Remove completed tasks older than specified hours."""
        schedule = self._load_schedule()
        cutoff_time = datetime.now() - timedelta(hours=keep_recent_hours)
        
        filtered_schedule = []
        for task_dict in schedule:
            if task_dict.get('status') in ['completed', 'failed']:
                completed_at = task_dict.get('completed_at')
                if completed_at:
                    completed_time = datetime.fromisoformat(completed_at)
                    if completed_time < cutoff_time:
                        continue  # Skip old completed tasks
            
            filtered_schedule.append(task_dict)
        
        if len(filtered_schedule) != len(schedule):
            logger.info(f"Cleaned up {len(schedule) - len(filtered_schedule)} old completed tasks")
            self._save_schedule(filtered_schedule)
    
    def get_next_scheduled_time(self) -> Optional[str]:
        """Get the next scheduled task time."""
        schedule = self._load_schedule()
        
        next_time = None
        for task_dict in schedule:
            if task_dict.get('status') == 'pending':
                scheduled_time = task_dict.get('scheduled_time')
                if scheduled_time:
                    if next_time is None or scheduled_time < next_time:
                        next_time = scheduled_time
        
        return next_time
    
    def schedule_recurring_task(self, base_task: ScheduledTask, interval_hours: int, count: int = 1) -> None:
        """Schedule a recurring task."""
        base_time = datetime.fromisoformat(base_task.scheduled_time)
        
        for i in range(count):
            task_time = base_time + timedelta(hours=interval_hours * i)
            task = ScheduledTask(
                id=f"{base_task.id}_{i+1}",
                agent=base_task.agent,
                action=base_task.action,
                parameters=base_task.parameters.copy(),
                scheduled_time=task_time.isoformat(),
                priority=base_task.priority
            )
            self.add_task(task)
    
    def _load_schedule(self) -> List[Dict[str, Any]]:
        """Load the schedule from file."""
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading schedule: {e}")
            return []
    
    def _save_schedule(self, schedule: List[Dict[str, Any]]) -> None:
        """Save the schedule to file."""
        try:
            with open(self.schedule_file, 'w') as f:
                json.dump(schedule, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving schedule: {e}")
    
    def _log_task_update(self, task_id: str, status: str, error_message: Optional[str] = None) -> None:
        """Log task updates to history file."""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "status": status,
                "error_message": error_message
            }
            
            with open(self.history_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.warning(f"Error logging task update: {e}")
    
    def _create_default_startup_tasks(self) -> List[ScheduledTask]:
        """Create default startup tasks when resuming the system."""
        now = datetime.now()
        
        tasks = [
            ScheduledTask(
                id="startup_research_keywords",
                agent="research",
                action="keyword_research",
                parameters={"niche": "arthritis-friendly kitchen tools", "count": 30},
                scheduled_time=now.isoformat(),
                priority=1
            ),
            ScheduledTask(
                id="startup_competitor_analysis",
                agent="research",
                action="competitor_analysis",
                parameters={"niche": "arthritis-friendly kitchen tools"},
                scheduled_time=(now + timedelta(minutes=30)).isoformat(),
                priority=2
            ),
            ScheduledTask(
                id="startup_content_planning",
                agent="content",
                action="create_content_calendar",
                parameters={"weeks": 4, "posts_per_week": 3},
                scheduled_time=(now + timedelta(hours=1)).isoformat(),
                priority=3
            ),
            ScheduledTask(
                id="startup_monitor_setup",
                agent="monitor",
                action="setup_monitoring",
                parameters={},
                scheduled_time=(now + timedelta(minutes=15)).isoformat(),
                priority=4
            )
        ]
        
        return tasks 