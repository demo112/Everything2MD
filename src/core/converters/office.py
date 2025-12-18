import subprocess
import tempfile
import os
import shutil
import re
import time
from pathlib import Path
from ..utils import get_soffice_path, get_pandoc_path, log_info, log_warn, log_error
from .base import BaseConverter
import sys


class OfficeConverter(BaseConverter):
    def _run_subprocess(self, cmd, context=None, **kwargs):
        """Helper to run subprocess with cancellation support"""
        if context:
            # Ensure output capturing is set if check=True or capture_output=True is implied
            # subprocess.run with capture_output=True sets stdout/stderr to PIPE
            if kwargs.pop("capture_output", False):
                kwargs["stdout"] = subprocess.PIPE
                kwargs["stderr"] = subprocess.PIPE

            # check parameter is handled manually
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
        soffice_path = get_soffice_path()
        pandoc_path = get_pandoc_path()

        if not soffice_path:
            if input_path.suffix.lower() == ".docx" and pandoc_path:
                log_warn(f"LibreOffice不可用，尝试使用Pandoc直接转换DOCX: {input_path}")
                self._convert_with_pandoc_direct(
                    input_path, output_path, pandoc_path, context=context
                )
                return output_path
            else:
                raise RuntimeError("LibreOffice未安装且无替代转换方案")

        # Validate paths
        if os.path.isdir(soffice_path):
            raise RuntimeError(
                f"配置的 LibreOffice 路径是一个目录，请指定 soffice.exe 文件路径: {soffice_path}"
            )

        if pandoc_path and os.path.isdir(pandoc_path):
            raise RuntimeError(
                f"配置的 Pandoc 路径是一个目录，请指定 pandoc.exe 文件路径: {pandoc_path}"
            )

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # 复制输入文件到临时目录
            safe_input = temp_dir_path / input_path.name

            # Retry logic for file copying
            copy_success = False
            last_error = None
            for i in range(5):
                try:
                    if safe_input.exists():
                        try:
                            os.chmod(safe_input, 0o777)
                            os.remove(safe_input)
                        except Exception:
                            pass
                    shutil.copy(input_path, safe_input)
                    copy_success = True
                    break
                except PermissionError as e:
                    last_error = e
                    log_warn(f"文件被占用，第 {i+1} 次重试: {input_path}")
                    time.sleep(1 + i)
                except Exception as e:
                    last_error = e
                    log_warn(f"复制文件失败，第 {i+1} 次重试: {e}")
                    time.sleep(1)

            if not copy_success:
                raise RuntimeError(
                    f"无法复制文件到临时目录 (重试5次后失败): {last_error}"
                )

            # 0. Check for PDF output
            if output_path.suffix.lower() == ".pdf":
                user_profile = temp_dir_path / "user_profile"
                cmd = [
                    soffice_path,
                    f"-env:UserInstallation=file:///{str(user_profile).replace(os.sep, '/')}",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(temp_dir_path),
                    str(safe_input),
                ]

                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self._run_subprocess(
                            cmd, context=context, check=True, capture_output=True
                        )
                        break
                    except subprocess.CalledProcessError as e:
                        err_msg = (
                            e.stderr.decode("utf-8", errors="ignore")
                            if e.stderr
                            else str(e)
                        )
                        if attempt < max_retries - 1:
                            log_warn(
                                f"LibreOffice PDF转换尝试 {attempt+1} 失败: {err_msg}，正在重试..."
                            )
                            time.sleep(2)
                        else:
                            raise RuntimeError(
                                f"LibreOffice PDF转换失败 (重试{max_retries}次后): {err_msg}"
                            )

                # Move PDF to output path
                # Expecting output file name to be same as input but with .pdf extension
                pdf_file = temp_dir_path / safe_input.with_suffix(".pdf").name
                if pdf_file.exists():
                    shutil.move(str(pdf_file), str(output_path))
                    log_info(f"成功转换Office文档: {input_path} -> {output_path}")
                    return output_path
                else:
                    raise RuntimeError(f"LibreOffice未生成PDF文件: {pdf_file}")

            # 1. LibreOffice -> HTML (增加重试机制)
            # 使用独立的用户配置目录以支持并发
            user_profile = temp_dir_path / "user_profile"
            cmd = [
                soffice_path,
                f"-env:UserInstallation=file:///{str(user_profile).replace(os.sep, '/')}",
                "--headless",
                "--convert-to",
                "html",
                "--outdir",
                str(temp_dir_path),
                str(safe_input),
            ]

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = self._run_subprocess(
                        cmd, context=context, check=True, capture_output=True
                    )
                    break  # Success
                except subprocess.CalledProcessError as e:
                    err_msg = (
                        e.stderr.decode("utf-8", errors="ignore")
                        if e.stderr
                        else str(e)
                    )
                    if attempt < max_retries - 1:
                        log_warn(
                            f"LibreOffice转换尝试 {attempt+1} 失败: {err_msg}，正在重试..."
                        )
                        time.sleep(2)  # Wait before retry
                    else:
                        raise RuntimeError(
                            f"LibreOffice转换失败 (重试{max_retries}次后): {err_msg}"
                        )

            # 查找生成的 HTML
            # LibreOffice 有时生成的 HTML 文件名可能与原文件名略有不同（例如替换空格）
            # 既然我们是复制进去的，应该是唯一的 html 文件
            html_files = list(temp_dir_path.glob("*.html"))
            if not html_files:
                # 尝试列出目录内容以辅助调试
                files_in_temp = list(temp_dir_path.glob("*"))
                raise RuntimeError(
                    f"LibreOffice未生成HTML文件。临时目录内容: {[f.name for f in files_in_temp]}"
                )

            html_file = html_files[0]

            # 2. HTML -> Markdown (via Pandoc)
            if pandoc_path:
                self._convert_html_to_md(
                    html_file, output_path, pandoc_path, context=context
                )
            else:
                # 无 Pandoc，直接输出 HTML
                shutil.copy(html_file, output_path)

            log_info(f"成功转换Office文档: {input_path} -> {output_path}")
            return output_path

    def _convert_with_pandoc_direct(
        self, input_path, output_path, pandoc_path, context=None
    ):
        cmd = [pandoc_path, str(input_path), "-o", str(output_path)]
        self._run_subprocess(cmd, context=context, check=True)

    def _convert_html_to_md(self, html_path, output_path, pandoc_path, context=None):
        if getattr(sys, "frozen", False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.parent.parent.parent

        lua_filter = base_path / "src" / "filters" / "clean.lua"

        cmd = [
            pandoc_path,
            "-f",
            "html",
            "-t",
            "gfm-raw_html",
            str(html_path),
            "-o",
            str(output_path),
        ]

        if lua_filter.exists():
            cmd.append("--lua-filter")
            cmd.append(str(lua_filter))
        else:
            log_warn(f"Lua filter not found at {lua_filter}")

        try:
            # Add encoding to subprocess for Windows Chinese path support
            # And use shell=False for safety, but check if env is needed
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            self._run_subprocess(
                cmd, context=context, check=True, capture_output=True, env=env
            )
        except subprocess.CalledProcessError as e:
            err_msg = e.stderr.decode("utf-8", errors="ignore") if e.stderr else str(e)
            # Exit 21 is Pandoc general error, often encoding or input file issue
            if e.returncode == 21:
                log_warn(
                    f"Pandoc Exit 21: 可能是输入文件编码问题或路径字符问题。尝试回退到无 Lua 过滤器的简单模式。"
                )
                # Retry without Lua filter as fallback
                cmd_fallback = [
                    c for c in cmd if "lua-filter" not in c and ".lua" not in c
                ]
                try:
                    self._run_subprocess(
                        cmd_fallback,
                        context=context,
                        check=True,
                        capture_output=True,
                        env=env,
                    )
                    return
                except subprocess.CalledProcessError as e2:
                    err_msg = (
                        e2.stderr.decode("utf-8", errors="ignore")
                        if e2.stderr
                        else str(e2)
                    )

            raise RuntimeError(
                f"Pandoc转换Markdown失败 (Exit {e.returncode}): {err_msg}"
            )

        # Post-processing cleanup (sed equivalent)
        if output_path.exists():
            try:
                content = output_path.read_text(encoding="utf-8")
                # 清理 span 和 div 标签
                content = re.sub(r"<span[^>]*>", "", content)
                content = re.sub(r"</span>", "", content)
                content = re.sub(r"<div[^>]*>", "", content)
                content = re.sub(r"</div>", "", content)
                output_path.write_text(content, encoding="utf-8")
            except Exception as e:
                log_warn(f"后处理清理失败: {e}")
