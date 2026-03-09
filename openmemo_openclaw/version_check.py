"""
Version check for OpenMemo Adapter.

Checks local vs remote versions at startup and provides upgrade recommendations.
"""

import json
import logging
import importlib.metadata
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("openmemo_openclaw")

REMOTE_VERSION_URL = "https://api.openmemo.ai/version"


@dataclass
class VersionInfo:
    local_core: Optional[str] = None
    local_adapter: Optional[str] = None
    latest_core: Optional[str] = None
    latest_adapter: Optional[str] = None
    update_available: bool = False


def get_local_versions() -> dict:
    core_version = None
    adapter_version = None

    try:
        core_version = importlib.metadata.version("openmemo")
    except importlib.metadata.PackageNotFoundError:
        try:
            import openmemo
            core_version = getattr(openmemo, "__version__", None)
        except ImportError:
            pass

    try:
        adapter_version = importlib.metadata.version("openmemo-openclaw")
    except importlib.metadata.PackageNotFoundError:
        try:
            import openmemo_openclaw
            adapter_version = getattr(openmemo_openclaw, "__version__", None)
        except ImportError:
            pass

    return {
        "core": core_version,
        "adapter": adapter_version,
    }


def _fetch_remote_versions() -> Optional[dict]:
    try:
        import urllib.request
        req = urllib.request.Request(
            REMOTE_VERSION_URL,
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def _is_newer(remote_ver: str, local_ver: str) -> bool:
    try:
        r = [int(x) for x in remote_ver.split(".")]
        l = [int(x) for x in local_ver.split(".")]
        return r > l
    except (ValueError, AttributeError):
        return False


def check_version() -> VersionInfo:
    local = get_local_versions()
    info = VersionInfo(
        local_core=local.get("core"),
        local_adapter=local.get("adapter"),
    )

    remote = _fetch_remote_versions()
    if not remote:
        return info

    info.latest_core = remote.get("latest_core")
    info.latest_adapter = remote.get("latest_adapter")

    if info.local_core and info.latest_core:
        if _is_newer(info.latest_core, info.local_core):
            info.update_available = True

    if info.local_adapter and info.latest_adapter:
        if _is_newer(info.latest_adapter, info.local_adapter):
            info.update_available = True

    return info


def log_version_status(info: VersionInfo = None):
    if info is None:
        info = check_version()

    logger.info("[openmemo] core=%s adapter=%s",
                info.local_core or "not installed",
                info.local_adapter or "not installed")

    if info.update_available:
        parts = []
        if info.latest_core and info.local_core and _is_newer(info.latest_core, info.local_core):
            parts.append(f"core {info.local_core} → {info.latest_core}")
        if info.latest_adapter and info.local_adapter and _is_newer(info.latest_adapter, info.local_adapter):
            parts.append(f"adapter {info.local_adapter} → {info.latest_adapter}")

        logger.info("[openmemo] Update available: %s", ", ".join(parts))
        logger.info("[openmemo] Run: pip install -U openmemo openmemo-openclaw")
