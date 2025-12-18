import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.core.converters.ppt import PptConverter
import subprocess


@pytest.fixture
def ppt_converter():
    return PptConverter()


def test_convert_pptx_with_pptx2md(ppt_converter):
    input_path = Path("test.pptx")
    output_path = Path("output.md")

    with patch.dict("sys.modules", {"pptx2md.entry": Mock(), "pptx2md.types": Mock()}):
        # We need to ensure import pptx2md works
        mock_convert = Mock()
        mock_config = Mock()

        with patch("src.core.converters.ppt.log_info") as mock_log:
            with patch("builtins.__import__") as mock_import:
                # This is hard to mock correctly for lazy imports inside methods without actually having the module.
                # A better way is to mock sys.modules directly or use patch.dict
                pass

    # Easier approach: Mock the internal _convert_pptx method for the main convert test,
    # and test _convert_pptx separately if possible, or just mock the imports inside it.

    with patch(
        "src.core.converters.ppt.PptConverter._convert_pptx"
    ) as mock_convert_pptx:
        ppt_converter.convert(input_path, output_path)
        mock_convert_pptx.assert_called_once_with(input_path, output_path, None)


def test_convert_ppt_libreoffice(ppt_converter):
    input_path = Path("test.ppt")
    output_path = Path(
        "output.md"
    )  # Note: ppt converter usually converts to pdf first or uses libreoffice to convert to pdf then pdf to md?
    # Wait, looking at code:
    # if suffix == '.pdf': _convert_pdf_to_md
    # else: _convert_ppt (which likely calls LibreOffice to PDF then PDF to MD)

    with patch("src.core.converters.ppt.PptConverter._convert_ppt") as mock_convert_ppt:
        ppt_converter.convert(input_path, output_path)
        mock_convert_ppt.assert_called_once_with(input_path, output_path, None)


def test_convert_fallback_logic(ppt_converter):
    # Test that if _convert_pptx fails, it logs warn and tries something else?
    # The code says:
    # try: _convert_pptx... except: log_warn... return _convert_ppt...

    input_path = Path("test.pptx")
    output_path = Path("output.md")

    with patch(
        "src.core.converters.ppt.PptConverter._convert_pptx",
        side_effect=Exception("Fail"),
    ):
        with patch(
            "src.core.converters.ppt.PptConverter._convert_ppt"
        ) as mock_convert_ppt:
            with patch("src.core.converters.ppt.log_warn") as mock_warn:
                ppt_converter.convert(input_path, output_path)

                mock_warn.assert_called()
                mock_convert_ppt.assert_called_once()


def test_run_subprocess(ppt_converter):
    # Test the _run_subprocess helper
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = Mock()
        mock_proc.communicate.return_value = (b"out", b"err")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        context = Mock()

        ppt_converter._run_subprocess(["ls"], context=context, check=True)

        context.set_process.assert_called()
        mock_popen.assert_called()
