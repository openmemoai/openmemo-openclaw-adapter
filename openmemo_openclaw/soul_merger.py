"""
Soul Merger — merges original soul context with OpenMemo Memory Rules.

Merge order (later = higher effective priority in LLM attention):
  1. system_prompt (original)
  2. soul.md content
  3. openmemo_memory_rules
  4. runtime memory injection

This module handles steps 1-3. Step 4 is done by the injector.
"""

import logging
from typing import List, Optional

logger = logging.getLogger("openmemo_openclaw")

RULES_SECTION_MARKER = "<!-- openmemo-memory-rules -->"


def merge_soul(system_prompt: str, memory_rules: str) -> str:
    if not memory_rules:
        return system_prompt

    if RULES_SECTION_MARKER in system_prompt:
        start = system_prompt.index(RULES_SECTION_MARKER)
        end_marker = system_prompt.find(RULES_SECTION_MARKER, start + len(RULES_SECTION_MARKER))
        if end_marker > start:
            before = system_prompt[:start]
            after = system_prompt[end_marker + len(RULES_SECTION_MARKER):]
            system_prompt = before.rstrip() + after.lstrip("\n")

    merged = system_prompt.rstrip()
    merged += "\n\n"
    merged += RULES_SECTION_MARKER + "\n"
    merged += memory_rules.strip()
    merged += "\n" + RULES_SECTION_MARKER

    return merged


def merge_into_messages(messages: List[dict], memory_rules: str) -> List[dict]:
    if not memory_rules:
        return messages

    result = list(messages)

    for i, msg in enumerate(result):
        if msg.get("role") == "system":
            result[i] = {
                **msg,
                "content": merge_soul(msg["content"], memory_rules),
            }
            return result

    result.insert(0, {
        "role": "system",
        "content": merge_soul("", memory_rules),
    })
    return result


def extract_user_rules(system_prompt: str) -> Optional[str]:
    lower = system_prompt.lower()
    keywords = ["memory rule", "memory contract", "memory policy",
                "use memory", "prefer memory", "check memory"]
    for kw in keywords:
        if kw in lower:
            return kw
    return None
