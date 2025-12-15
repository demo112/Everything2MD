import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess
import sys
from src.core.converters.ppt import PptConverter

@pytest.fixture
def converter():
    return PptConverter()

@patch("src.core.converters.ppt.get_soffice_path")
@patch("src.core.converters.ppt.get_pandoc_path")
@patch("subprocess.run")
def test_convert_ppt_success(mock_run, mock_pandoc, mock_soffice, converter, tmp_path):
    mock_soffice.return_value = "/usr/bin/soffice"
    mock_pandoc.return_value = "/usr/bin/pandoc"
    
    input_file = tmp_path / "test.ppt"
    input_file.write_text("dummy")
    output_file = tmp_path / "test.md"
    
    # Simulate side effects
    def side_effect(cmd, **kwargs):
        if "soffice" in cmd[0]:
            # PPT -> PDF
            # The command uses --outdir
            # cmd[4] is the path to input file or outdir?
            # cmd: [soffice, --headless, --convert-to, pdf, --outdir, TEMP_DIR, INPUT_FILE]
            # Index 0: soffice
            # Index 1: --headless
            # Index 2: --convert-to
            # Index 3: pdf
            # Index 4: --outdir
            # Index 5: TEMP_DIR
            outdir = Path(cmd[5])
            (outdir / "test.pdf").write_text("dummy pdf")
            return MagicMock(returncode=0)
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect
    
    converter.convert(input_file, output_file)
    
    assert mock_run.call_count == 2 # soffice + pandoc

@patch("src.core.converters.ppt.get_soffice_path")
def test_convert_ppt_no_soffice(mock_soffice, converter, tmp_path):
    mock_soffice.return_value = None
    input_file = tmp_path / "test.ppt"
    output_file = tmp_path / "test.md"
    
    with pytest.raises(RuntimeError, match="LibreOffice未安装"):
        converter.convert(input_file, output_file)

@patch("subprocess.run")
def test_convert_pptx_pptx2md(mock_run, converter, tmp_path):
    # This requires pptx2md importable or we mock the import?
    # The code tries to import pptx2md.
    # Since we likely don't have it in test env, it might raise ImportError
    # and fallback to LibreOffice logic.
    
    # We want to test the pptx2md path.
    # We need to mock sys.modules or the specific import in the function.
    
    input_file = tmp_path / "test.pptx"
    output_file = tmp_path / "test.md"
    
    # Mock the import check in _convert_pptx
    with patch.dict('sys.modules', {'pptx2md.parser': MagicMock(), 'pptx2md.outputter': MagicMock()}):
        converter.convert(input_file, output_file)
        
        # Should call subprocess for pptx2md
        mock_run.assert_called_once()
        assert "pptx2md" in mock_run.call_args[0][0]

def test_convert_pptx_import_fail_fallback(converter, tmp_path):
    # If import fails, it should fallback to _convert_ppt (LibreOffice)
    # We mock _convert_ppt to verify fallback
    
    input_file = tmp_path / "test.pptx"
    output_file = tmp_path / "test.md"
    
    with patch.object(converter, '_convert_ppt') as mock_fallback:
        # Force import error by ensuring it's not in sys.modules
        with patch.dict('sys.modules'):
            if 'pptx2md' in sys.modules:
                del sys.modules['pptx2md']
                
            converter.convert(input_file, output_file)
            mock_fallback.assert_called_once()
