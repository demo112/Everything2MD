import pytest
import json
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings
from src.core.config import ConfigManager


# =============================================================================
# Requirement 3.1: JSON format storage
# =============================================================================

def test_config_stored_as_json(tmp_path):
    """Verify config is stored as valid JSON format (Req 3.1)"""
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))
    
    # File should exist and be valid JSON
    assert config_file.exists()
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Should have expected structure
    assert "version" in data
    assert "conversion_settings" in data
    assert "path_settings" in data


def test_config_load_save(tmp_path):
    """Test basic config load and save cycle (Req 3.1)"""
    config_file = tmp_path / "config.json"

    # Initialize with no file (should use defaults)
    cm = ConfigManager(str(config_file))
    assert cm.get("log_level") == "INFO"

    # Set and Save
    cm.set("log_level", "DEBUG")

    # Reload
    cm2 = ConfigManager(str(config_file))
    assert cm2.get("log_level") == "DEBUG"


# =============================================================================
# Requirement 3.2: Default config creation when file doesn't exist
# =============================================================================

def test_config_creates_default_when_missing(tmp_path):
    """Verify default config is created when file doesn't exist (Req 3.2)"""
    config_file = tmp_path / "subdir" / "config.json"
    
    # File and directory don't exist
    assert not config_file.exists()
    assert not config_file.parent.exists()
    
    cm = ConfigManager(str(config_file))
    
    # File should now exist with defaults
    assert config_file.exists()
    assert cm.get("log_level") == "INFO"
    assert cm.get("output_format") == "markdown"


def test_config_defaults(tmp_path):
    """Test default value handling for unknown keys (Req 3.2)"""
    cm = ConfigManager(str(tmp_path / "nonexistent.json"))
    assert cm.get("unknown_key", "default") == "default"


def test_config_default_values_complete(tmp_path):
    """Verify all expected default values are present (Req 3.2, 3.4)"""
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))
    
    # Conversion settings defaults
    assert cm.get("log_level") == "INFO"
    assert cm.get("output_format") == "markdown"
    assert cm.get("max_output_file_size_mb") == 20
    assert cm.get("batch_processing_enabled") == "true"
    assert cm.get("max_parallel_jobs") == "2"
    
    # Image recognition defaults
    assert cm.get("img_rec_enabled") == False
    assert cm.get("img_rec_model") == "gpt-4-vision-preview"
    
    # Structure cleaning defaults
    assert cm.get("struct_clean_enabled") == False


# =============================================================================
# Requirement 3.3: Backup and reset on corrupted config
# =============================================================================

def test_config_invalid_json(tmp_path):
    """Test handling of corrupted JSON config (Req 3.3)"""
    f = tmp_path / "bad_config.json"
    f.write_text("{invalid_json")

    # Should handle error gracefully and use defaults
    cm = ConfigManager(str(f))
    assert cm.get("log_level") == "INFO"


def test_config_backup_on_corruption(tmp_path):
    """Verify backup is created when config is corrupted (Req 3.3)"""
    config_file = tmp_path / "config.json"
    config_file.write_text("{corrupted: json content")
    
    cm = ConfigManager(str(config_file))
    
    # Backup file should be created
    backup_file = Path(str(config_file) + ".bak")
    assert backup_file.exists()
    
    # Original file should now have valid defaults
    assert cm.get("log_level") == "INFO"


# =============================================================================
# Requirement 3.4: Support for all config items
# =============================================================================

def test_config_all_settings_accessible(tmp_path):
    """Verify all config items are accessible via get/set (Req 3.4)"""
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))
    
    # Test all mapped keys can be accessed
    config_keys = [
        "log_level", "output_format", "max_output_file_size_mb",
        "batch_processing_enabled", "max_parallel_jobs", "file_filters",
        "last_input_path", "last_output_path", "soffice_path", "pandoc_path",
        "rag_api_base", "rag_api_key",
        "img_rec_enabled", "img_rec_api_base", "img_rec_api_key", 
        "img_rec_model", "img_rec_concurrency", "img_rec_context_length",
        "struct_clean_enabled", "struct_clean_api_base", 
        "struct_clean_api_key", "struct_clean_model"
    ]
    
    for key in config_keys:
        # Should not raise exception
        value = cm.get(key)
        assert value is not None or key in ["last_input_path", "last_output_path", 
                                             "soffice_path", "pandoc_path",
                                             "img_rec_api_key", "struct_clean_api_key"]


