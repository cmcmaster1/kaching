"""
KaChing: Autonomous Affiliate Content Agent

A multi-agent system using Smolagents to generate affiliate content
and manage an autonomous internet business.
"""

__version__ = "0.1.0"
__author__ = "KaChing Project"
__description__ = "Autonomous affiliate content agent using Smolagents"

from .orchestrator import KaChingOrchestrator
from .agents import ResearchAgent, ContentAgent  # , PublishingAgent, MonitorAgent

__all__ = [
    "KaChingOrchestrator",
    "ResearchAgent", 
    "ContentAgent",
    # "PublishingAgent",
    # "MonitorAgent",
] 