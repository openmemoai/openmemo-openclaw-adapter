"""
OpenMemo × OpenClaw Adapter

Cognitive Memory Backend for OpenClaw Agents.
Provides long-term memory, scene-aware recall, recency-aware ranking,
conflict suppression, and decision reconstruction.
"""

from openmemo_openclaw.adapter import OpenMemoAdapter
from openmemo_openclaw.plugin import OpenClawMemoryPlugin
from openmemo_openclaw.config import AdapterConfig
from openmemo_openclaw.health import HealthCheckError

__version__ = "0.1.1"
__all__ = [
    "OpenMemoAdapter",
    "OpenClawMemoryPlugin",
    "AdapterConfig",
    "HealthCheckError",
]
