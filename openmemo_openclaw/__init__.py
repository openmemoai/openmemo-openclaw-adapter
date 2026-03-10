"""
OpenMemo × OpenClaw Adapter v2.4.0

Automatic Cognitive Memory Infrastructure for OpenClaw Agents.
install → run → memory works automatically.
Now with built-in Memory Inspector Dashboard + Memory Rules System.
"""

from openmemo_openclaw.adapter import OpenMemoAdapter
from openmemo_openclaw.plugin import OpenClawMemoryPlugin
from openmemo_openclaw.config import AdapterConfig
from openmemo_openclaw.health import HealthCheckError
from openmemo_openclaw.pre_check import PreCheckResult
from openmemo_openclaw.fingerprint import generate_fingerprint
from openmemo_openclaw.task_extractor import TaskTracker
from openmemo_openclaw.version_check import VersionInfo, check_version
from openmemo_openclaw.inspector import InspectorServer
from openmemo_openclaw.memory_rules import MemoryRulesEngine, DEFAULT_MEMORY_RULES
from openmemo_openclaw.soul_merger import merge_soul, merge_into_messages

__version__ = "2.4.0"
__all__ = [
    "OpenMemoAdapter",
    "OpenClawMemoryPlugin",
    "AdapterConfig",
    "HealthCheckError",
    "PreCheckResult",
    "generate_fingerprint",
    "TaskTracker",
    "VersionInfo",
    "check_version",
    "InspectorServer",
    "MemoryRulesEngine",
    "DEFAULT_MEMORY_RULES",
    "merge_soul",
    "merge_into_messages",
]
