import pytest
from openmemo_openclaw.health import (
    check_library,
    HealthCheckError,
    run_health_check,
)
from openmemo_openclaw.config import AdapterConfig


class TestCheckLibrary:
    def test_library_available(self):
        results = check_library()
        assert len(results) >= 1
        names = [r[0] for r in results]
        assert "library" in names
        lib_ok = next(ok for name, ok, _ in results if name == "library")
        assert lib_ok is True

    def test_library_init(self):
        results = check_library()
        init_results = [r for r in results if r[0] == "init"]
        if init_results:
            assert init_results[0][1] is True


class TestRunHealthCheck:
    def test_library_backend(self):
        config = AdapterConfig(backend="library")
        result = run_health_check(config)
        assert result == "library"

    def test_unknown_backend_raises(self):
        config = AdapterConfig(backend="nonexistent")
        with pytest.raises(HealthCheckError):
            run_health_check(config)

    def test_local_api_unreachable(self):
        config = AdapterConfig(backend="local_api", endpoint="http://127.0.0.1:19999")
        with pytest.raises(HealthCheckError, match="cannot connect"):
            run_health_check(config)

    def test_auto_falls_to_library(self):
        config = AdapterConfig(
            backend="auto",
            endpoint="http://127.0.0.1:19999",
            cloud_url="http://127.0.0.1:19998",
        )
        result = run_health_check(config)
        assert result == "library"
