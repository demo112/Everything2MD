import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path
import subprocess
from src.core.converters.office import OfficeConverter


@pytest.fixture
def converter():
    return OfficeConverter()


@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
@patch("subprocess.run")
@patch("shutil.copy")
@patch("time.sleep")  # Don't actually sleep
def test_copy_retry_success(
    mock_sleep, mock_copy, mock_run, mock_pandoc, mock_soffice, converter, tmp_path
):
    """Test that file copying retries and eventually succeeds"""
    mock_soffice.return_value = "/usr/bin/soffice"
    mock_pandoc.return_value = "/usr/bin/pandoc"

    input_file = tmp_path / "test.docx"
    output_file = tmp_path / "test.md"

    # Simulate PermissionError twice, then success
    mock_copy.side_effect = [PermissionError("Busy"), PermissionError("Busy"), None]

    # Mock subprocess success (LibreOffice) and create dummy HTML
    def side_effect(cmd, **kwargs):
        # cmd: [soffice, ..., --outdir, TEMP_DIR, INPUT]
        # We need to find --outdir and next arg
        try:
            idx = cmd.index("--outdir")
            outdir = Path(cmd[idx + 1])
            (outdir / "test.html").write_text("<html></html>")
        except ValueError:
            pass
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect

    # We need to ensure temporary directory mocking or just let it use real temp dir?
    # The code uses tempfile.TemporaryDirectory().
    # We can mock tempfile.TemporaryDirectory to return a known path if we want precise control,
    # or just let it run. But we need to make sure input_file.name is valid.

    # To avoid real file system issues with shutil.copy (since we mocked it),
    # we just need to ensure the flow works.

    # We need to mock os.chmod and os.remove as well inside the loop?
    # They are in a try-except block.

    converter.convert(input_file, output_file)

    # Verify copy was called 3 times
    assert mock_copy.call_count == 3

    # Verify sleep was called 2 times
    assert mock_sleep.call_count == 2


@patch("src.core.converters.office.get_soffice_path")
@patch("src.core.converters.office.get_pandoc_path")
@patch("shutil.copy")
@patch("time.sleep")
def test_copy_retry_failure(
    mock_sleep, mock_copy, mock_pandoc, mock_soffice, converter, tmp_path
):
    """Test that file copying fails after max retries"""
    mock_soffice.return_value = "/usr/bin/soffice"
    mock_pandoc.return_value = "/usr/bin/pandoc"

    input_file = tmp_path / "test.docx"
    output_file = tmp_path / "test.md"

    # Simulate persistent error
    mock_copy.side_effect = PermissionError("Busy")

    with pytest.raises(RuntimeError, match="无法复制文件到临时目录"):
        converter.convert(input_file, output_file)

    # Should retry 5 times
    assert mock_copy.call_count == 5
