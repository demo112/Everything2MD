import pytest
from unittest.mock import patch, MagicMock, ANY
from pathlib import Path
import subprocess
from src.core.converters.office import OfficeConverter

@pytest.fixture
def converter():
    return OfficeConverter()

@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
@patch("subprocess.run")
def test_convert_docx_success(mock_run, mock_pandoc, mock_soffice, converter, tmp_path):
    mock_soffice.return_value = "/usr/bin/soffice"
    mock_pandoc.return_value = "/usr/bin/pandoc"
    
    input_file = tmp_path / "test.docx"
    input_file.write_text("dummy")
    output_file = tmp_path / "test.md"
    
    # Mock subprocess to simulate success
    # 1. LibreOffice: create dummy html
    def side_effect(cmd, **kwargs):
        if "soffice" in cmd[0]:
            # Simulate HTML creation in temp dir
            # cmd: [soffice, -env:..., --headless, --convert-to, html, --outdir, TEMP_DIR, INPUT_FILE]
            # Index 6 is TEMP_DIR
            outdir = Path(cmd[6])
            (outdir / "test.html").write_text("<html></html>")
            return MagicMock(returncode=0)
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect
    
    converter.convert(input_file, output_file)
    
    # Check if subprocess was called twice (LibreOffice + Pandoc)
    assert mock_run.call_count == 2
    
@patch("src.core.converters.office.get_soffice_path")
def test_convert_no_soffice(mock_soffice, converter, tmp_path):
    mock_soffice.return_value = None
    input_file = tmp_path / "test.doc" # .doc needs soffice
    output_file = tmp_path / "test.md"
    
    with pytest.raises(RuntimeError, match="LibreOffice未安装"):
        converter.convert(input_file, output_file)

@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
@patch("subprocess.run")
def test_convert_docx_fallback_pandoc(mock_run, mock_pandoc, mock_soffice, converter, tmp_path):
    # Case: No LibreOffice but Pandoc exists and input is .docx
    mock_soffice.return_value = None
    mock_pandoc.return_value = "/usr/bin/pandoc"
    
    input_file = tmp_path / "test.docx"
    input_file.write_text("dummy")
    output_file = tmp_path / "test.md"
    
    converter.convert(input_file, output_file)
    
    # Should call pandoc direct
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[0] == "/usr/bin/pandoc"
    assert str(input_file) in args

@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
@patch("subprocess.run")
def test_convert_soffice_failure_retry(mock_run, mock_pandoc, mock_soffice, converter, tmp_path):
    mock_soffice.return_value = "/usr/bin/soffice"
    mock_pandoc.return_value = "/usr/bin/pandoc"
    
    input_file = tmp_path / "test.docx"
    input_file.write_text("dummy")
    output_file = tmp_path / "test.md"
    
    # Simulate failure
    mock_run.side_effect = subprocess.CalledProcessError(1, "soffice")
    
    with pytest.raises(RuntimeError, match="LibreOffice转换失败"):
        converter.convert(input_file, output_file)
        
    # Should retry 3 times
    assert mock_run.call_count == 3
