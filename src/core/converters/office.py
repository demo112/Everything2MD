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
    def convert(self, input_path: Path, output_path: Path, **kwargs):
        soffice_path = get_soffice_path()
        pandoc_path = get_pandoc_path()

        if not soffice_path:
            if input_path.suffix.lower() == '.docx' and pandoc_path:
                log_warn(f"LibreOffice不可用，尝试使用Pandoc直接转换DOCX: {input_path}")
                self._convert_with_pandoc_direct(input_path, output_path, pandoc_path)
                return
            else:
                raise RuntimeError("LibreOffice未安装且无替代转换方案")

        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # 复制输入文件到临时目录
            safe_input = temp_dir_path / input_path.name
            try:
                shutil.copy(input_path, safe_input)
            except PermissionError:
                # 如果文件被占用，尝试等待一下
                log_warn(f"文件可能被占用，重试复制: {input_path}")
                time.sleep(1)
                shutil.copy(input_path, safe_input)

            # 1. LibreOffice -> HTML (增加重试机制)
            cmd = [
                soffice_path,
                "--headless",
                "--convert-to", "html",
                "--outdir", str(temp_dir_path),
                str(safe_input)
            ]
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = subprocess.run(cmd, check=True, capture_output=True)
                    break # Success
                except subprocess.CalledProcessError as e:
                    err_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
                    if attempt < max_retries - 1:
                        log_warn(f"LibreOffice转换尝试 {attempt+1} 失败: {err_msg}，正在重试...")
                        time.sleep(2) # Wait before retry
                    else:
                        raise RuntimeError(f"LibreOffice转换失败 (重试{max_retries}次后): {err_msg}")

            # 查找生成的 HTML
            # LibreOffice 有时生成的 HTML 文件名可能与原文件名略有不同（例如替换空格）
            # 既然我们是复制进去的，应该是唯一的 html 文件
            html_files = list(temp_dir_path.glob("*.html"))
            if not html_files:
                # 尝试列出目录内容以辅助调试
                files_in_temp = list(temp_dir_path.glob("*"))
                raise RuntimeError(f"LibreOffice未生成HTML文件。临时目录内容: {[f.name for f in files_in_temp]}")
            
            html_file = html_files[0]

            # 2. HTML -> Markdown (via Pandoc)
            if pandoc_path:
                self._convert_html_to_md(html_file, output_path, pandoc_path)
            else:
                # 无 Pandoc，直接输出 HTML
                shutil.copy(html_file, output_path)

            log_info(f"成功转换Office文档: {input_path} -> {output_path}")

    def _convert_with_pandoc_direct(self, input_path, output_path, pandoc_path):
        cmd = [pandoc_path, str(input_path), "-o", str(output_path)]
        subprocess.run(cmd, check=True)

    def _convert_html_to_md(self, html_path, output_path, pandoc_path):
        if getattr(sys, 'frozen', False):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent.parent.parent.parent
            
        lua_filter = base_path / "src" / "filters" / "clean.lua"
        
        cmd = [
            pandoc_path,
            "-f", "html",
            "-t", "gfm-raw_html",
            str(html_path),
            "-o", str(output_path)
        ]
        
        if lua_filter.exists():
            cmd.insert(4, f"--lua-filter={lua_filter}")
        else:
            log_warn(f"Lua filter not found at {lua_filter}")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
             err_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
             raise RuntimeError(f"Pandoc转换Markdown失败: {err_msg}")

        # Post-processing cleanup (sed equivalent)
        if output_path.exists():
            try:
                content = output_path.read_text(encoding='utf-8')
                # 清理 span 和 div 标签
                content = re.sub(r'<span[^>]*>', '', content)
                content = re.sub(r'</span>', '', content)
                content = re.sub(r'<div[^>]*>', '', content)
                content = re.sub(r'</div>', '', content)
                output_path.write_text(content, encoding='utf-8')
            except Exception as e:
                log_warn(f"后处理清理失败: {e}")
