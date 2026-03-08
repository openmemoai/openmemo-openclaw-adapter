"""
Event transformer — converts OpenClaw lifecycle events to MemoryEvent dicts.
"""

import time
import re
from typing import Optional


def transform_event(event_type: str, content: str,
                    tools: list = None, task_id: str = "",
                    session_id: str = "", metadata: dict = None) -> dict:
    cleaned = _clean_text(content)
    if not cleaned:
        return {}

    return {
        "type": event_type,
        "content": cleaned,
        "tools": tools or [],
        "task_id": task_id,
        "session_id": session_id,
        "timestamp": time.time(),
        "metadata": metadata or {},
    }


def transform_user_message(message: str, session_id: str = "",
                           task_id: str = "") -> dict:
    return transform_event(
        event_type="user_message",
        content=message,
        session_id=session_id,
        task_id=task_id,
    )


def transform_agent_response(response: str, tools: list = None,
                              session_id: str = "",
                              task_id: str = "") -> dict:
    return transform_event(
        event_type="agent_response",
        content=response,
        tools=tools,
        session_id=session_id,
        task_id=task_id,
    )


def transform_tool_call(tool_name: str, tool_output: str,
                        session_id: str = "",
                        task_id: str = "") -> dict:
    content = f"Tool {tool_name}: {tool_output}" if tool_output else f"Tool call: {tool_name}"
    return transform_event(
        event_type="tool_call",
        content=content,
        tools=[tool_name],
        session_id=session_id,
        task_id=task_id,
    )


def transform_task_complete(summary: str, tools: list = None,
                            session_id: str = "",
                            task_id: str = "") -> dict:
    return transform_event(
        event_type="task_complete",
        content=summary,
        tools=tools,
        session_id=session_id,
        task_id=task_id,
    )


def extract_memory_content(event: dict) -> Optional[str]:
    content = event.get("content", "")
    if not content:
        return None

    event_type = event.get("type", "")

    if event_type == "user_message":
        return f"User: {content}"
    elif event_type == "agent_response":
        tools = event.get("tools", [])
        if tools:
            return f"Agent: {content} (tools: {', '.join(tools)})"
        return f"Agent: {content}"
    elif event_type == "tool_call":
        return content
    elif event_type == "task_complete":
        return f"Task completed: {content}"

    return content


def infer_memory_type(event: dict) -> str:
    event_type = event.get("type", "")
    content = event.get("content", "").lower()

    if event_type == "task_complete":
        return "fact"

    if any(w in content for w in ["prefer", "like", "want", "choose"]):
        return "preference"
    if any(w in content for w in ["decided", "decision", "chose", "switched"]):
        return "decision"
    if any(w in content for w in ["must", "always", "never", "require", "constraint"]):
        return "constraint"

    return "observation"


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    if len(text) > 500:
        text = text[:500]
    return text
