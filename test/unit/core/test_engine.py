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
    
    assert engine.convert_file(inp, out) == out
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
    with patch.object(engine, 'convert_file') as mock_convert:
        def side_effect(inp, out, *args, **kwargs):
            out.touch()
            return out
        mock_convert.side_effect = side_effect

        mock_progress = MagicMock()
        mock_file_done = MagicMock()

        engine.run(str(input_dir), str(output_dir), 
                  progress_callback=mock_progress,
                  file_converted_callback=mock_file_done)
        
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
    
    with patch.object(engine, 'convert_file') as mock_convert:
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
    
    with patch.object(engine, 'convert_file') as mock_convert:
        engine.run(str(input_file), str(output_file))
        args = mock_convert.call_args[0]
        assert args[1] == output_file

def test_run_filter(mock_config, tmp_path):
    # Mock config to filter only docx
    mock_config.get.side_effect = lambda k, d=None: "docx" if k == "file_filters" else d
    
    engine = ConversionEngine(mock_config)
    
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "f1.txt").touch() # Should be skipped
    (input_dir / "f2.docx").touch() # Should be processed
    output_dir = tmp_path / "output"
    
    with patch.object(engine, 'convert_file') as mock_convert:
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
    with patch.object(engine, 'convert_file') as mock_convert:
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
    
    with patch.object(engine, 'convert_file', side_effect=Exception("Thread Error")):
        with patch("src.core.engine.log_error") as mock_log:
            engine.run(str(input_dir), str(tmp_path))
            mock_log.assert_called()
