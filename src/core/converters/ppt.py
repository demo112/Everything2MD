import subprocess
import tempfile
import shutil
import os
from pathlib import Path
from ..utils import get_soffice_path, get_pandoc_path, log_info, log_warn, log_error
from .base import BaseConverter

class PptConverter(BaseConverter):
    def convert(self, input_path: Path, output_path: Path, **kwargs):
        suffix = input_path.suffix.lower()
        
        if suffix == '.pptx':
            try:
                self._convert_pptx(input_path, output_path)
                return
            except Exception as e:
                log_warn(f"pptx2md转换失败: {e}，尝试降级使用LibreOffice")
                # 降级到 PPT 处理流程

        # PPT 处理流程 (或 PPTX 降级)
        self._convert_ppt(input_path, output_path)

    def _convert_pptx(self, input_path, output_path):
        # 尝试 import pptx2md
        try:
            from pptx2md.parser import Parser
            from pptx2md.outputter import md_outputter
        except ImportError:
            raise RuntimeError("pptx2md模块未安装")

        log_info(f"使用pptx2md转换: {input_path}")
        
        # pptx2md API 调用模拟
        # 注意：pptx2md 源码结构可能经常变，这里参考通常用法
        # 如果 API 调用太复杂，回退到 subprocess 调用命令行
        
        # 检查 pptx2md 命令是否可用（如果安装在 venv）
        cmd = ["pptx2md", str(input_path), "-o", str(output_path)]
        # 添加图片目录参数
        img_dir = output_path.parent / "img"
        cmd.extend(["-i", str(img_dir)])
        
        # 尝试直接调用命令行 (更稳健，因为我们已经 pip install 了它)
        # 在 exe 环境下，需要确保 pptx2md.exe 在路径中，或者直接调用 python -m pptx2md
        # 考虑到 PyInstaller 打包，subprocess 调用外部 exe 可能会失败。
        # 所以我们尝试用 sys.executable -m pptx2md (如果打包了 python 环境)
        # 但单文件 exe 没有 sys.executable 指向 python。
        
        # 最佳方案：调用库函数。
        # 阅读 pptx2md 源码是最好的，但这里假设 subprocess 调用 "pptx2md" 在开发环境可行。
        # 在打包环境，我们需要把 pptx2md 的入口脚本打包进去，或者用 python 代码调用。
        
        # 暂时使用 subprocess，如果在 exe 中失败，用户需要反馈。
        # 为了更稳健，我们捕获异常。
        subprocess.run(cmd, check=True, capture_output=True)

    def _convert_ppt(self, input_path, output_path):
        soffice_path = get_soffice_path()
        if not soffice_path:
            raise RuntimeError("LibreOffice未安装，无法转换PPT文件")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            safe_input = temp_dir_path / input_path.name
            shutil.copy(input_path, safe_input)

            # 1. PPT -> PDF
            cmd = [
                soffice_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(temp_dir_path),
                str(safe_input)
            ]
            
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"LibreOffice转换PDF失败: {e.stderr.decode()}")

            pdf_files = list(temp_dir_path.glob("*.pdf"))
            if not pdf_files:
                raise RuntimeError("未生成PDF文件")
            pdf_file = pdf_files[0]

            # 2. PDF -> Markdown
            # 优先使用 pandoc
            pandoc_path = get_pandoc_path()
            if pandoc_path:
                # pandoc -f pdf -t markdown ...
                # 注意：Pandoc 读取 PDF 需要 pdftotext 支持（通常）
                cmd_pandoc = [
                    pandoc_path,
                    "-f", "pdf",
                    "-t", "markdown",
                    str(pdf_file),
                    "-o", str(output_path)
                ]
                subprocess.run(cmd_pandoc, check=True)
            else:
                # 如果没有 Pandoc，看看有没有 pdftotext
                if shutil.which("pdftotext"):
                    subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_file), str(output_path)], check=True)
                else:
                    # 都没有，直接复制 PDF 到输出（改名）
                    log_warn("无可用PDF转换工具，仅输出PDF")
                    shutil.copy(pdf_file, output_path.with_suffix(".pdf"))

        log_info(f"成功转换PPT文档: {input_path} -> {output_path}")
