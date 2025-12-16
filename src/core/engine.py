import os
import logging
import threading
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import ConfigManager
from .converters.office import OfficeConverter
from .converters.ppt import PptConverter
from .utils import log_info, log_error, log_warn

class CancellationContext:
    def __init__(self):
        self.process = None # subprocess.Popen object
        self._lock = threading.Lock()
        
    def set_process(self, proc):
        with self._lock:
            self.process = proc
            
    def abort(self):
        with self._lock:
            if self.process:
                try:
                    log_info(f"强制终止子进程: {self.process.pid}")
                    # On Windows, use taskkill to kill process tree
                    if os.name == 'nt':
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.process.pid)], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    else:
                        self.process.kill() # Force kill
                except Exception as e:
                    log_warn(f"终止子进程失败: {e}")

class ConversionEngine:
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.office_converter = OfficeConverter()
        self.ppt_converter = PptConverter()
        self.stop_flag = False
        self.active_contexts = []
        self._lock = threading.Lock()

    def detect_type(self, path: Path):
        suffix = path.suffix.lower()
        if suffix in ['.docx', '.doc', '.xlsx', '.xls']:
            return 'office'
        elif suffix in ['.pptx', '.ppt']:
            return 'ppt'
        elif suffix == '.pdf':
            return 'pdf' # Treated as office in original logic
        elif suffix == '.txt':
            return 'text'
        return None

    def convert_file(self, input_path: Path, output_path: Path, status_callback=None, context=None):
        if self.stop_flag:
            return False

        if output_path.exists():
            log_info(f"跳过已存在的文件: {output_path}")
            if status_callback:
                status_callback(str(input_path), "skipped", "文件已存在")
            return output_path

        if status_callback:
            status_callback(str(input_path), "processing", "开始转换")

        file_type = self.detect_type(input_path)
        if not file_type:
            log_warn(f"不支持的文件类型: {input_path}")
            if status_callback:
                status_callback(str(input_path), "failed", "不支持的文件类型")
            return False

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            final_path = output_path
            if file_type == 'office':
                final_path = self.office_converter.convert(input_path, output_path, context=context)
            elif file_type in ['ppt', 'pdf']:
                final_path = self.ppt_converter.convert(input_path, output_path, context=context)
            elif file_type == 'text':
                import shutil
                shutil.copy(input_path, output_path)
                final_path = output_path
            
            if status_callback:
                status_callback(str(input_path), "success", "转换成功")
            return final_path
        except Exception as e:
            if self.stop_flag:
                log_warn(f"任务被取消: {input_path}")
                if status_callback:
                    status_callback(str(input_path), "cancelled", "用户取消")
            else:
                log_error(f"转换失败 {input_path}: {e}")
                if status_callback:
                    status_callback(str(input_path), "failed", str(e))
            return None

    def _run_task(self, input_path, output_path, status_callback):
        context = CancellationContext()
        with self._lock:
            self.active_contexts.append(context)
        try:
            return self.convert_file(input_path, output_path, status_callback, context)
        finally:
            with self._lock:
                if context in self.active_contexts:
                    self.active_contexts.remove(context)

    def run(self, input_path_str, output_path_str, progress_callback=None, file_converted_callback=None, status_callback=None):
        self.stop_flag = False
        with self._lock:
            self.active_contexts = []
            
        input_path = Path(input_path_str)
        output_path = Path(output_path_str)
        
        # 获取配置
        max_workers = int(self.config.get("max_parallel_jobs", 2))
        filters = self.config.get("file_filters", "docx,pptx,pdf,txt").split(',')
        filters = [f.strip().lower() for f in filters if f.strip()]
        # normalize filters (remove leading dot)
        filters = [f[1:] if f.startswith('.') else f for f in filters]

        # Determine target suffix based on output_format
        output_format = self.config.get("output_format", "markdown")
        target_suffix = ".md"
        if output_format == "html":
            target_suffix = ".html"
        elif output_format == "txt":
            target_suffix = ".txt"
        elif output_format == "pdf":
            target_suffix = ".pdf"

        tasks = []

        if input_path.is_file():
            # 单文件模式
            # 如果 output_path 是目录，则构造文件名
            if output_path.is_dir() or output_path_str.endswith(os.sep):
                 output_file = output_path / (input_path.stem + target_suffix)
            else:
                 output_file = output_path
            
            tasks.append((input_path, output_file))
        else:
            # 目录模式 (批量)
            for root, _, files in os.walk(input_path):
                for file in files:
                    file_path = Path(root) / file
                    ext = file_path.suffix.lower()[1:]
                    if ext in filters:
                        # 保持相对路径结构
                        rel_path = file_path.relative_to(input_path)
                        out_file = output_path / rel_path.with_suffix(target_suffix)
                        tasks.append((file_path, out_file))

        total = len(tasks)
        if total == 0:
            log_warn("没有找到需要转换的文件")
            return

        completed = 0
        
        log_info(f"开始转换，共 {total} 个文件，并行数: {max_workers}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self._run_task, inp, out, status_callback): inp 
                for inp, out in tasks
            }

            for future in as_completed(future_to_file):
                if self.stop_flag:
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                
                completed += 1
                if progress_callback:
                    progress_callback(completed, total)
                
                inp = future_to_file[future]
                try:
                    result_path = future.result()
                    if result_path and file_converted_callback:
                        file_converted_callback(str(result_path))
                except Exception as e:
                    log_error(f"任务异常 {inp}: {e}")

    def stop(self):
        self.stop_flag = True
        log_info("正在强制终止所有活动任务...")
        with self._lock:
            for ctx in self.active_contexts:
                ctx.abort()
