"""
OpenMemo × OpenClaw Adapter v2.0

Automatic Cognitive Memory Infrastructure for OpenClaw Agents.
install → run → memory works automatically.
"""

from openmemo_openclaw.adapter import OpenMemoAdapter
from openmemo_openclaw.plugin import OpenClawMemoryPlugin
from openmemo_openclaw.config import AdapterConfig
from openmemo_openclaw.health import HealthCheckError
from openmemo_openclaw.pre_check import PreCheckResult
from openmemo_openclaw.fingerprint import generate_fingerprint
from openmemo_openclaw.task_extractor import TaskTracker

__version__ = "2.0.0"
__all__ = [
    "OpenMemoAdapter",
    "OpenClawMemoryPlugin",
    "AdapterConfig",
    "HealthCheckError",
    "PreCheckResult",
    "generate_fingerprint",
    "TaskTracker",
]
