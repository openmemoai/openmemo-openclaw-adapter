"""
Task Memory Extractor — extracts structured task_execution memory from lifecycle events.

Converts raw agent events into structured task summaries for long-term memory.
"""

import time
import logging
from typing import List, Optional

logger = logging.getLogger("openmemo_openclaw")


def extract_task_memory(user_request: str, tool_trace: List[dict] = None,
                        task_result: str = "", scene: str = "",
                        fingerprint: str = "",
                        status: str = "success") -> dict:
    tools_used = []
    if tool_trace:
        for t in tool_trace:
            tool_name = t.get("tool_name", t.get("name", ""))
            if tool_name and tool_name not in tools_used:
                tools_used.append(tool_name)

    task_name = _infer_task_name(user_request, scene)
    summary = _build_summary(user_request, task_result, tools_used)

    return {
        "memory_type": "task_execution",
        "task_name": task_name,
        "scene": scene,
        "task_fingerprint": fingerprint,
        "status": status,
        "summary": summary,
        "tools_used": tools_used,
        "user_request": user_request,
        "timestamp": time.time(),
    }


def _infer_task_name(user_request: str, scene: str) -> str:
    text = user_request.lower().strip()

    action_words = [
        "deploy", "build", "test", "fix", "debug", "create",
        "install", "setup", "configure", "run", "update",
        "refactor", "migrate", "analyze", "search", "write", "implement",
    ]

    action = ""
    for word in action_words:
        if word in text:
            action = word
            break

    if not action:
        action = scene or "task"

    target_words = [w for w in text.split() if len(w) > 3 and w not in action_words]
    target = target_words[0] if target_words else ""

    if target:
        return f"{action}_{target}"
    return action


def _build_summary(user_request: str, task_result: str,
                   tools_used: List[str]) -> str:
    parts = []

    if task_result:
        parts.append(task_result.strip())
    elif user_request:
        parts.append(user_request.strip())

    if tools_used:
        parts.append(f"Tools: {', '.join(tools_used)}")

    summary = ". ".join(parts)
    if len(summary) > 300:
        summary = summary[:300]

    return summary


class TaskTracker:
    """
    Tracks tool calls and events within a single task lifecycle.
    Used by the adapter to accumulate context for task memory extraction.
    """

    def __init__(self):
        self._user_request = ""
        self._tool_trace: List[dict] = []
        self._scene = ""
        self._fingerprint = ""

    def set_user_request(self, message: str):
        if not self._user_request:
            self._user_request = message

    def add_tool_call(self, tool_name: str, output: str = ""):
        self._tool_trace.append({
            "tool_name": tool_name,
            "output": output[:200] if output else "",
            "timestamp": time.time(),
        })

    def set_scene(self, scene: str):
        self._scene = scene

    def set_fingerprint(self, fp: str):
        self._fingerprint = fp

    def extract(self, task_result: str = "",
                status: str = "success") -> dict:
        return extract_task_memory(
            user_request=self._user_request,
            tool_trace=self._tool_trace,
            task_result=task_result,
            scene=self._scene,
            fingerprint=self._fingerprint,
            status=status,
        )

    def reset(self):
        self._user_request = ""
        self._tool_trace = []
        self._scene = ""
        self._fingerprint = ""

    @property
    def fingerprint(self) -> str:
        return self._fingerprint

    @property
    def has_data(self) -> bool:
        return bool(self._user_request or self._tool_trace)
