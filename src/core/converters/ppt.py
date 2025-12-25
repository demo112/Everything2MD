import subprocess
import tempfile
import shutil
import os
import sys
from pathlib import Path
from ..utils import get_soffice_path, get_pandoc_path, log_info, log_warn, log_error
from .base import BaseConverter


class PptConverter(BaseConverter):
    def _run_subprocess(self, cmd, context=None, **kwargs):
        """Helper to run subprocess with cancellation support"""
        if context:
            if kwargs.pop("capture_output", False):
                kwargs["stdout"] = subprocess.PIPE
                kwargs["stderr"] = subprocess.PIPE

            check = kwargs.pop("check", False)
            timeout = kwargs.pop("timeout", None)

            proc = subprocess.Popen(cmd, **kwargs)
            context.set_process(proc)
            try:
                stdout, stderr = proc.communicate(timeout=timeout)
                retcode = proc.returncode

                if check and retcode != 0:
                    raise subprocess.CalledProcessError(
                        retcode, cmd, output=stdout, stderr=stderr
                    )

                return subprocess.CompletedProcess(cmd, retcode, stdout, stderr)
            finally:
                context.set_process(None)
        else:
            return subprocess.run(cmd, **kwargs)

    def convert(
        self, input_path: Path, output_path: Path, context=None, **kwargs
    ) -> Path:
        suffix = input_path.suffix.lower()

        # Check for PDF output
        if output_path.suffix.lower() == ".pdf":
            if suffix == ".pdf":
                shutil.copy2(input_path, output_path)
                return output_path
            else:
                # PPT/PPTX -> PDF via LibreOffice
                return self._convert_ppt(
                    input_path, output_path, context, output_pdf_only=True
                )

        if suffix == ".pptx":
            try:
                self._convert_pptx(input_path, output_path, context)
                return output_path
            except Exception as e:
                log_warn(f"pptx2md转换失败: {e}，尝试降级使用LibreOffice")
                # 降级到 PPT 处理流程

        if suffix == ".pdf":
            return self._convert_pdf_to_md(input_path, output_path, context)

        # PPT 处理流程 (或 PPTX 降级)
        return self._convert_ppt(input_path, output_path, context)

    def _get_pptx2md_executable(self):
        """Find the pptx2md executable path"""
        # 1. Try finding in current python environment's Scripts (Windows) or bin (Linux)
        if os.name == 'nt':
            candidate = Path(sys.prefix) / "Scripts" / "pptx2md.exe"
        else:
            candidate = Path(sys.prefix) / "bin" / "pptx2md"
            
        if candidate.exists():
            return str(candidate)
            
        # 2. Fallback to PATH lookup
        path_exe = shutil.which("pptx2md")
        if path_exe:
            return path_exe
            
        return "pptx2md" # Last resort

    def _convert_pptx(self, input_path, output_path, context=None):
        """
        Convert PPTX using pptx2md.
        Prefer subprocess execution to support cancellation and isolation.
        """
        log_info(f"使用 pptx2md 转换: {input_path}")
        
        # Ensure output directories exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img_dir = output_path.parent / "img"
        img_dir.mkdir(parents=True, exist_ok=True)

        executable = self._get_pptx2md_executable()
        
        # Construct command
        # pptx2md [input] -o [output] -i [img_dir]
        cmd = [executable, str(input_path), "-o", str(output_path), "-i", str(img_dir)]
        
        try:
            # Use subprocess for cancellation support
            self._run_subprocess(cmd, context=context, check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            log_warn(f"pptx2md 命令行调用失败: {e}，尝试 Python 库调用作为回退...")
            
            # Fallback to library call (blocking, not cancellable)
            try:
                from pptx2md.entry import convert as pptx_convert
                from pptx2md.types import ConversionConfig
                
                config = ConversionConfig(
                    pptx_path=input_path,
                    output_path=output_path,
                    image_dir=img_dir,
                    title_path=None,
                    image_width=None,
                    disable_image=False,
                    disable_wmf=False,
                    disable_color=False,
                    disable_escaping=False,
                    disable_notes=False,
                    enable_slides=False,
                    try_multi_column=False,
                    is_wiki=False,
                    is_mdk=False,
                    is_qmd=False,
                    min_block_size=15,
                    page=None,
                    keep_similar_titles=False,
                )
                pptx_convert(config)
            except ImportError:
                raise RuntimeError("pptx2md模块未安装")
            except Exception as lib_e:
                raise RuntimeError(f"pptx2md 转换失败: {lib_e}")

    def _convert_ppt(
        self, input_path, output_path, context=None, output_pdf_only=False
    ):
        soffice_path = get_soffice_path()
        if not soffice_path:
            raise RuntimeError("LibreOffice未安装，无法转换PPT文件")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            safe_input = temp_dir_path / input_path.name
            shutil.copy(input_path, safe_input)

            # 1. PPT -> PDF
            # 使用独立的用户配置目录，避免并发冲突或锁文件问题
            user_profile_dir = temp_dir_path / "user_profile"
            user_profile_url = f"file:///{str(user_profile_dir).replace(os.sep, '/')}"

            cmd = [
                soffice_path,
                f"-env:UserInstallation={user_profile_url}",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(temp_dir_path),
                str(safe_input),
            ]

            try:
                # 增加超时机制，防止假死
                # Note: With Popen and context, timeout is trickier if we want to support both cancellation AND timeout.
                # subprocess.run supports timeout. Popen.communicate supports timeout.
                # Here we use _run_subprocess which uses Popen.communicate.
                # We can pass timeout to it.

                result = self._run_subprocess(
                    cmd, context=context, check=False, capture_output=True, timeout=120
                )
                if result.returncode != 0:
                    raise RuntimeError(
                        f"LibreOffice转换PDF失败 (Exit Code {result.returncode}): {result.stderr.decode() or result.stdout.decode()}"
                    )
            except subprocess.TimeoutExpired:
                raise RuntimeError("LibreOffice转换PDF超时")
            except Exception as e:
                raise RuntimeError(f"LibreOffice启动失败: {e}")

            pdf_files = list(temp_dir_path.glob("*.pdf"))
            if not pdf_files:
                # 记录更多调试信息
                log_warn(
                    f"LibreOffice执行结束但未生成PDF。Stdout: {result.stdout.decode()} Stderr: {result.stderr.decode()}"
                )
                raise RuntimeError("未生成PDF文件")
            pdf_file = pdf_files[0]

            if output_pdf_only:
                shutil.move(str(pdf_file), str(output_path))
                return output_path

            # 2. PDF -> Markdown
            return self._convert_pdf_to_md(pdf_file, output_path, context)

    def _convert_pdf_to_md(
        self, pdf_file: Path, output_path: Path, context=None
    ) -> Path:
        # 优先使用 pandoc
        pandoc_path = get_pandoc_path()
        pandoc_success = False

        if pandoc_path:
            # pandoc -f pdf -t markdown ...
            # 注意：Pandoc 读取 PDF 需要 pdftotext 支持（通常）
            cmd_pandoc = [
                pandoc_path,
                "-f",
                "pdf",
                "-t",
                "markdown",
                str(pdf_file),
                "-o",
                str(output_path),
            ]
            try:
                self._run_subprocess(
                    cmd_pandoc, context=context, check=True, capture_output=True
                )
                pandoc_success = True
            except subprocess.CalledProcessError as e:
                log_warn(f"Pandoc 转换 PDF 失败: {e}，尝试使用 pdftotext")

        if not pandoc_success:
            # 如果没有 Pandoc 或 Pandoc 失败，看看有没有 pdftotext
            if shutil.which("pdftotext"):
                try:
                    self._run_subprocess(
                        [
                            "pdftotext",
                            "-layout",
                            "-enc",
                            "UTF-8",
                            str(pdf_file),
                            str(output_path),
                        ],
                        context=context,
                        check=True,
                    )
                except subprocess.CalledProcessError as e:
                    log_warn(f"pdftotext 转换失败: {e}")
                    # 尝试 Python 原生解析
                    return self._fallback_pdf_parsing(pdf_file, output_path)
            else:
                log_warn("未找到 pdftotext，尝试使用 Python 原生解析")
                return self._fallback_pdf_parsing(pdf_file, output_path)

        log_info(f"成功转换文档: {pdf_file} -> {output_path}")
        return output_path

    def _fallback_pdf_parsing(self, pdf_file: Path, output_path: Path) -> Path:
        """使用 Python 库解析 PDF (最后一道防线)"""
        try:
            from pdfminer.high_level import extract_text

            text = extract_text(str(pdf_file))
            if not text or not text.strip():
                raise ValueError("未提取到文本")

            output_path.write_text(text, encoding="utf-8")
            log_info(f"使用 pdfminer 成功提取文本: {pdf_file}")
            return output_path
        except ImportError:
            log_warn("pdfminer.six 未安装，跳过 Python 原生解析")
        except Exception as e:
            log_warn(f"Python 原生解析失败: {e}")

        # 最后的最后：复制 PDF
        log_warn("无可用转换工具，仅输出PDF")
        target_pdf = output_path.with_suffix(".pdf")
        shutil.copy(pdf_file, target_pdf)
        return target_pdf
