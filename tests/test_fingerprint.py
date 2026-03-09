import pytest
from openmemo_openclaw.fingerprint import (
    normalize_intent,
    generate_fingerprint,
    fingerprint_from_event,
)


class TestNormalizeIntent:
    def test_basic(self):
        result = normalize_intent("deploy my app")
        assert "deploy" in result
        assert "app" in result
        assert "my" not in result

    def test_verb_normalization(self):
        r1 = normalize_intent("deploying the application")
        r2 = normalize_intent("deployed the application")
        assert r1 == r2

    def test_stop_words_removed(self):
        result = normalize_intent("please install the package for me")
        assert "please" not in result
        assert "the" not in result
        assert "install" in result
        assert "package" in result

    def test_dedup(self):
        result = normalize_intent("deploy deploy deploy")
        assert result.count("deploy") == 1

    def test_truncation(self):
        long_msg = " ".join([f"word{i}" for i in range(50)])
        result = normalize_intent(long_msg)
        assert len(result.split()) <= 8

    def test_empty(self):
        assert normalize_intent("") == ""


class TestGenerateFingerprint:
    def test_basic(self):
        fp = generate_fingerprint(scene="deployment", intent="deploy my app")
        assert fp.startswith("task_fp_")
        assert len(fp) == 16

    def test_deterministic(self):
        fp1 = generate_fingerprint(scene="deployment", intent="deploy my app")
        fp2 = generate_fingerprint(scene="deployment", intent="deploy my app")
        assert fp1 == fp2

    def test_same_intent_same_fp(self):
        fp1 = generate_fingerprint(scene="deployment", intent="deploy my app")
        fp2 = generate_fingerprint(scene="deployment", intent="deploying my app")
        assert fp1 == fp2

    def test_different_scene_different_fp(self):
        fp1 = generate_fingerprint(scene="deployment", intent="run tests")
        fp2 = generate_fingerprint(scene="debug", intent="run tests")
        assert fp1 != fp2

    def test_with_tools(self):
        fp1 = generate_fingerprint(scene="deployment", intent="deploy", tools=["docker"])
        fp2 = generate_fingerprint(scene="deployment", intent="deploy")
        assert fp1 != fp2

    def test_empty_returns_empty(self):
        assert generate_fingerprint() == ""

    def test_tools_order_independent(self):
        fp1 = generate_fingerprint(tools=["docker", "ssh"])
        fp2 = generate_fingerprint(tools=["ssh", "docker"])
        assert fp1 == fp2


class TestFingerprintFromEvent:
    def test_basic(self):
        event = {"content": "deploy my app", "tools": ["docker"], "task_id": ""}
        fp = fingerprint_from_event(event, scene="deployment")
        assert fp.startswith("task_fp_")

    def test_empty_event(self):
        fp = fingerprint_from_event({})
        assert fp == ""