def test_config_rag_persistence(tmp_path):
    """Test RAGFlow settings persistence (Req 3.4, 3.5)"""
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))

    cm.set("rag_api_base", "http://test-url:9999")
    cm.set("rag_api_key", "test-secret-key")

    # Reload
    cm2 = ConfigManager(str(config_file))
    assert cm2.get("rag_api_base") == "http://test-url:9999"
    assert cm2.get("rag_api_key") == "test-secret-key"


def test_config_image_recognition_settings(tmp_path):
    """Test image recognition settings (Req 3.4)"""
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))
    
    cm.set("img_rec_enabled", True)
    cm.set("img_rec_api_base", "https://custom-api.example.com")
    cm.set("img_rec_model", "gpt-4o")
    cm.set("img_rec_concurrency", "4")
    cm.set("img_rec_context_length", "1000")
    
    # Reload and verify
    cm2 = ConfigManager(str(config_file))
    assert cm2.get("img_rec_enabled") == True
    assert cm2.get("img_rec_api_base") == "https://custom-api.example.com"
    assert cm2.get("img_rec_model") == "gpt-4o"
    assert cm2.get("img_rec_concurrency") == 4
    assert cm2.get("img_rec_context_length") == 1000


def test_config_structure_cleaning_settings(tmp_path):
    """Test structure cleaning settings (Req 3.4)"""
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))
    
    cm.set("struct_clean_enabled", True)
    cm.set("struct_clean_api_base", "https://llm-api.example.com")
    cm.set("struct_clean_model", "gpt-4-turbo")
    
    # Reload and verify
    cm2 = ConfigManager(str(config_file))
    assert cm2.get("struct_clean_enabled") == True
    assert cm2.get("struct_clean_api_base") == "https://llm-api.example.com"
    assert cm2.get("struct_clean_model") == "gpt-4-turbo"


# =============================================================================
# Requirement 3.5: Immediate persistence on modification
# =============================================================================

def test_config_immediate_persistence(tmp_path):
    """Verify config is persisted immediately on set() (Req 3.5)"""
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))
    
    # Set a value
    cm.set("log_level", "DEBUG")
    
    # Read file directly without using ConfigManager
    with open(config_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Value should be persisted immediately
    assert data["conversion_settings"]["log_level"] == "DEBUG"


def test_config_batch_settings_persistence(tmp_path):
    """Test batch processing settings persistence (Req 3.4, 3.5)"""
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))
    
    cm.set("batch_processing_enabled", "false")
    cm.set("max_parallel_jobs", "8")
    cm.set("file_filters", "doc,docx,pdf")
    
    # Reload and verify
    cm2 = ConfigManager(str(config_file))
    assert cm2.get("batch_processing_enabled") == "false"
    assert cm2.get("max_parallel_jobs") == "8"
    assert cm2.get("file_filters") == "doc,docx,pdf"


def test_config_path_settings_persistence(tmp_path):
    """Test path settings persistence (Req 3.4, 3.5)"""
    config_file = tmp_path / "config.json"
    cm = ConfigManager(str(config_file))
    
    cm.set("last_input_path", "/home/user/documents")
    cm.set("last_output_path", "/home/user/output")
    cm.set("soffice_path", "/usr/bin/soffice")
    cm.set("pandoc_path", "/usr/bin/pandoc")
    
    # Reload and verify
    cm2 = ConfigManager(str(config_file))
    assert cm2.get("last_input_path") == "/home/user/documents"
    assert cm2.get("last_output_path") == "/home/user/output"
    assert cm2.get("soffice_path") == "/usr/bin/soffice"
    assert cm2.get("pandoc_path") == "/usr/bin/pandoc"


