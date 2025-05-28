# KaChing Agents Module
# Multi-agent system for autonomous affiliate content generation

from .research_agent import ResearchAgent, ResearchTask
from .content_agent import ContentAgent, ContentTask
from .publishing_agent import PublishingAgent, PublishingTask, AffiliateProduct
from .monitor_agent import MonitorAgent, PerformanceMetrics, QualityAlert, BudgetStatus

# Placeholder imports for agents that will be implemented
# from .monitor_agent import MonitorAgent

__all__ = [
    "ResearchAgent",
    "ResearchTask",
    "ContentAgent",
    "ContentTask",
    "PublishingAgent",
    "PublishingTask",
    "AffiliateProduct",
    "MonitorAgent",
    "PerformanceMetrics",
    "QualityAlert",
    "BudgetStatus"
] 