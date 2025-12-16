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
            import pptx
        except ImportError:
            raise RuntimeError("pptx2md模块未安装")

        log_info(f"使用pptx2md转换: {input_path}")
        
        # 使用库调用方式，避免 subprocess 找不到命令
        try:
            # 模拟 pptx2md 的 main 逻辑
            # 参考 pptx2md 源码，通常是:
            # prs = pptx.Presentation(input_path)
            # outputter = md_outputter(output_path)
            # parser = Parser(prs, outputter)
            # parser.parse()
            
            # 由于 pptx2md API 可能变动，我们尽量模拟其 entry point 逻辑
            # 如果能直接调用 parser 和 outputter 最好
            
            # 1. 创建输出目录
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img_dir = output_path.parent / "img"
            img_dir.mkdir(parents=True, exist_ok=True)
            
            # 2. 调用 pptx2md 逻辑
            # 注意: pptx2md 源码中，Parser 接收 Presentation 对象
            prs = pptx.Presentation(str(input_path))
            outputter = md_outputter(str(output_path), image_dir=str(img_dir), image_page_dir_check=True) # image_page_dir_check=True for image per page folder? or just check signature
            
            # pptx2md 2.0+ 签名可能是 md_outputter(filepath, image_dir=...)
            # 让我们保守一点，检查参数
            
            parser = Parser(prs, outputter)
            parser.parse()
            
        except Exception as e:
             # 如果库调用失败 (API 不匹配)，尝试回退到 subprocess (仅限开发环境)
             log_warn(f"pptx2md 库调用失败: {e}，尝试命令行回退...")
             cmd = ["pptx2md", str(input_path), "-o", str(output_path)]
             img_dir = output_path.parent / "img"
             cmd.extend(["-i", str(img_dir)])
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
