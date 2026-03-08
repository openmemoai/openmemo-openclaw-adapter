import pytest
from openmemo_openclaw.scenes import SceneMapper, detect_scene


class TestSceneMapper:
    def test_coding_from_tools(self):
        mapper = SceneMapper()
        scene = mapper.detect(tools=["code_editor"])
        assert scene == "coding"

    def test_debug_from_tools(self):
        mapper = SceneMapper()
        scene = mapper.detect(tools=["pytest"])
        assert scene == "debug"

    def test_deployment_from_tools(self):
        mapper = SceneMapper()
        scene = mapper.detect(tools=["docker"])
        assert scene == "deployment"

    def test_research_from_tools(self):
        mapper = SceneMapper()
        scene = mapper.detect(tools=["web_search"])
        assert scene == "research"

    def test_coding_from_files(self):
        mapper = SceneMapper()
        scene = mapper.detect(file_paths=["src/main.py"])
        assert scene == "coding"

    def test_debug_from_files(self):
        mapper = SceneMapper()
        scene = mapper.detect(file_paths=["test_main.py"])
        assert scene == "debug"

    def test_deployment_from_keywords(self):
        mapper = SceneMapper()
        scene = mapper.detect(prompt="deploy to kubernetes")
        assert scene == "deployment"

    def test_fallback_general(self):
        mapper = SceneMapper()
        scene = mapper.detect(prompt="hello")
        assert scene == "general"

    def test_scene_override(self):
        mapper = SceneMapper()
        mapper.scene_override("debug")
        scene = mapper.detect(tools=["docker"])
        assert scene == "debug"

    def test_clear_override(self):
        mapper = SceneMapper()
        mapper.scene_override("debug")
        mapper.clear_override()
        scene = mapper.detect(tools=["docker"])
        assert scene == "deployment"

    def test_combined_signals(self):
        mapper = SceneMapper()
        scene = mapper.detect(
            tools=["docker"],
            prompt="deploy my application",
        )
        assert scene == "deployment"


class TestDetectScene:
    def test_function(self):
        scene = detect_scene(tools=["pytest"], prompt="fix the bug")
        assert scene == "debug"
