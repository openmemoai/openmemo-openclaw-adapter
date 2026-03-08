"""
Memory ranker — reranks recall results with recency bias and conflict suppression.

Scoring formula:
    final_score = semantic_score * 0.6 + recency_score * 0.25 + scene_score * 0.15
"""

import time
from typing import List


SEMANTIC_WEIGHT = 0.6
RECENCY_WEIGHT = 0.25
SCENE_WEIGHT = 0.15

RECENCY_DECAY_DAYS = 30.0


def rank_memories(memories: List[dict], current_scene: str = "",
                  conflict_policy: str = "suppress") -> List[dict]:
    if not memories:
        return []

    scored = []
    for mem in memories:
        semantic = _normalize_score(mem.get("score", 0.0))
        recency = _recency_score(mem.get("timestamp", 0))
        scene = _scene_score(mem.get("scene", ""), current_scene)

        final = (semantic * SEMANTIC_WEIGHT
                 + recency * RECENCY_WEIGHT
                 + scene * SCENE_WEIGHT)

        scored.append({
            **mem,
            "final_score": final,
            "semantic_score": semantic,
            "recency_score": recency,
            "scene_score": scene,
        })

    scored.sort(key=lambda x: x["final_score"], reverse=True)

    if conflict_policy == "suppress":
        scored = _suppress_conflicts(scored)

    return scored


def _normalize_score(score: float) -> float:
    if score <= 0:
        return 0.0
    return min(1.0, score / 10.0)


def _recency_score(timestamp: float) -> float:
    if not timestamp:
        return 0.5

    age_days = (time.time() - timestamp) / 86400
    if age_days < 0:
        return 1.0
    if age_days > RECENCY_DECAY_DAYS:
        return 0.1

    return max(0.1, 1.0 - (age_days / RECENCY_DECAY_DAYS))


def _scene_score(memory_scene: str, current_scene: str) -> float:
    if not current_scene or not memory_scene:
        return 0.5

    if memory_scene == current_scene:
        return 1.0

    return 0.2


def _suppress_conflicts(memories: List[dict]) -> List[dict]:
    if len(memories) <= 1:
        return memories

    result = []
    seen_topics = {}

    for mem in memories:
        content = mem.get("content", "").lower()
        topic = _extract_topic(content)

        if topic and topic in seen_topics:
            continue

        if topic:
            seen_topics[topic] = True
        result.append(mem)

    return result


def _extract_topic(content: str) -> str:
    content = content.lower().strip()

    prefixes = ["user ", "agent ", "tool ", "task completed: "]
    for p in prefixes:
        if content.startswith(p):
            content = content[len(p):]

    action_verbs = [
        "prefers", "likes", "wants", "uses", "deploys",
        "chose", "decided", "switched", "selected",
    ]
    for verb in action_verbs:
        if verb in content:
            return verb

    words = content.split()
    if len(words) >= 4:
        return " ".join(words[:4])

    return content if content else ""