# =============================================================================
# Property-Based Tests (using Hypothesis)
# Property 2: 配置持久化往返一致性
# **Validates: Requirements 3.1, 3.5**
# =============================================================================

# Strategy for generating valid config values
config_string_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'S'), 
                           whitelist_characters=' -_./'),
    min_size=0, 
    max_size=100
).filter(lambda x: '\x00' not in x)

config_int_strategy = st.integers(min_value=1, max_value=100)

config_bool_strategy = st.booleans()

file_filters_strategy = st.lists(
    st.sampled_from(['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'txt', 'emmx']),
    min_size=1,
    max_size=9,
    unique=True
)


@given(log_level=st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR']))
@settings(max_examples=100)
def test_property_log_level_round_trip(log_level):
    """
    Property 2: Config round-trip for log_level
    
    *For any* valid log level, saving and reloading should preserve the value.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        # Set value
        cm.set("log_level", log_level)
        
        # Reload and verify round-trip
        cm2 = ConfigManager(str(config_file))
        assert cm2.get("log_level") == log_level


@given(output_format=st.sampled_from(['markdown', 'html', 'txt']))
@settings(max_examples=100)
def test_property_output_format_round_trip(output_format):
    """
    Property 2: Config round-trip for output_format
    
    *For any* valid output format, saving and reloading should preserve the value.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        cm.set("output_format", output_format)
        
        cm2 = ConfigManager(str(config_file))
        assert cm2.get("output_format") == output_format


@given(max_size=config_int_strategy)
@settings(max_examples=100)
def test_property_max_output_file_size_round_trip(max_size):
    """
    Property 2: Config round-trip for max_output_file_size_mb
    
    *For any* valid max file size, saving and reloading should preserve the value.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        cm.set("max_output_file_size_mb", max_size)
        
        cm2 = ConfigManager(str(config_file))
        assert cm2.get("max_output_file_size_mb") == max_size


@given(enabled=config_bool_strategy)
@settings(max_examples=100)
def test_property_batch_processing_enabled_round_trip(enabled):
    """
    Property 2: Config round-trip for batch_processing_enabled
    
    *For any* boolean value, saving and reloading should preserve the value.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        cm.set("batch_processing_enabled", enabled)
        
        cm2 = ConfigManager(str(config_file))
        # Note: batch_processing_enabled returns string "true"/"false"
        expected = str(enabled).lower()
        assert cm2.get("batch_processing_enabled") == expected


@given(max_jobs=st.integers(min_value=1, max_value=16))
@settings(max_examples=100)
def test_property_max_parallel_jobs_round_trip(max_jobs):
    """
    Property 2: Config round-trip for max_parallel_jobs
    
    *For any* valid parallel job count (1-16), saving and reloading should preserve the value.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        cm.set("max_parallel_jobs", str(max_jobs))
        
        cm2 = ConfigManager(str(config_file))
        # Note: max_parallel_jobs returns string
        assert cm2.get("max_parallel_jobs") == str(max_jobs)


@given(filters=file_filters_strategy)
@settings(max_examples=100)
def test_property_file_filters_round_trip(filters):
    """
    Property 2: Config round-trip for file_filters
    
    *For any* valid list of file filters, saving and reloading should preserve the value.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        filters_str = ",".join(filters)
        cm.set("file_filters", filters_str)
        
        cm2 = ConfigManager(str(config_file))
        # Note: file_filters returns comma-separated string
        result = cm2.get("file_filters")
        assert result == filters_str


@given(path=config_string_strategy)
@settings(max_examples=100)
def test_property_path_settings_round_trip(path):
    """
    Property 2: Config round-trip for path settings
    
    *For any* valid path string, saving and reloading should preserve the value.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        cm.set("last_input_path", path)
        cm.set("last_output_path", path)
        cm.set("soffice_path", path)
        cm.set("pandoc_path", path)
        
        cm2 = ConfigManager(str(config_file))
        assert cm2.get("last_input_path") == path
        assert cm2.get("last_output_path") == path
        assert cm2.get("soffice_path") == path
        assert cm2.get("pandoc_path") == path


@given(api_base=config_string_strategy, api_key=config_string_strategy)
@settings(max_examples=100)
def test_property_ragflow_settings_round_trip(api_base, api_key):
    """
    Property 2: Config round-trip for RAGFlow settings
    
    *For any* valid API base URL and key, saving and reloading should preserve the values.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        cm.set("rag_api_base", api_base)
        cm.set("rag_api_key", api_key)
        
        cm2 = ConfigManager(str(config_file))
        assert cm2.get("rag_api_base") == api_base
        assert cm2.get("rag_api_key") == api_key


@given(
    enabled=config_bool_strategy,
    api_base=config_string_strategy,
    model=st.sampled_from(['gpt-4-vision-preview', 'gpt-4o', 'claude-3-opus']),
    concurrency=st.integers(min_value=1, max_value=10),
    context_length=st.integers(min_value=100, max_value=2000)
)
@settings(max_examples=100)
def test_property_image_recognition_settings_round_trip(enabled, api_base, model, concurrency, context_length):
    """
    Property 2: Config round-trip for image recognition settings
    
    *For any* valid image recognition configuration, saving and reloading should preserve all values.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        cm.set("img_rec_enabled", enabled)
        cm.set("img_rec_api_base", api_base)
        cm.set("img_rec_model", model)
        cm.set("img_rec_concurrency", str(concurrency))
        cm.set("img_rec_context_length", str(context_length))
        
        cm2 = ConfigManager(str(config_file))
        assert cm2.get("img_rec_enabled") == enabled
        assert cm2.get("img_rec_api_base") == api_base
        assert cm2.get("img_rec_model") == model
        assert cm2.get("img_rec_concurrency") == concurrency
        assert cm2.get("img_rec_context_length") == context_length


@given(
    enabled=config_bool_strategy,
    api_base=config_string_strategy,
    model=st.sampled_from(['gpt-4', 'gpt-4-turbo', 'claude-3-sonnet'])
)
@settings(max_examples=100)
def test_property_structure_cleaning_settings_round_trip(enabled, api_base, model):
    """
    Property 2: Config round-trip for structure cleaning settings
    
    *For any* valid structure cleaning configuration, saving and reloading should preserve all values.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        cm.set("struct_clean_enabled", enabled)
        cm.set("struct_clean_api_base", api_base)
        cm.set("struct_clean_model", model)
        
        cm2 = ConfigManager(str(config_file))
        assert cm2.get("struct_clean_enabled") == enabled
        assert cm2.get("struct_clean_api_base") == api_base
        assert cm2.get("struct_clean_model") == model


@given(
    log_level=st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    max_jobs=st.integers(min_value=1, max_value=16),
    enabled=config_bool_strategy,
    path=config_string_strategy
)
@settings(max_examples=100)
def test_property_full_config_round_trip(log_level, max_jobs, enabled, path):
    """
    Property 2: Full config round-trip - multiple settings at once
    
    *For any* combination of valid config values, saving and reloading
    should preserve all values exactly.
    
    **Validates: Requirements 3.1, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_file = Path(tmp_dir) / "config.json"
        cm = ConfigManager(str(config_file))
        
        # Set multiple values
        cm.set("log_level", log_level)
        cm.set("max_parallel_jobs", str(max_jobs))
        cm.set("img_rec_enabled", enabled)
        cm.set("last_input_path", path)
        
        # Reload and verify all values
        cm2 = ConfigManager(str(config_file))
        assert cm2.get("log_level") == log_level
        assert cm2.get("max_parallel_jobs") == str(max_jobs)
        assert cm2.get("img_rec_enabled") == enabled
        assert cm2.get("last_input_path") == path
