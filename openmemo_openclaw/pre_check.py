"""
Pre-Task Memory Check — checks if a similar task has been executed before.

Returns a recommendation: reuse_or_skip, proceed, or adapt.
"""

import logging
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger("openmemo_openclaw")


@dataclass
class PreCheckResult:
    matched: bool
    task_status: str = ""
    previous_summary: str = ""
    recommended_action: str = "proceed"
    confidence: float = 0.0
    fingerprint: str = ""

    def to_dict(self) -> dict:
        return {
            "matched": self.matched,
            "task_status": self.task_status,
            "previous_summary": self.previous_summary,
            "recommended_action": self.recommended_action,
            "confidence": self.confidence,
            "fingerprint": self.fingerprint,
        }


NO_MATCH = PreCheckResult(matched=False, recommended_action="proceed")


class PreTaskChecker:
    def __init__(self, client):
        self._client = client

    def check(self, fingerprint: str, query: str = "",
              scene: str = "") -> PreCheckResult:
        if not fingerprint:
            return NO_MATCH

        results = self._client.search_memory(
            query=fingerprint,
            scene=scene,
            limit=5,
        )

        matched = self._find_matching_task(results, fingerprint)
        if not matched:
            if query:
                results = self._client.search_memory(
                    query=query,
                    scene=scene,
                    limit=5,
                )
                matched = self._find_matching_task(results, fingerprint)

        if not matched:
            logger.debug("[openmemo] pre-check: no matching task found for %s", fingerprint)
            return NO_MATCH

        status = matched.get("status", matched.get("metadata", {}).get("status", ""))
        summary = matched.get("summary", matched.get("content", ""))
        confidence = self._calculate_confidence(matched, fingerprint)
        action = self._recommend_action(status, confidence)

        logger.info(
            "[openmemo] pre-check: matched=%s status=%s action=%s confidence=%.2f",
            fingerprint, status, action, confidence,
        )

        return PreCheckResult(
            matched=True,
            task_status=status,
            previous_summary=summary[:300] if summary else "",
            recommended_action=action,
            confidence=confidence,
            fingerprint=fingerprint,
        )

    def _find_matching_task(self, results: List[dict],
                            fingerprint: str) -> Optional[dict]:
        for r in results:
            content = r.get("content", "")
            metadata = r.get("metadata", {})
            fp = metadata.get("task_fingerprint", "")

            if fp == fingerprint:
                return r

            if fingerprint in content:
                return r

        return None

    def _calculate_confidence(self, matched: dict, fingerprint: str) -> float:
        metadata = matched.get("metadata", {})
        fp = metadata.get("task_fingerprint", "")

        if fp == fingerprint:
            return 0.95

        score = matched.get("score", 0)
        if score > 8:
            return 0.85
        elif score > 5:
            return 0.7
        return 0.5

    def _recommend_action(self, status: str, confidence: float) -> str:
        if status == "success" and confidence >= 0.8:
            return "reuse_or_skip"

        if status == "success" and confidence >= 0.5:
            return "adapt"

        if status == "failed":
            return "adapt"

        return "proceed"
