import pytest
from openmemo_openclaw.pre_check import (
    PreTaskChecker,
    PreCheckResult,
    NO_MATCH,
)


class MockClient:
    def __init__(self, search_results=None):
        self._results = search_results or []

    def search_memory(self, query="", scene="", limit=5):
        return self._results


class TestPreCheckResult:
    def test_no_match(self):
        assert NO_MATCH.matched is False
        assert NO_MATCH.recommended_action == "proceed"

    def test_to_dict(self):
        result = PreCheckResult(
            matched=True,
            task_status="success",
            previous_summary="Done",
            recommended_action="reuse_or_skip",
            confidence=0.92,
            fingerprint="task_fp_abc",
        )
        d = result.to_dict()
        assert d["matched"] is True
        assert d["recommended_action"] == "reuse_or_skip"
        assert d["confidence"] == 0.92


class TestPreTaskChecker:
    def test_no_fingerprint(self):
        checker = PreTaskChecker(MockClient())
        result = checker.check("")
        assert result.matched is False

    def test_no_match_found(self):
        checker = PreTaskChecker(MockClient([]))
        result = checker.check("task_fp_abc")
        assert result.matched is False
        assert result.recommended_action == "proceed"

    def test_match_by_fingerprint_in_metadata(self):
        client = MockClient([
            {
                "content": "Task deployed",
                "metadata": {
                    "task_fingerprint": "task_fp_abc",
                    "status": "success",
                },
                "summary": "Deployed via Docker",
                "status": "success",
                "score": 9.0,
            }
        ])
        checker = PreTaskChecker(client)
        result = checker.check("task_fp_abc")
        assert result.matched is True
        assert result.task_status == "success"
        assert result.recommended_action == "reuse_or_skip"
        assert result.confidence >= 0.9

    def test_match_by_fingerprint_in_content(self):
        client = MockClient([
            {
                "content": "Task: deploy_app | Fingerprint: task_fp_xyz | Status: success | Summary: Done",
                "metadata": {},
                "score": 8.0,
            }
        ])
        checker = PreTaskChecker(client)
        result = checker.check("task_fp_xyz")
        assert result.matched is True

    def test_failed_task_recommends_adapt(self):
        client = MockClient([
            {
                "content": "Task failed",
                "metadata": {
                    "task_fingerprint": "task_fp_fail",
                    "status": "failed",
                },
                "status": "failed",
                "score": 9.0,
            }
        ])
        checker = PreTaskChecker(client)
        result = checker.check("task_fp_fail")
        assert result.matched is True
        assert result.recommended_action == "adapt"

    def test_exact_fingerprint_high_confidence(self):
        client = MockClient([
            {
                "content": "Task done",
                "metadata": {
                    "task_fingerprint": "task_fp_exact",
                    "status": "success",
                },
                "status": "success",
                "score": 2.0,
            }
        ])
        checker = PreTaskChecker(client)
        result = checker.check("task_fp_exact")
        assert result.matched is True
        assert result.confidence >= 0.9
        assert result.recommended_action == "reuse_or_skip"
