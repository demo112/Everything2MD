import pytest
from unittest.mock import MagicMock, patch, ANY
from pathlib import Path
from src.core.engine import ConversionEngine


@pytest.fixture
def mock_config():
    cm = MagicMock()
    cm.get.side_effect = lambda k, default=None: default
    return cm


def test_detect_type(mock_config):
    engine = ConversionEngine(mock_config)
    assert engine.detect_type(Path("test.docx")) == "office"
    assert engine.detect_type(Path("test.pdf")) == "pdf"
    assert engine.detect_type(Path("test.pptx")) == "ppt"
    assert engine.detect_type(Path("test.txt")) == "text"
    assert engine.detect_type(Path("test.unknown")) is None


def test_convert_text(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)

    inp = tmp_path / "test.txt"
    inp.write_text("hello")
    out = tmp_path / "test.md"

    assert engine.convert_file(inp, out) == [out]
    assert out.exists()
    assert out.read_text() == "hello"


def test_convert_file_exists_skip(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    inp = tmp_path / "test.txt"
    out = tmp_path / "test.md"
    out.touch()

    cb = MagicMock()
    res = engine.convert_file(inp, out, status_callback=cb)

    assert res == out
    cb.assert_called_with(str(inp), "skipped", "文件已存在")


def test_convert_file_unsupported(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    inp = tmp_path / "test.xyz"
    out = tmp_path / "test.md"

    cb = MagicMock()
    res = engine.convert_file(inp, out, status_callback=cb)

    assert res is False
    cb.assert_called_with(str(inp), "failed", "不支持的文件类型")


def test_convert_file_exception(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    inp = tmp_path / "test.txt"
    out = tmp_path / "test.md"

    # Simulate shutil.copy exception by mocking it
    with patch("shutil.copy", side_effect=Exception("Disk full")):
        cb = MagicMock()
        res = engine.convert_file(inp, out, status_callback=cb)

        assert res is None
        cb.assert_called_with(str(inp), "failed", "Disk full")


def test_convert_file_office_delegation(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    engine.office_converter = MagicMock()

    inp = tmp_path / "test.docx"
    out = tmp_path / "test.md"

    engine.convert_file(inp, out)
    engine.office_converter.convert.assert_called_once_with(inp, out, context=None)


def test_convert_file_ppt_delegation(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    engine.ppt_converter = MagicMock()

    inp = tmp_path / "test.pptx"
    out = tmp_path / "test.md"

    engine.convert_file(inp, out)
    engine.ppt_converter.convert.assert_called_once_with(inp, out, context=None)


def test_convert_stop_flag(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    engine.stop_flag = True

    inp = tmp_path / "test.txt"
    out = tmp_path / "test.md"

    assert engine.convert_file(inp, out) is False


def test_run_batch_success(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)

    # Setup files
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    (input_dir / "f1.txt").write_text("1")
    (input_dir / "f2.txt").write_text("2")

    # Mock convert_file to avoid real IO overhead and focus on batch logic
    with patch.object(engine, "convert_file") as mock_convert:

        def side_effect(inp, out, *args, **kwargs):
            out.touch()
            return out

        mock_convert.side_effect = side_effect

        mock_progress = MagicMock()
        mock_file_done = MagicMock()

        engine.run(
            str(input_dir),
            str(output_dir),
            progress_callback=mock_progress,
            file_converted_callback=mock_file_done,
        )

        # Should be called twice
        assert mock_convert.call_count == 2
        assert mock_progress.call_count == 2
        assert mock_file_done.call_count == 2


def test_run_single_file(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)

    input_file = tmp_path / "f1.txt"
    input_file.write_text("1")
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with patch.object(engine, "convert_file") as mock_convert:
        mock_convert.return_value = output_dir / "f1.md"

        engine.run(str(input_file), str(output_dir))

        mock_convert.assert_called_once()
        args = mock_convert.call_args[0]
        assert args[0] == input_file
        assert args[1] == output_dir / "f1.md"


def test_run_single_file_to_file(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    input_file = tmp_path / "f1.txt"
    input_file.touch()
    output_file = tmp_path / "out.md"

    with patch.object(engine, "convert_file") as mock_convert:
        engine.run(str(input_file), str(output_file))
        args = mock_convert.call_args[0]
        assert args[1] == output_file


def test_run_filter(mock_config, tmp_path):
    # Mock config to filter only docx
    mock_config.get.side_effect = lambda k, d=None: "docx" if k == "file_filters" else d

    engine = ConversionEngine(mock_config)

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "f1.txt").touch()  # Should be skipped
    (input_dir / "f2.docx").touch()  # Should be processed
    output_dir = tmp_path / "output"

    with patch.object(engine, "convert_file") as mock_convert:
        engine.run(str(input_dir), str(output_dir))
        assert mock_convert.call_count == 1
        assert "f2.docx" in str(mock_convert.call_args[0][0])


def test_run_stop(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "f1.txt").touch()
    output_dir = tmp_path / "output"

    # Mock convert_file to set stop flag
    with patch.object(engine, "convert_file") as mock_convert:

        def side_effect(*args, **kwargs):
            engine.stop()
            return args[1]

        mock_convert.side_effect = side_effect

        # We need at least 2 files to test stopping mid-way?
        # Actually ThreadPoolExecutor might schedule all at once.
        # But loop checks stop_flag.

        engine.run(str(input_dir), str(output_dir))
        assert engine.stop_flag is True


def test_run_no_files(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    input_dir = tmp_path / "empty"
    input_dir.mkdir()

    with patch("src.core.engine.log_warn") as mock_log:
        engine.run(str(input_dir), str(tmp_path))
        mock_log.assert_called_with("没有找到需要转换的文件")


def test_run_exception_in_thread(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "f1.txt").touch()

    with patch.object(engine, "convert_file", side_effect=Exception("Thread Error")):
        with patch("src.core.engine.log_error") as mock_log:
            engine.run(str(input_dir), str(tmp_path))
            mock_log.assert_called()


def test_detect_type_all_formats(mock_config):
    """Test file type detection for all supported formats (Requirements 1.1-1.7)"""
    engine = ConversionEngine(mock_config)
    
    # Office formats (Requirement 1.1, 1.2)
    assert engine.detect_type(Path("test.doc")) == "office"
    assert engine.detect_type(Path("test.docx")) == "office"
    assert engine.detect_type(Path("test.xls")) == "office"
    assert engine.detect_type(Path("test.xlsx")) == "office"
    
    # PPT formats (Requirement 1.3, 1.4)
    assert engine.detect_type(Path("test.ppt")) == "ppt"
    assert engine.detect_type(Path("test.pptx")) == "ppt"
    
    # PDF format (Requirement 1.5)
    assert engine.detect_type(Path("test.pdf")) == "pdf"
    
    # Text format (Requirement 1.6)
    assert engine.detect_type(Path("test.txt")) == "text"
    
    # EMMX format (Requirement 1.7)
    assert engine.detect_type(Path("test.emmx")) == "emmx"
    
    # Case insensitivity
    assert engine.detect_type(Path("test.DOCX")) == "office"
    assert engine.detect_type(Path("test.PDF")) == "pdf"


def test_run_preserves_directory_structure(mock_config, tmp_path):
    """Test that batch processing preserves directory structure (Requirement 2.3)"""
    engine = ConversionEngine(mock_config)
    
    # Setup nested directory structure
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    # Create nested directories with files
    subdir1 = input_dir / "subdir1"
    subdir2 = input_dir / "subdir1" / "subdir2"
    subdir1.mkdir()
    subdir2.mkdir()
    
    (input_dir / "root.txt").write_text("root")
    (subdir1 / "level1.txt").write_text("level1")
    (subdir2 / "level2.txt").write_text("level2")
    
    with patch.object(engine, "convert_file") as mock_convert:
        def side_effect(inp, out, *args, **kwargs):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.touch()
            return out
        mock_convert.side_effect = side_effect
        
        engine.run(str(input_dir), str(output_dir))
        
        # Verify all files were processed
        assert mock_convert.call_count == 3
        
        # Verify output paths preserve structure
        call_args = [call[0] for call in mock_convert.call_args_list]
        output_paths = [str(args[1]) for args in call_args]
        
        assert any("subdir1/subdir2/level2.md" in p or "subdir1\\subdir2\\level2.md" in p for p in output_paths)
        assert any("subdir1/level1.md" in p or "subdir1\\level1.md" in p for p in output_paths)


def test_convert_file_emmx_delegation(mock_config, tmp_path):
    """Test EMMX file conversion delegation (Requirement 1.7)"""
    engine = ConversionEngine(mock_config)
    engine.emmx_converter = MagicMock()
    
    inp = tmp_path / "test.emmx"
    out = tmp_path / "test.md"
    
    engine.convert_file(inp, out)
    engine.emmx_converter.convert.assert_called_once_with(inp, out, context=None)


def test_run_multiple_filters(mock_config, tmp_path):
    """Test batch processing with multiple file filters (Requirement 2.5)"""
    # Mock config to filter docx and pdf
    mock_config.get.side_effect = lambda k, d=None: "docx,pdf" if k == "file_filters" else d
    
    engine = ConversionEngine(mock_config)
    
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "f1.txt").touch()   # Should be skipped
    (input_dir / "f2.docx").touch()  # Should be processed
    (input_dir / "f3.pdf").touch()   # Should be processed
    (input_dir / "f4.pptx").touch()  # Should be skipped
    output_dir = tmp_path / "output"
    
    with patch.object(engine, "convert_file") as mock_convert:
        engine.run(str(input_dir), str(output_dir))
        assert mock_convert.call_count == 2
        
        # Verify correct files were processed
        processed_files = [str(call[0][0]) for call in mock_convert.call_args_list]
        assert any("f2.docx" in f for f in processed_files)
        assert any("f3.pdf" in f for f in processed_files)
        assert not any("f1.txt" in f for f in processed_files)
        assert not any("f4.pptx" in f for f in processed_files)


# =============================================================================
# Property-Based Tests (using Hypothesis)
# Property 1: 文件类型检测一致性
# **Validates: Requirements 1.1-1.7**
# =============================================================================

from hypothesis import given, strategies as st, settings, HealthCheck


# Strategy for generating valid file extensions
supported_extensions = ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.pdf', '.txt', '.emmx']
unsupported_extensions = ['.xyz', '.abc', '.unknown', '.mp3', '.jpg', '.png', '.zip', '.exe']

# Expected type mappings
EXTENSION_TYPE_MAP = {
    '.doc': 'office',
    '.docx': 'office',
    '.xls': 'office',
    '.xlsx': 'office',
    '.ppt': 'ppt',
    '.pptx': 'ppt',
    '.pdf': 'pdf',
    '.txt': 'text',
    '.emmx': 'emmx',
}


def _create_mock_config():
    """Helper to create a mock config for property tests."""
    cm = MagicMock()
    cm.get.side_effect = lambda k, default=None: default
    return cm


@given(ext=st.sampled_from(supported_extensions))
@settings(max_examples=100)
def test_property_detect_type_returns_correct_type(ext):
    """
    Property 1: File type detection correctness
    
    *For any* supported file extension, detect_type() should return the correct type identifier.
    
    **Validates: Requirements 1.1-1.7**
    """
    engine = ConversionEngine(_create_mock_config())
    
    # Test with lowercase extension
    path = Path(f"test_file{ext}")
    result = engine.detect_type(path)
    expected = EXTENSION_TYPE_MAP[ext]
    assert result == expected, f"Expected {expected} for {ext}, got {result}"


@given(ext=st.sampled_from(supported_extensions))
@settings(max_examples=100)
def test_property_detect_type_case_insensitive(ext):
    """
    Property 1: File type detection is case-insensitive
    
    *For any* supported file extension in any case (upper/lower/mixed),
    detect_type() should return the same correct type identifier.
    
    **Validates: Requirements 1.1-1.7**
    """
    engine = ConversionEngine(_create_mock_config())
    
    # Test lowercase
    path_lower = Path(f"test_file{ext.lower()}")
    result_lower = engine.detect_type(path_lower)
    
    # Test uppercase
    path_upper = Path(f"test_file{ext.upper()}")
    result_upper = engine.detect_type(path_upper)
    
    # Both should return the same type
    assert result_lower == result_upper, f"Case sensitivity issue: {ext.lower()} -> {result_lower}, {ext.upper()} -> {result_upper}"
    
    # And it should be the correct type
    expected = EXTENSION_TYPE_MAP[ext]
    assert result_lower == expected


@given(ext=st.sampled_from(supported_extensions))
@settings(max_examples=100)
def test_property_detect_type_idempotent(ext):
    """
    Property 1: File type detection is idempotent
    
    *For any* file path, calling detect_type() multiple times should always return the same result.
    
    **Validates: Requirements 1.1-1.7**
    """
    engine = ConversionEngine(_create_mock_config())
    
    path = Path(f"test_file{ext}")
    
    # Call multiple times
    result1 = engine.detect_type(path)
    result2 = engine.detect_type(path)
    result3 = engine.detect_type(path)
    
    # All results should be identical
    assert result1 == result2 == result3, f"Idempotency violation: {result1}, {result2}, {result3}"


@given(ext=st.sampled_from(unsupported_extensions))
@settings(max_examples=100)
def test_property_detect_type_unsupported_returns_none(ext):
    """
    Property 1: Unsupported file types return None
    
    *For any* unsupported file extension, detect_type() should return None.
    
    **Validates: Requirements 1.1-1.7**
    """
    engine = ConversionEngine(_create_mock_config())
    
    path = Path(f"test_file{ext}")
    result = engine.detect_type(path)
    
    assert result is None, f"Expected None for unsupported extension {ext}, got {result}"


@given(
    filename=st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='_-'),
        min_size=1,
        max_size=50
    ).filter(lambda x: x and not x.startswith('.')),
    ext=st.sampled_from(supported_extensions)
)
@settings(max_examples=100)
def test_property_detect_type_filename_independent(filename, ext):
    """
    Property 1: File type detection depends only on extension
    
    *For any* valid filename with a supported extension, detect_type() should return
    the correct type regardless of the filename content.
    
    **Validates: Requirements 1.1-1.7**
    """
    engine = ConversionEngine(_create_mock_config())
    
    path = Path(f"{filename}{ext}")
    result = engine.detect_type(path)
    expected = EXTENSION_TYPE_MAP[ext]
    
    assert result == expected, f"Expected {expected} for {filename}{ext}, got {result}"


@given(
    dir_path=st.text(
        alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters='/_-'),
        min_size=0,
        max_size=50
    ),
    ext=st.sampled_from(supported_extensions)
)
@settings(max_examples=100)
def test_property_detect_type_path_independent(dir_path, ext):
    """
    Property 1: File type detection depends only on extension, not directory path
    
    *For any* file path with a supported extension, detect_type() should return
    the correct type regardless of the directory structure.
    
    **Validates: Requirements 1.1-1.7**
    """
    engine = ConversionEngine(_create_mock_config())
    
    # Clean up dir_path to avoid invalid paths
    dir_path = dir_path.strip('/').replace('//', '/')
    if dir_path:
        path = Path(f"{dir_path}/test_file{ext}")
    else:
        path = Path(f"test_file{ext}")
    
    result = engine.detect_type(path)
    expected = EXTENSION_TYPE_MAP[ext]
    
    assert result == expected, f"Expected {expected} for path {path}, got {result}"
