import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess
from src.core.converters.ppt import PptConverter
from src.core.engine import ConversionEngine


@pytest.fixture
def ppt_converter():
    return PptConverter()


@pytest.fixture
def engine():
    config = MagicMock()
    config.get.return_value = "docx,pptx,pdf,txt"
    return ConversionEngine(config)


def test_pdf_direct_conversion_routing(engine, tmp_path):
    """Test that .pdf files are routed to PptConverter"""
    input_path = tmp_path / "test.pdf"
    input_path.touch()
    output_path = tmp_path / "test.md"

    # Mock the converters
    engine.ppt_converter = MagicMock()
    engine.office_converter = MagicMock()

    # Setup return value
    engine.ppt_converter.convert.return_value = output_path

    # Run
    res = engine.convert_file(input_path, output_path)

    # Verify routing
    engine.ppt_converter.convert.assert_called_once_with(
        input_path, output_path, context=None
    )
    engine.office_converter.convert.assert_not_called()
    assert res == [output_path]


def test_pdf_fallback_suffix_change(engine, tmp_path):
    """Test that engine returns the modified path when suffix changes"""
    input_path = tmp_path / "test.pdf"
    input_path.touch()
    output_path = tmp_path / "test.md"

    fallback_path = tmp_path / "test.pdf"  # output path suffix changed

    engine.ppt_converter = MagicMock()
    engine.ppt_converter.convert.return_value = fallback_path

    res = engine.convert_file(input_path, output_path)

    assert res == [fallback_path]


def test_ppt_converter_pdf_input(ppt_converter, tmp_path):
    """Test PptConverter handles .pdf input directly"""
    input_path = tmp_path / "test.pdf"
    input_path.touch()
    output_path = tmp_path / "test.md"

    # Mock _convert_pdf_to_md to avoid actual conversion
    with patch.object(ppt_converter, "_convert_pdf_to_md") as mock_method:
        mock_method.return_value = output_path

        res = ppt_converter.convert(input_path, output_path)

        mock_method.assert_called_once_with(input_path, output_path, None)
        assert res == output_path


def test_pdf_conversion_pandoc_success(ppt_converter, tmp_path):
    """Test PDF conversion using Pandoc (first choice)"""
    input_path = tmp_path / "test.pdf"
    input_path.touch()
    output_path = tmp_path / "test.md"

    with patch(
        "src.core.converters.ppt.get_pandoc_path", return_value="/usr/bin/pandoc"
    ), patch("subprocess.run") as mock_run:

        mock_run.return_value.returncode = 0

        res = ppt_converter._convert_pdf_to_md(input_path, output_path)

        # Verify Pandoc was called
        args, _ = mock_run.call_args
        assert args[0][0] == "/usr/bin/pandoc"
        assert str(input_path) in args[0]
        assert str(output_path) in args[0]
        assert res == output_path


def test_pdf_conversion_pandoc_fail_pdftotext_success(ppt_converter, tmp_path):
    """Test fallback to pdftotext when Pandoc fails"""
    input_path = tmp_path / "test.pdf"
    input_path.touch()
    output_path = tmp_path / "test.md"

    with patch(
        "src.core.converters.ppt.get_pandoc_path", return_value="/usr/bin/pandoc"
    ), patch("shutil.which", return_value="/usr/bin/pdftotext"), patch(
        "subprocess.run"
    ) as mock_run:

        # First call (Pandoc) raises error
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, ["pandoc"]),  # Pandoc fails
            MagicMock(returncode=0),  # pdftotext succeeds
        ]

        res = ppt_converter._convert_pdf_to_md(input_path, output_path)

        # Verify both were called
        assert mock_run.call_count == 2
        args_pandoc, _ = mock_run.call_args_list[0]
        args_pdftotext, _ = mock_run.call_args_list[1]

        assert args_pandoc[0][0] == "/usr/bin/pandoc"
        assert args_pdftotext[0][0] == "pdftotext"
        assert res == output_path


def test_pdf_conversion_all_cmds_fail_pdfminer_success(ppt_converter, tmp_path):
    """Test fallback to pdfminer when CLI tools fail"""
    input_path = tmp_path / "test.pdf"
    input_path.touch()
    output_path = tmp_path / "test.md"

    # We need to mock pdfminer.high_level.extract_text
    # Since it is imported inside the function, we patch it where it lives
    with patch(
        "src.core.converters.ppt.get_pandoc_path", return_value="/usr/bin/pandoc"
    ), patch("shutil.which", return_value="/usr/bin/pdftotext"), patch(
        "subprocess.run", side_effect=subprocess.CalledProcessError(1, "cmd")
    ), patch(
        "pdfminer.high_level.extract_text", return_value="Extracted text", create=True
    ):

        res = ppt_converter._convert_pdf_to_md(input_path, output_path)

        assert output_path.read_text(encoding="utf-8") == "Extracted text"
        assert res == output_path


def test_fallback_pdf_parsing_copy_on_failure(ppt_converter, tmp_path):
    """Test ultimate fallback to copying PDF if everything fails"""
    input_path = tmp_path / "test.pdf"
    input_path.touch()
    output_path = tmp_path / "test.md"

    # Mock extract_text to fail (ImportError or Exception)
    # Also mock shutil.copy to verify copy happens
    with patch(
        "pdfminer.high_level.extract_text", side_effect=ImportError, create=True
    ), patch("shutil.copy") as mock_copy:

        res = ppt_converter._fallback_pdf_parsing(input_path, output_path)

        expected_pdf_path = output_path.with_suffix(".pdf")
        mock_copy.assert_called_once_with(input_path, expected_pdf_path)
        assert res == expected_pdf_path
