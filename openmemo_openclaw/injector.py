"""
Context injector — formats memory context for prompt injection.

Supports two strategies:
  - system: inject into system prompt
  - user_prefix: prepend before user message

Also supports direct message-list injection for OpenClaw compatibility.
"""

import logging
from typing import List, Optional

logger = logging.getLogger("openmemo_openclaw")

SYSTEM_TEMPLATE = """Relevant memory:
{items}"""

USER_PREFIX_TEMPLATE = """[Memory Context]
{items}

"""


def _truncate_memories(memories: List[str], max_items: int = 5,
                       max_tokens: int = 200) -> List[str]:
    truncated = memories[:max_items]

    items = []
    total_tokens = 0
    for i, mem in enumerate(truncated, 1):
        token_estimate = len(mem.split())
        if total_tokens + token_estimate > max_tokens and items:
            break
        items.append(f"{i}. {mem}")
        total_tokens += token_estimate

    return items


def inject_context(memories: List[str], strategy: str = "system",
                   max_items: int = 5,
                   max_tokens: int = 200) -> Optional[str]:
    if not memories:
        return None

    items = _truncate_memories(memories, max_items, max_tokens)

    if not items:
        return None

    items_text = "\n".join(items)

    if strategy == "user_prefix":
        return USER_PREFIX_TEMPLATE.format(items=items_text)

    return SYSTEM_TEMPLATE.format(items=items_text)


def inject_into_messages(messages: List[dict], memories: List[str],
                         strategy: str = "system",
                         max_items: int = 5,
                         max_tokens: int = 200) -> List[dict]:
    if not memories:
        logger.debug("[openmemo] no memories to inject, skipping")
        return messages

    items = _truncate_memories(memories, max_items, max_tokens)
    if not items:
        return messages

    items_text = "\n".join(items)
    result = list(messages)

    if strategy == "system":
        injection = SYSTEM_TEMPLATE.format(items=items_text)

        has_system = False
        for i, msg in enumerate(result):
            if msg.get("role") == "system":
                result[i] = {
                    **msg,
                    "content": f"{msg['content']}\n\n{injection}",
                }
                has_system = True
                break

        if not has_system:
            result.insert(0, {"role": "system", "content": injection})

    elif strategy == "user_prefix":
        injection = USER_PREFIX_TEMPLATE.format(items=items_text)

        for i in range(len(result) - 1, -1, -1):
            if result[i].get("role") == "user":
                result[i] = {
                    **result[i],
                    "content": f"{injection}{result[i]['content']}",
                }
                break

    logger.info("[openmemo] injected %d memories into %s prompt", len(items), strategy)
    return result


def format_system_injection(memories: List[str],
                            max_items: int = 5,
                            max_tokens: int = 200) -> Optional[str]:
    return inject_context(memories, strategy="system",
                          max_items=max_items, max_tokens=max_tokens)


def format_user_prefix(memories: List[str],
                       max_items: int = 5,
                       max_tokens: int = 200) -> Optional[str]:
    return inject_context(memories, strategy="user_prefix",
                          max_items=max_items, max_tokens=max_tokens)


def build_prompt(original_prompt: str, memory_context: List[str],
                 strategy: str = "system",
                 max_items: int = 5,
                 max_tokens: int = 200) -> str:
    injection = inject_context(memory_context, strategy=strategy,
                               max_items=max_items, max_tokens=max_tokens)

    if not injection:
        return original_prompt

    if strategy == "user_prefix":
        return f"{injection}{original_prompt}"

    return f"{injection}\n\n{original_prompt}"
