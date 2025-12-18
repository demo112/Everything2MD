import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.core.converters.office import OfficeConverter
import subprocess


@pytest.fixture
def office_converter():
    return OfficeConverter()


def test_convert_docx_libreoffice(office_converter):
    input_path = Path("test.docx")
    output_path = Path("output.md")

    with patch(
        "src.core.converters.office.get_soffice_path", return_value="/usr/bin/soffice"
    ):
        with patch(
            "src.core.converters.office.get_pandoc_path", return_value="/usr/bin/pandoc"
        ):
            with patch("subprocess.Popen") as mock_popen:
                # Mock tempfile
                with patch("tempfile.TemporaryDirectory") as mock_temp:
                    mock_temp.return_value.__enter__.return_value = "/tmp/dir"
                    with patch("shutil.copy") as mock_copy:
                        with patch("os.path.isdir", return_value=False):
                            # Mock the actual conversion command execution
                            mock_proc = Mock()
                            mock_proc.communicate.return_value = (b"", b"")
                            mock_proc.returncode = 0
                            mock_proc.poll.return_value = (
                                0  # Fix for subprocess.run check
                            )
                            # Make mock_proc a context manager for subprocess.run usage of Popen
                            mock_proc.__enter__ = Mock(return_value=mock_proc)
                            mock_proc.__exit__ = Mock(return_value=None)

                            mock_popen.return_value = mock_proc

                            # OfficeConverter logic for PDF output:
                            # 1. Check soffice path
                            # 2. Copy to temp
                            # 3. Convert to PDF (soffice)
                            # 4. Move PDF to output path

                            output_path_pdf = output_path.with_suffix(".pdf")
                            with patch(
                                "src.core.converters.office.Path.exists",
                                return_value=True,
                            ):
                                with patch("shutil.move") as mock_move:
                                    office_converter.convert(
                                        input_path, output_path_pdf
                                    )

                                    # Verify soffice called
                                    args, _ = mock_popen.call_args
                                    cmd = args[0]
                                    assert "/usr/bin/soffice" in cmd
                                    assert "--convert-to" in cmd
                                    assert "pdf" in cmd

                                    # Verify move called
                                    mock_move.assert_called_once()


def test_convert_docx_pandoc_fallback(office_converter):
    input_path = Path("test.docx")
    output_path = Path("output.md")

    with patch("src.core.converters.office.get_soffice_path", return_value=None):
        with patch(
            "src.core.converters.office.get_pandoc_path", return_value="/usr/bin/pandoc"
        ):
            with patch(
                "src.core.converters.office.OfficeConverter._convert_with_pandoc_direct"
            ) as mock_pandoc:
                office_converter.convert(input_path, output_path)
                mock_pandoc.assert_called_once()


def test_convert_no_converter(office_converter):
    input_path = Path("test.docx")
    output_path = Path("output.md")

    with patch("src.core.converters.office.get_soffice_path", return_value=None):
        with patch("src.core.converters.office.get_pandoc_path", return_value=None):
            with pytest.raises(RuntimeError, match="LibreOffice.*未安装"):
                office_converter.convert(input_path, output_path)
