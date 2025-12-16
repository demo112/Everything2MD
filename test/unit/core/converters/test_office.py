import pytest
from unittest.mock import patch, MagicMock, ANY
from pathlib import Path
import subprocess
import os
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
            (outdir / "test.html").write_text("<html><span>text</span></html>")
            return MagicMock(returncode=0)
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect
    
    converter.convert(input_file, output_file)
    
    # Check if subprocess was called twice (LibreOffice + Pandoc)
    assert mock_run.call_count == 2
    
    # Verify post-processing (span removal)
    # output_file is written by pandoc, but we mocked pandoc.
    # The post-processing logic reads output_path.
    # We need to simulate pandoc outputting something.
    # Since we mocked subprocess.run, pandoc doesn't run.
    # So we need to write to output_file in the mock side_effect for pandoc too.
    
    # Wait, in this test setup, mock_run handles both calls.
    # The first call (soffice) creates test.html.
    # The second call (pandoc) is mocked to return success, but doesn't write to output_file.
    # So output_file doesn't exist?
    # Ah, if output_file doesn't exist, post-processing (lines 183-193) is skipped.
    
    # Let's fix this test to verify post-processing.
    

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

@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
def test_path_is_directory(mock_pandoc, mock_soffice, converter, tmp_path):
    # Mock soffice path as directory
    mock_soffice.return_value = str(tmp_path)
    mock_pandoc.return_value = "/usr/bin/pandoc"
    
    input_file = tmp_path / "test.docx"
    output_file = tmp_path / "test.md"
    
    with pytest.raises(RuntimeError, match="配置的 LibreOffice 路径是一个目录"):
        converter.convert(input_file, output_file)

@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
@patch("subprocess.run")
def test_convert_soffice_no_html_generated(mock_run, mock_pandoc, mock_soffice, converter, tmp_path):
    mock_soffice.return_value = "/usr/bin/soffice"
    mock_pandoc.return_value = "/usr/bin/pandoc"
    
    input_file = tmp_path / "test.docx"
    input_file.write_text("dummy")
    output_file = tmp_path / "test.md"
    
    # Simulate success but NO html file created
    mock_run.return_value = MagicMock(returncode=0)
    
    with pytest.raises(RuntimeError, match="LibreOffice未生成HTML文件"):
        converter.convert(input_file, output_file)

@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
@patch("subprocess.run")
def test_convert_pandoc_missing_fallback(mock_run, mock_pandoc, mock_soffice, converter, tmp_path):
    # Case: LibreOffice generates HTML, but Pandoc is missing
    mock_soffice.return_value = "/usr/bin/soffice"
    mock_pandoc.return_value = None
    
    input_file = tmp_path / "test.docx"
    input_file.write_text("dummy")
    output_file = tmp_path / "test.md"
    
    def side_effect(cmd, **kwargs):
        if "soffice" in cmd[0]:
            outdir = Path(cmd[6])
            (outdir / "test.html").write_text("<html>content</html>")
            return MagicMock(returncode=0)
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect
    
    converter.convert(input_file, output_file)
    
    # Should copy HTML to output_file
    assert output_file.exists()
    assert output_file.read_text() == "<html>content</html>"

@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
@patch("subprocess.run")
def test_pandoc_exit_21_fallback(mock_run, mock_pandoc, mock_soffice, converter, tmp_path):
    mock_soffice.return_value = "/usr/bin/soffice"
    mock_pandoc.return_value = "/usr/bin/pandoc"
    
    input_file = tmp_path / "test.docx"
    input_file.write_text("dummy")
    output_file = tmp_path / "test.md"
    
    # 1. Soffice success
    # 2. Pandoc (with Lua) fails with Exit 21
    # 3. Pandoc (no Lua) succeeds
    
    def side_effect(cmd, **kwargs):
        cmd_str = str(cmd)
        if "soffice" in cmd[0]:
            outdir = Path(cmd[6])
            (outdir / "test.html").write_text("<html></html>")
            return MagicMock(returncode=0)
        elif "pandoc" in cmd[0]:
            if "lua-filter" in cmd_str or ".lua" in cmd_str:
                raise subprocess.CalledProcessError(21, cmd)
            else:
                # Fallback success
                return MagicMock(returncode=0)
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect
    
    converter.convert(input_file, output_file)
    
    # Should call subprocess 3 times: 1 Soffice, 1 Pandoc(Fail), 1 Pandoc(Fallback)
    assert mock_run.call_count == 3

@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
@patch("subprocess.run")
def test_post_processing(mock_run, mock_pandoc, mock_soffice, converter, tmp_path):
    mock_soffice.return_value = "/usr/bin/soffice"
    mock_pandoc.return_value = "/usr/bin/pandoc"
    
    input_file = tmp_path / "test.docx"
    input_file.write_text("dummy")
    output_file = tmp_path / "test.md"
    
    def side_effect(cmd, **kwargs):
        if "soffice" in cmd[0]:
            outdir = Path(cmd[6])
            (outdir / "test.html").write_text("<html></html>")
        elif "pandoc" in cmd[0]:
            # Simulate Pandoc output with span tags
            output_file.write_text("Some <span class='x'>text</span> and <div>div</div>", encoding='utf-8')
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect
    
    converter.convert(input_file, output_file)
    
    # Verify cleanup
    content = output_file.read_text(encoding='utf-8')
    assert "<span>" not in content
    assert "<div>" not in content
    assert content == "Some text and div"
