import pytest
import json
from src.core.config import ConfigManager


def test_config_load_save(tmp_path):
    config_file = tmp_path / "config.json"

    # Initialize with no file (should use defaults)
    cm = ConfigManager(str(config_file))
    assert cm.get("log_level") == "INFO"

    # Set and Save
    cm.set("log_level", "DEBUG")

    # Reload
    cm2 = ConfigManager(str(config_file))
    assert cm2.get("log_level") == "DEBUG"


def test_config_defaults(tmp_path):
    cm = ConfigManager(str(tmp_path / "nonexistent.json"))
    assert cm.get("unknown_key", "default") == "default"


def test_config_invalid_json(tmp_path):
    f = tmp_path / "bad_config.json"
    f.write_text("{invalid_json")

    # Should handle error gracefully and use defaults
    cm = ConfigManager(str(f))
    assert cm.get("log_level") == "INFO"


def test_config_rag_persistence(tmp_path):
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))

    # Check default (might be None or default string depending on impl)
    # Just set new values and verify persistence

    cm.set("rag_api_base", "http://test-url:9999")
    cm.set("rag_api_key", "test-secret-key")

    # Reload
    cm2 = ConfigManager(str(config_file))
    assert cm2.get("rag_api_base") == "http://test-url:9999"
    assert cm2.get("rag_api_key") == "test-secret-key"
