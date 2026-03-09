"""
Task Fingerprint Generator — identifies tasks to detect duplicates.

Fingerprint is generated from:
  - scene
  - normalized user intent
  - task name
  - target object
  - key tools

Same task → same fingerprint, enabling duplicate detection and reuse.
"""

import hashlib
import re
from typing import List, Optional


STOP_WORDS = {
    "a", "an", "the", "my", "this", "that", "is", "are", "was", "were",
    "be", "been", "do", "does", "did", "have", "has", "had", "will",
    "would", "could", "should", "can", "may", "might", "shall",
    "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "it", "its", "i", "me", "we", "our", "you", "your", "he", "she",
    "and", "or", "but", "not", "so", "if", "then", "than", "very",
    "just", "also", "please", "now", "here", "there",
}

INTENT_VERBS = {
    "deploy": "deploy",
    "deploying": "deploy",
    "deployed": "deploy",
    "deployment": "deploy",
    "build": "build",
    "building": "build",
    "built": "build",
    "test": "test",
    "testing": "test",
    "tested": "test",
    "fix": "fix",
    "fixing": "fix",
    "fixed": "fix",
    "debug": "debug",
    "debugging": "debug",
    "debugged": "debug",
    "create": "create",
    "creating": "create",
    "created": "create",
    "install": "install",
    "installing": "install",
    "installed": "install",
    "setup": "setup",
    "configure": "configure",
    "configuring": "configure",
    "configured": "configure",
    "run": "run",
    "running": "run",
    "update": "update",
    "updating": "update",
    "updated": "update",
    "refactor": "refactor",
    "refactoring": "refactor",
    "migrate": "migrate",
    "migrating": "migrate",
    "analyze": "analyze",
    "analyzing": "analyze",
    "search": "search",
    "searching": "search",
    "write": "write",
    "writing": "write",
    "implement": "implement",
    "implementing": "implement",
}


def normalize_intent(message: str) -> str:
    text = message.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    words = text.split()

    normalized = []
    for w in words:
        if w in STOP_WORDS:
            continue
        canonical = INTENT_VERBS.get(w, w)
        if canonical not in normalized:
            normalized.append(canonical)

    return " ".join(normalized[:8])


def generate_fingerprint(scene: str = "", intent: str = "",
                         task_name: str = "", target: str = "",
                         tools: List[str] = None) -> str:
    parts = [
        scene.lower().strip(),
        normalize_intent(intent) if intent else "",
        task_name.lower().strip(),
        target.lower().strip(),
    ]

    if tools:
        tool_str = "|".join(sorted(t.lower().strip() for t in tools))
        parts.append(tool_str)

    combined = "|".join(p for p in parts if p)

    if not combined:
        return ""

    hash_val = hashlib.sha256(combined.encode()).hexdigest()[:8]
    return f"task_fp_{hash_val}"


def fingerprint_from_event(event: dict, scene: str = "") -> str:
    content = event.get("content", "")
    tools = event.get("tools", [])
    task_id = event.get("task_id", "")

    return generate_fingerprint(
        scene=scene,
        intent=content,
        task_name=task_id,
        tools=tools,
    )
