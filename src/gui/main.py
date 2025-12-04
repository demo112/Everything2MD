#!/usr/bin/env python3
"""
Everything2MD GUI主程序 (Python Native Refactored)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
import threading
import queue
import json
from pathlib import Path

# Add src to sys.path to allow imports
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from core.config import ConfigManager
    from core.engine import ConversionEngine
    from core.utils import setup_gui_logging, log_info
except ImportError as e:
    # Fallback for development environment structure differences
    sys.path.append(str(src_dir.parent))
    from src.core.config import ConfigManager
    from src.core.engine import ConversionEngine
    from src.core.utils import setup_gui_logging, log_info

class Everything2MDGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Everything2MD - 文档转换工具")
        self.root.geometry("700x600")
        
        # 初始化核心组件
        self.config_manager = ConfigManager()
        self.engine = ConversionEngine(self.config_manager)
        
        # 初始化变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.log_level = tk.StringVar(value="INFO")
        self.output_format = tk.StringVar(value="markdown")
        self.batch_processing = tk.BooleanVar(value=True)
        self.max_parallel_jobs = tk.StringVar(value="2")
        self.file_filters = tk.StringVar(value="docx,pptx,pdf,txt")
        self.soffice_path = tk.StringVar()
        
        self.is_converting = False
        
        # 日志队列
        self.log_queue = queue.Queue()
        setup_gui_logging(self.on_log_received)
        
        # 加载配置
        self.load_config()
        
        # 创建界面
        self.create_widgets()
        
        # 启动日志处理循环
        self.process_log_queue()
        
    def on_log_received(self, level, msg):
        self.log_queue.put((level, msg))
        
    def process_log_queue(self):
        while not self.log_queue.empty():
            try:
                level, msg = self.log_queue.get_nowait()
                self.append_log(level, msg)
            except queue.Empty:
                break
        self.root.after(100, self.process_log_queue)

    def append_log(self, level, msg):
        if not hasattr(self, 'status_text'): return
        
        self.status_text.configure(state='normal')
        tag = 'info'
        if level in ['ERROR', 'CRITICAL']: tag = 'error'
        elif level in ['WARNING', 'WARN']: tag = 'warn'
        
        self.status_text.insert(tk.END, f"[{level}] {msg}\n", tag)
        self.status_text.see(tk.END)
        self.status_text.configure(state='disabled')

    def create_widgets(self):
        # 主框架
        try:
            style = ttk.Style()
            style.theme_use('clam')
        except Exception:
            pass
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 输入选择
        ttk.Label(main_frame, text="输入路径:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.input_entry = ttk.Entry(main_frame, textvariable=self.input_path)
        self.input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        self.browse_input_button = ttk.Button(main_frame, text="浏览...", command=self.browse_input)
        self.browse_input_button.grid(row=0, column=2, pady=2)
        
        # 输出选择
        ttk.Label(main_frame, text="输出路径:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_path)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        self.browse_output_button = ttk.Button(main_frame, text="浏览...", command=self.browse_output)
        self.browse_output_button.grid(row=1, column=2, pady=2)
        
        # 参数配置
        config_frame = ttk.LabelFrame(main_frame, text="转换配置", padding="5")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        config_frame.columnconfigure(1, weight=1)
        
        # 日志级别
        ttk.Label(config_frame, text="日志级别:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.log_level_combo = ttk.Combobox(config_frame, textvariable=self.log_level, values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly")
        self.log_level_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        
        # 输出格式
        ttk.Label(config_frame, text="输出格式:").grid(row=0, column=2, sticky=tk.W, pady=2)
        self.output_format_combo = ttk.Combobox(config_frame, textvariable=self.output_format, values=["markdown", "html", "txt"], state="readonly")
        self.output_format_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=2)
        
        # 批量处理
        ttk.Label(config_frame, text="批量处理:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.batch_checkbox = ttk.Checkbutton(config_frame, text="启用", variable=self.batch_processing)
        self.batch_checkbox.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 并行任务数
        ttk.Label(config_frame, text="并行任务数:").grid(row=1, column=2, sticky=tk.W, pady=2)
        self.max_jobs_spinbox = ttk.Spinbox(config_frame, textvariable=self.max_parallel_jobs, from_=1, to=16, width=5)
        self.max_jobs_spinbox.grid(row=1, column=3, sticky=tk.W, pady=2)
        
        # 文件过滤器
        ttk.Label(config_frame, text="文件过滤器:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.file_filters_entry = ttk.Entry(config_frame, textvariable=self.file_filters)
        self.file_filters_entry.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2)

        # LibreOffice 路径
        ttk.Label(config_frame, text="LibreOffice:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.soffice_entry = ttk.Entry(config_frame, textvariable=self.soffice_path)
        self.soffice_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        self.browse_soffice_button = ttk.Button(config_frame, text="...", width=3, command=self.browse_soffice)
        self.browse_soffice_button.grid(row=3, column=3, sticky=tk.W, pady=2)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.save_config_button = ttk.Button(button_frame, text="保存配置", command=self.save_config)
        self.save_config_button.pack(side=tk.LEFT, padx=5)
        
        # 进度显示
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 状态显示
        self.status_text = tk.Text(main_frame, height=15, wrap=tk.WORD, state='disabled')
        self.status_text.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.tag_configure('error', foreground='red')
        self.status_text.tag_configure('warn', foreground='#FFA500') # Orange
        self.status_text.tag_configure('info', foreground='black')
        
        main_frame.rowconfigure(5, weight=1)
        self.status_bar = ttk.Label(main_frame, text="就绪", anchor='w')
        self.status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))

    def set_controls_disabled(self, disabled):
        state = tk.DISABLED if disabled else tk.NORMAL
        for w in [self.input_entry, self.output_entry, self.browse_input_button, 
                  self.browse_output_button, self.log_level_combo, self.output_format_combo,
                  self.batch_checkbox, self.max_jobs_spinbox, self.file_filters_entry,
                  self.save_config_button, self.soffice_entry, self.browse_soffice_button]:
            try:
                w.config(state=state)
            except Exception:
                pass

    def browse_input(self):
        initial_dir = self.input_path.get() if os.path.exists(self.input_path.get()) else os.path.expanduser("~")
        # Ask for file or directory? Python tkinter doesn't support both in one dialog easily.
        # Let's use askopenfilename by default, but if user wants batch, they might want directory.
        # The original app seemed to support both.
        # We'll use a simple dialog to ask user or just add a separate button? 
        # Original code: browse_input used askopenfilename.
        # But logic supported directory input.
        
        # Let's provide a way to choose directory.
        # Simple hack: If shift is held... no that's hidden.
        # Let's just stick to file for now, or maybe add a "Browse Folder" button?
        # For now, stick to file, but user can paste folder path.
        
        path = filedialog.askopenfilename(initialdir=initial_dir, title="选择输入文件")
        if not path:
            # If cancelled, maybe they wanted a folder?
            # Let's just use file for now to match original browse_input behavior
            pass
        else:
            self.input_path.set(path)
            
    def browse_output(self):
        initial_dir = self.output_path.get() if os.path.exists(self.output_path.get()) else os.path.expanduser("~")
        path = filedialog.askdirectory(initialdir=initial_dir, title="选择输出目录")
        if path:
            self.output_path.set(path)

    def browse_soffice(self):
        path = filedialog.askopenfilename(title="选择 LibreOffice (soffice.exe)", filetypes=[("Executable", "*.exe"), ("All Files", "*.*")])
        if path:
            self.soffice_path.set(path)

    def load_config(self):
        self.log_level.set(self.config_manager.get("log_level", "INFO"))
        self.output_format.set(self.config_manager.get("output_format", "markdown"))
        self.batch_processing.set(self.config_manager.get("batch_processing_enabled", "true") == "true")
        self.max_parallel_jobs.set(self.config_manager.get("max_parallel_jobs", "2"))
        self.file_filters.set(self.config_manager.get("file_filters", "docx,pptx,pdf,txt"))
        self.input_path.set(self.config_manager.get("last_input_path", ""))
        self.output_path.set(self.config_manager.get("last_output_path", ""))
        self.soffice_path.set(self.config_manager.get("soffice_path", ""))
        print("配置加载成功")

    def save_config(self):
        try:
            self.config_manager.set("log_level", self.log_level.get())
            self.config_manager.set("output_format", self.output_format.get())
            self.config_manager.set("batch_processing_enabled", self.batch_processing.get())
            self.config_manager.set("max_parallel_jobs", self.max_parallel_jobs.get())
            self.config_manager.set("file_filters", self.file_filters.get())
            self.config_manager.set("last_input_path", self.input_path.get())
            self.config_manager.set("last_output_path", self.output_path.get())
            self.config_manager.set("soffice_path", self.soffice_path.get())
            messagebox.showinfo("成功", "配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")

    def start_conversion(self):
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入路径")
            return
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出路径")
            return

        # 保存配置
        self.save_config()
        
        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.set_controls_disabled(True)
        self.is_converting = True
        
        self.status_text.configure(state='normal')
        self.status_text.delete(1.0, tk.END)
        self.status_text.configure(state='disabled')
        self.progress['value'] = 0
        self.progress['mode'] = 'indeterminate'
        self.progress.start()
        self.status_bar.config(text="运行中...")
        
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()

    def run_conversion(self):
        try:
            self.engine.run(
                self.input_path.get(),
                self.output_path.get(),
                progress_callback=self.update_progress
            )
        except Exception as e:
            log_info(f"Critical Error: {e}")
        finally:
            self.root.after(0, self.on_conversion_finished)

    def update_progress(self, current, total):
        self.root.after(0, lambda: self._update_progress_ui(current, total))
        
    def _update_progress_ui(self, current, total):
        self.progress.stop()
        self.progress['mode'] = 'determinate'
        self.progress['maximum'] = total
        self.progress['value'] = current
        self.status_bar.config(text=f"进度: {current}/{total}")

    def cancel_conversion(self):
        if self.is_converting:
            self.engine.stop()
            self.status_bar.config(text="正在取消...")

    def on_conversion_finished(self):
        self.is_converting = False
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.set_controls_disabled(False)
        self.progress.stop()
        self.status_bar.config(text="完成")
        messagebox.showinfo("完成", "转换任务结束")

if __name__ == "__main__":
    root = tk.Tk()
    app = Everything2MDGUI(root)
    root.mainloop()
