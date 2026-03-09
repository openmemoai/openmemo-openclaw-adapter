import pytest
from unittest.mock import patch
from openmemo_openclaw.version_check import (
    VersionInfo, check_version, get_local_versions,
    log_version_status, _is_newer,
)


class TestVersionInfo:
    def test_defaults(self):
        info = VersionInfo()
        assert info.local_core is None
        assert info.local_adapter is None
        assert info.latest_core is None
        assert info.latest_adapter is None
        assert info.update_available is False


class TestGetLocalVersions:
    def test_returns_dict(self):
        result = get_local_versions()
        assert isinstance(result, dict)
        assert "core" in result
        assert "adapter" in result


class TestIsNewer:
    def test_newer(self):
        assert _is_newer("2.0.0", "1.0.0") is True

    def test_same(self):
        assert _is_newer("1.0.0", "1.0.0") is False

    def test_older(self):
        assert _is_newer("0.5.0", "1.0.0") is False

    def test_invalid(self):
        assert _is_newer("abc", "1.0.0") is False


class TestCheckVersion:
    @patch("openmemo_openclaw.version_check._fetch_remote_versions")
    def test_no_remote(self, mock_fetch):
        mock_fetch.return_value = None
        info = check_version()
        assert isinstance(info, VersionInfo)
        assert info.update_available is False

    @patch("openmemo_openclaw.version_check._fetch_remote_versions")
    def test_update_available(self, mock_fetch):
        mock_fetch.return_value = {
            "latest_core": "99.0.0",
            "latest_adapter": "99.0.0",
        }
        info = check_version()
        assert info.update_available is True
        assert info.latest_core == "99.0.0"

    @patch("openmemo_openclaw.version_check._fetch_remote_versions")
    def test_no_update(self, mock_fetch):
        mock_fetch.return_value = {
            "latest_core": "0.0.1",
            "latest_adapter": "0.0.1",
        }
        info = check_version()
        assert info.update_available is False


class TestLogVersionStatus:
    @patch("openmemo_openclaw.version_check.check_version")
    def test_logs_without_error(self, mock_check):
        mock_check.return_value = VersionInfo(
            local_core="0.4.0",
            local_adapter="2.0.0",
        )
        log_version_status()

    def test_with_info(self):
        info = VersionInfo(
            local_core="0.4.0",
            local_adapter="2.0.0",
            latest_core="0.4.0",
            latest_adapter="2.0.0",
            update_available=False,
        )
        log_version_status(info)


class TestFeatureFlags:
    def test_default_features(self):
        from openmemo_openclaw.config import AdapterConfig
        config = AdapterConfig()
        assert config.features["inspector"] is True
        assert config.features["task_precheck"] is True
        assert config.features["suppression"] is True

    def test_features_from_dict(self):
        from openmemo_openclaw.config import AdapterConfig
        config = AdapterConfig.from_dict({
            "memory": {
                "features": {
                    "inspector": False,
                    "task_precheck": True,
                }
            }
        })
        assert config.features["inspector"] is False
        assert config.features["task_precheck"] is True
        assert config.features["suppression"] is True

    def test_features_unknown_flag(self):
        from openmemo_openclaw.config import AdapterConfig
        config = AdapterConfig.from_dict({
            "memory": {
                "features": {
                    "new_feature": True,
                }
            }
        })
        assert config.features["new_feature"] is True
        assert config.features["inspector"] is True
