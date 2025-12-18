import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import subprocess
import sys
# Try import pdfminer to verify environment
try:
    import pdfminer
except ImportError:
    pdfminer = None

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
            # Find --outdir index
            try:
                outdir_idx = cmd.index("--outdir")
                outdir = Path(cmd[outdir_idx + 1])
                (outdir / "test.pdf").write_text("dummy pdf", encoding="utf-8")
                return MagicMock(returncode=0)
            except ValueError:
                pass
        return MagicMock(returncode=0)

    mock_run.side_effect = side_effect

    converter.convert(input_file, output_file)

    assert mock_run.call_count == 2  # soffice + pandoc


@patch("src.core.converters.ppt.get_soffice_path")
def test_convert_ppt_no_soffice(mock_soffice, converter, tmp_path):
    mock_soffice.return_value = None
    input_file = tmp_path / "test.ppt"
    output_file = tmp_path / "test.md"

    with pytest.raises(RuntimeError, match="LibreOffice未安装"):
        converter.convert(input_file, output_file)


@patch("src.core.converters.ppt.log_info")
def test_convert_pptx_pptx2md(mock_log, converter, tmp_path):
    # This requires pptx2md importable or we mock the import?
    # The code tries to import pptx2md.
    # Since we likely don't have it in test env, it might raise ImportError
    # and fallback to LibreOffice logic.

    # We want to test the pptx2md path.
    # We need to mock sys.modules or the specific import in the function.

    input_file = tmp_path / "test.pptx"
    output_file = tmp_path / "test.md"

    # Mock the import check in _convert_pptx
    # We need to mock both pptx2md.entry and pptx2md.types
    mock_convert = MagicMock()
    mock_config_cls = MagicMock()
    
    modules = {
        "pptx2md": MagicMock(),
        "pptx2md.entry": MagicMock(convert=mock_convert),
        "pptx2md.types": MagicMock(ConversionConfig=mock_config_cls),
    }

    with patch.dict("sys.modules", modules):
        converter.convert(input_file, output_file)

        # Should call pptx2md.entry.convert
        mock_convert.assert_called_once()
        # Verify ConversionConfig was created with correct paths
        mock_config_cls.assert_called_once()
        args = mock_config_cls.call_args
        assert args.kwargs['pptx_path'] == input_file
        assert args.kwargs['output_path'] == output_file


def test_convert_pptx_import_fail_fallback(converter, tmp_path):
    # If import fails, it should fallback to _convert_ppt (LibreOffice)
    # We mock _convert_ppt to verify fallback

    input_file = tmp_path / "test.pptx"
    output_file = tmp_path / "test.md"

    with patch.object(converter, "_convert_ppt") as mock_fallback:
        # Force import error by ensuring it's not in sys.modules
        with patch.dict("sys.modules"):
            if "pptx2md" in sys.modules:
                del sys.modules["pptx2md"]

            converter.convert(input_file, output_file)
            mock_fallback.assert_called_once()


def test_run_subprocess_with_context(converter):
    context = MagicMock()
    cmd = ["echo", "test"]

    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (b"output", b"error")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        converter._run_subprocess(cmd, context=context, check=True)

        context.set_process.assert_called()
        assert context.set_process.call_count >= 2  # Once set, once cleared


def test_run_subprocess_with_context_failure(converter):
    context = MagicMock()
    cmd = ["echo", "fail"]

    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (b"output", b"error")
        mock_proc.returncode = 1
        mock_popen.return_value = mock_proc

        with pytest.raises(subprocess.CalledProcessError):
            converter._run_subprocess(cmd, context=context, check=True)


@patch("src.core.converters.ppt.get_soffice_path", return_value="/usr/bin/soffice")
def test_convert_ppt_libreoffice_timeout(mock_soffice, converter, tmp_path):
    input_file = tmp_path / "test.ppt"
    input_file.touch()
    output_file = tmp_path / "test.md"

    context = MagicMock()

    with patch.object(
        converter,
        "_run_subprocess",
        side_effect=subprocess.TimeoutExpired(cmd="soffice", timeout=120),
    ):
        with pytest.raises(RuntimeError, match="LibreOffice转换PDF超时"):
            converter.convert(input_file, output_file, context=context)


@patch("src.core.converters.ppt.get_soffice_path", return_value="/usr/bin/soffice")
def test_convert_ppt_libreoffice_silent_failure(mock_soffice, converter, tmp_path):
    input_file = tmp_path / "test.ppt"
    input_file.touch()
    output_file = tmp_path / "test.md"

    # Mock successful return code but NO PDF generated
    with patch.object(converter, "_run_subprocess") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b""
        mock_run.return_value.stderr = b""

        with pytest.raises(RuntimeError, match="未生成PDF文件"):
            converter.convert(input_file, output_file)


def test_pdf_to_md_no_pdftotext(converter, tmp_path):
    input_file = tmp_path / "test.pdf"
    input_file.touch()
    output_file = tmp_path / "test.md"

    with patch("src.core.converters.ppt.get_pandoc_path", return_value=None), patch(
        "shutil.which", return_value=None
    ), patch.object(converter, "_fallback_pdf_parsing") as mock_fallback:

        converter._convert_pdf_to_md(input_file, output_file)
        mock_fallback.assert_called_once()


def test_fallback_pdf_parsing_empty(converter, tmp_path):
    input_file = tmp_path / "test.pdf"
    input_file.touch()
    output_file = tmp_path / "test.md"

    # Mock pdfminer modules to avoid ImportErrors if not installed
    mock_pdfminer = MagicMock()
    mock_high_level = MagicMock()
    mock_high_level.extract_text.return_value = "   "
    
    modules = {
        "pdfminer": mock_pdfminer,
        "pdfminer.high_level": mock_high_level,
    }

    with patch.dict("sys.modules", modules), patch(
        "shutil.copy"
    ) as mock_copy:

        # We also need to patch where it's imported in the source if it uses 'from ... import ...'
        # But based on the error, the patch("pdfminer.high_level.extract_text") was failing to resolve.
        # Here we manually set up the mock so we don't need patch(target_string) which triggers import.
        # However, the code under test (converter._fallback_pdf_parsing) needs to import it.
        # If the code does `from pdfminer.high_level import extract_text`, it will use our mock in sys.modules.
        
        res = converter._fallback_pdf_parsing(input_file, output_file)

        # Should copy because text is empty/whitespace
        mock_copy.assert_called_once()
        assert res.suffix == ".pdf"


def test_fallback_pdf_parsing_exception(converter, tmp_path):
    input_file = tmp_path / "test.pdf"
    input_file.touch()
    output_file = tmp_path / "test.md"

    # Mock pdfminer modules
    mock_pdfminer = MagicMock()
    mock_high_level = MagicMock()
    mock_high_level.extract_text.side_effect = Exception("Boom")
    
    modules = {
        "pdfminer": mock_pdfminer,
        "pdfminer.high_level": mock_high_level,
    }

    with patch.dict("sys.modules", modules), patch("shutil.copy") as mock_copy:

        res = converter._fallback_pdf_parsing(input_file, output_file)

        mock_copy.assert_called_once()
        assert res.suffix == ".pdf"
