import pytest
from openmemo_openclaw.task_extractor import (
    extract_task_memory,
    TaskTracker,
)


class TestExtractTaskMemory:
    def test_basic_extraction(self):
        result = extract_task_memory(
            user_request="deploy my app",
            task_result="Deployed successfully using Docker",
            scene="deployment",
            fingerprint="task_fp_abc12345",
        )
        assert result["memory_type"] == "task_execution"
        assert result["scene"] == "deployment"
        assert result["task_fingerprint"] == "task_fp_abc12345"
        assert result["status"] == "success"
        assert "Docker" in result["summary"]

    def test_with_tool_trace(self):
        result = extract_task_memory(
            user_request="deploy backend",
            tool_trace=[
                {"tool_name": "docker", "output": "built"},
                {"tool_name": "ssh", "output": "deployed"},
            ],
            task_result="Done",
            scene="deployment",
        )
        assert "docker" in result["tools_used"]
        assert "ssh" in result["tools_used"]

    def test_infer_task_name(self):
        result = extract_task_memory(
            user_request="deploy my backend service",
            task_result="Done",
            scene="deployment",
        )
        assert "deploy" in result["task_name"]

    def test_failed_status(self):
        result = extract_task_memory(
            user_request="deploy",
            task_result="Failed",
            status="failed",
        )
        assert result["status"] == "failed"

    def test_summary_truncation(self):
        long_result = "x" * 500
        result = extract_task_memory(
            user_request="test",
            task_result=long_result,
        )
        assert len(result["summary"]) <= 300


class TestTaskTracker:
    def test_basic_tracking(self):
        tracker = TaskTracker()
        tracker.set_user_request("deploy my app")
        tracker.add_tool_call("docker", "built image")
        tracker.set_scene("deployment")
        tracker.set_fingerprint("task_fp_abc")

        result = tracker.extract(task_result="Deployed successfully")
        assert result["user_request"] == "deploy my app"
        assert result["scene"] == "deployment"
        assert result["task_fingerprint"] == "task_fp_abc"
        assert "docker" in result["tools_used"]

    def test_reset(self):
        tracker = TaskTracker()
        tracker.set_user_request("test")
        tracker.add_tool_call("pytest", "passed")
        assert tracker.has_data is True

        tracker.reset()
        assert tracker.has_data is False

    def test_first_request_only(self):
        tracker = TaskTracker()
        tracker.set_user_request("first request")
        tracker.set_user_request("second request")
        result = tracker.extract()
        assert result["user_request"] == "first request"

    def test_empty_tracker(self):
        tracker = TaskTracker()
        assert tracker.has_data is False
        result = tracker.extract()
        assert result["memory_type"] == "task_execution"
