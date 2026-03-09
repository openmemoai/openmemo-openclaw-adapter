import time
import pytest
from openmemo_openclaw.ranker import rank_memories


class TestRankMemories:
    def test_empty_input(self):
        assert rank_memories([]) == []

    def test_single_memory(self):
        memories = [{"content": "test", "score": 5.0}]
        ranked = rank_memories(memories)
        assert len(ranked) == 1
        assert "final_score" in ranked[0]

    def test_sorts_by_final_score(self):
        memories = [
            {"content": "low", "score": 1.0},
            {"content": "high", "score": 8.0},
        ]
        ranked = rank_memories(memories)
        assert ranked[0]["content"] == "high"

    def test_recency_boost(self):
        now = time.time()
        memories = [
            {"content": "old", "score": 5.0, "timestamp": now - 86400 * 25},
            {"content": "new", "score": 5.0, "timestamp": now},
        ]
        ranked = rank_memories(memories)
        assert ranked[0]["content"] == "new"

    def test_scene_boost(self):
        memories = [
            {"content": "wrong scene", "score": 5.0, "scene": "coding"},
            {"content": "right scene", "score": 5.0, "scene": "deployment"},
        ]
        ranked = rank_memories(memories, current_scene="deployment")
        assert ranked[0]["content"] == "right scene"

    def test_conflict_suppression(self):
        memories = [
            {"content": "User prefers Python", "score": 8.0, "timestamp": time.time()},
            {"content": "User prefers Java", "score": 7.0, "timestamp": time.time() - 86400},
        ]
        ranked = rank_memories(memories, conflict_policy="suppress")
        assert len(ranked) == 1
        assert "Python" in ranked[0]["content"]

    def test_no_conflict_suppression(self):
        memories = [
            {"content": "User prefers Python", "score": 8.0},
            {"content": "User prefers Java", "score": 7.0},
        ]
        ranked = rank_memories(memories, conflict_policy="none")
        assert len(ranked) == 2

    def test_scoring_components(self):
        memories = [{"content": "test", "score": 5.0, "timestamp": time.time(), "scene": "coding"}]
        ranked = rank_memories(memories, current_scene="coding")
        r = ranked[0]
        assert 0 <= r["semantic_score"] <= 1.0
        assert 0 <= r["recency_score"] <= 1.0
        assert 0 <= r["scene_score"] <= 1.0
        assert 0 <= r["task_score"] <= 1.0

    def test_task_execution_gets_boost(self):
        memories = [
            {"content": "general observation", "score": 5.0, "memory_type": "observation"},
            {"content": "task execution log", "score": 5.0, "memory_type": "task_execution"},
        ]
        ranked = rank_memories(memories)
        assert ranked[0]["content"] == "task execution log"
        assert ranked[0]["task_score"] > ranked[1]["task_score"]

    def test_decision_memory_boost(self):
        memories = [
            {"content": "some fact", "score": 5.0, "memory_type": "observation"},
            {"content": "deploy decision", "score": 5.0, "memory_type": "decision"},
        ]
        ranked = rank_memories(memories)
        assert ranked[0]["task_score"] > ranked[1]["task_score"]
