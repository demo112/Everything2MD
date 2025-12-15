import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.core.engine import ConversionEngine

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
    
    # assert engine.convert_file(inp, out) is True
    # The new engine returns the output path on success, not True
    assert engine.convert_file(inp, out) == out
    assert out.exists()
    assert out.read_text() == "hello"

def test_run_batch(mock_config, tmp_path):
    engine = ConversionEngine(mock_config)
    
    # Setup files
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    (input_dir / "f1.txt").write_text("1")
    (input_dir / "f2.txt").write_text("2")
    
    # Mock converters for other types to avoid needing soffice
    with patch.object(engine, 'convert_file') as mock_convert:
        # We only want to mock execution, but wait, run calls convert_file inside threadpool.
        # It's better to integration test the run logic with real text conversion or mock convert_file logic.
        
        # Let's trust text conversion works (tested above) and test the threading logic using text files.
        # However, engine.run calls convert_file. If we mock convert_file, it won't actually create files.
        # But the test asserts files exist.
        # So we should mock side_effect to create files if we want to isolate threading.
        # Or just don't mock convert_file and let it run real conversion (since text conversion is fast/safe).
        
        # Remove the mock of convert_file to let it run real logic?
        # Or better, make the mock create the file.
        def side_effect(inp, out, *args, **kwargs):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text("mocked")
            return out

        mock_convert.side_effect = side_effect

        mock_callback = MagicMock()
        mock_file_callback = MagicMock()

        engine.run(str(input_dir), str(output_dir), 
                  progress_callback=mock_callback,
                  file_converted_callback=mock_file_callback)
    
    # Verify
    assert (output_dir / "f1.md").exists()
    assert (output_dir / "f2.md").exists()
    assert mock_callback.call_count == 2
    assert mock_file_callback.call_count == 2
