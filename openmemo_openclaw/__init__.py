"""
OpenMemo × OpenClaw Adapter

Cognitive Memory Backend for OpenClaw Agents.
Provides long-term memory, scene-aware recall, recency-aware ranking,
conflict suppression, and decision reconstruction.
"""

from openmemo_openclaw.adapter import OpenMemoAdapter
from openmemo_openclaw.plugin import OpenClawMemoryPlugin
from openmemo_openclaw.config import AdapterConfig

__version__ = "0.1.0"
__all__ = ["OpenMemoAdapter", "OpenClawMemoryPlugin", "AdapterConfig"]
