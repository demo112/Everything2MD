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
    from core.utils import setup_gui_logging, log_info, log_error
    from core.ragflow_client import RAGFlowClient
except ImportError as e:
    # Fallback for development environment structure differences
    sys.path.append(str(src_dir.parent))
    from src.core.config import ConfigManager
    from src.core.engine import ConversionEngine
    from src.core.utils import setup_gui_logging, log_info, log_error
    from src.core.ragflow_client import RAGFlowClient

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
        
        # RAGFlow 变量
        self.rag_api_base = tk.StringVar(value="http://localhost:9380")
        self.rag_api_key = tk.StringVar()
        self.ragflow_client = None
        self.kb_list = []
        self.selected_kb_id = tk.StringVar()
        self.converted_files = [] # List of dicts
        
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
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Tab 1: Conversion
        self.convert_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.convert_frame, text='转换控制')
        self.init_convert_tab(self.convert_frame)
        
        # Tab 2: RAGFlow
        self.rag_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.rag_frame, text='分发中心')
        self.init_rag_tab(self.rag_frame)
        
        # Check for auto-connect on startup
        self.root.after(1000, self.auto_connect_rag)

    def auto_connect_rag(self):
        if self.rag_api_base.get() and self.rag_api_key.get():
            log_info("尝试自动连接 RAGFlow...")
            self.refresh_kb_list()

    def init_convert_tab(self, parent):
        # 主框架 (Using parent)
        try:
            style = ttk.Style()
            style.theme_use('vista')
        except Exception:
            pass
        
        # 配置网格权重
        parent.columnconfigure(1, weight=1)
        
        # 输入选择
        ttk.Label(parent, text="输入路径:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.input_entry = ttk.Entry(parent, textvariable=self.input_path)
        self.input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=0, column=2, pady=2)
        self.browse_input_button = ttk.Button(btn_frame, text="选择文件", width=10, command=self.browse_input)
        self.browse_input_button.pack(side=tk.LEFT, padx=2)
        self.browse_input_dir_button = ttk.Button(btn_frame, text="选择目录", width=10, command=self.browse_input_dir)
        self.browse_input_dir_button.pack(side=tk.LEFT, padx=2)
        
        # 输出选择
        ttk.Label(parent, text="输出路径:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_entry = ttk.Entry(parent, textvariable=self.output_path)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        self.browse_output_button = ttk.Button(parent, text="浏览...", command=self.browse_output)
        self.browse_output_button.grid(row=1, column=2, pady=2)
        
        # 参数配置
        config_frame = ttk.LabelFrame(parent, text="转换配置", padding="5")
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
        ttk.Label(config_frame, text="文件过滤器:").grid(row=2, column=0, sticky=tk.NW, pady=2)
        
        # Filter Frame
        filter_container = ttk.Frame(config_frame)
        filter_container.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        
        # Scan Button
        self.scan_button = ttk.Button(filter_container, text="扫描类型", command=self.scan_file_types)
        self.scan_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Checkboxes Frame
        self.filter_checks_frame = ttk.Frame(filter_container)
        self.filter_checks_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dictionary to hold checkbox variables: {ext: BooleanVar}
        self.filter_vars = {}
        # Initial population based on default config
        self.refresh_filter_checkboxes(self.file_filters.get().split(','))

        # LibreOffice 路径
        ttk.Label(config_frame, text="LibreOffice:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.soffice_entry = ttk.Entry(config_frame, textvariable=self.soffice_path)
        self.soffice_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        self.browse_soffice_button = ttk.Button(config_frame, text="...", width=3, command=self.browse_soffice)
        self.browse_soffice_button.grid(row=3, column=3, sticky=tk.W, pady=2)
        
        # 操作按钮
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.save_config_button = ttk.Button(button_frame, text="保存配置", command=self.save_config)
        self.save_config_button.pack(side=tk.LEFT, padx=5)
        
        # 进度显示
        self.progress = ttk.Progressbar(parent, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 文件状态列表 (新增)
        list_frame = ttk.LabelFrame(parent, text="文件状态", padding="5")
        list_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        parent.rowconfigure(5, weight=2) # Give more weight to list
        
        columns = ('file', 'status', 'message')
        self.file_status_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.file_status_tree.heading('file', text='文件名')
        self.file_status_tree.heading('status', text='状态')
        self.file_status_tree.heading('message', text='信息')
        self.file_status_tree.column('file', width=300)
        self.file_status_tree.column('status', width=80)
        self.file_status_tree.column('message', width=200)
        
        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_status_tree.yview)
        self.file_status_tree.configure(yscrollcommand=list_scroll.set)
        
        self.file_status_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 状态显示 (日志)
        log_frame = ttk.LabelFrame(parent, text="运行日志", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        parent.rowconfigure(6, weight=1)

        self.status_text = tk.Text(log_frame, height=8, wrap=tk.WORD, state='disabled')
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.tag_configure('error', foreground='red')
        self.status_text.tag_configure('warn', foreground='#FFA500') # Orange
        self.status_text.tag_configure('info', foreground='black')
        
        self.status_bar = ttk.Label(parent, text="就绪", anchor='w')
        self.status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E))

    def set_controls_disabled(self, disabled):
        state = tk.DISABLED if disabled else tk.NORMAL
        for w in [self.input_entry, self.output_entry, self.browse_input_button, 
                  self.browse_output_button, self.browse_input_dir_button,
                  self.log_level_combo, self.output_format_combo,
                  self.batch_checkbox, self.max_jobs_spinbox, self.scan_button,
                  self.save_config_button, self.soffice_entry, self.browse_soffice_button]:
            try:
                w.config(state=state)
            except Exception:
                pass
        
        # Disable checkboxes
        for cb in self.filter_checks_frame.winfo_children():
            try:
                cb.config(state=state)
            except Exception:
                pass

    def browse_input(self):
        initial_dir = self.input_path.get() if os.path.exists(self.input_path.get()) else os.path.expanduser("~")
        if os.path.isfile(initial_dir):
            initial_dir = os.path.dirname(initial_dir)
            
        path = filedialog.askopenfilename(initialdir=initial_dir, title="选择输入文件")
        if path:
            self.input_path.set(path)
            
    def browse_input_dir(self):
        initial_dir = self.input_path.get() if os.path.exists(self.input_path.get()) else os.path.expanduser("~")
        if os.path.isfile(initial_dir):
            initial_dir = os.path.dirname(initial_dir)
            
        path = filedialog.askdirectory(initialdir=initial_dir, title="选择输入目录")
        if path:
            self.input_path.set(path)
            # Auto scan when dir is selected
            self.root.after(100, self.scan_file_types)

    def scan_file_types(self):
        path = self.input_path.get()
        if not path or not os.path.isdir(path):
            if not path:
                return # Fail silently if empty
            # If it's a file, just set that extension
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lstrip('.').lower()
                if ext:
                    self.refresh_filter_checkboxes([ext], {ext: 1})
            return

        # Scan directory in background to avoid freezing UI
        self.status_bar.config(text="正在扫描文件类型...")
        def _scan():
            extensions = {}
            try:
                for root, _, files in os.walk(path):
                    for file in files:
                        ext = os.path.splitext(file)[1].lstrip('.').lower()
                        if ext:
                            extensions[ext] = extensions.get(ext, 0) + 1
            except Exception as e:
                log_error(f"Scan failed: {e}")
                self.root.after(0, lambda: self.status_bar.config(text="扫描失败"))
                return
            
            # Update UI
            self.root.after(0, lambda: [self.refresh_filter_checkboxes(list(extensions.keys()), extensions), self.status_bar.config(text="扫描完成")])
            
        threading.Thread(target=_scan, daemon=True).start()

    def refresh_filter_checkboxes(self, extensions, counts=None):
        # Clear existing
        for widget in self.filter_checks_frame.winfo_children():
            widget.destroy()
        
        self.filter_vars = {}
        
        # Current active filters from config
        current_filters = [f.strip() for f in self.file_filters.get().split(',') if f.strip()]
        
        # Sort extensions
        extensions = sorted([e for e in extensions if e]) # remove empty
        
        # Create checkboxes
        # Layout: Grid with 4 columns
        col = 0
        row = 0
        max_cols = 4
        
        for ext in extensions:
            count_str = f" ({counts[ext]})" if counts and ext in counts else ""
            label = f".{ext}{count_str}"
            
            var = tk.BooleanVar()
            # Default check if in current config OR if config is empty/default
            if not current_filters or ext in current_filters:
                var.set(True)
            else:
                var.set(False)
            
            self.filter_vars[ext] = var
            
            cb = ttk.Checkbutton(self.filter_checks_frame, text=label, variable=var, 
                                command=self.update_filter_string)
            cb.grid(row=row, column=col, sticky='w', padx=2)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Update the string var immediately
        self.update_filter_string()

    def update_filter_string(self):
        selected = [ext for ext, var in self.filter_vars.items() if var.get()]
        self.file_filters.set(",".join(selected))

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
        self.input_path.set(self.config_manager.get("last_input_path", ""))
        self.output_path.set(self.config_manager.get("last_output_path", ""))
        self.soffice_path.set(self.config_manager.get("soffice_path", ""))
        
        self.log_level.set(self.config_manager.get("log_level", "INFO"))
        self.output_format.set(self.config_manager.get("output_format", "markdown"))
        self.batch_processing.set(self.config_manager.get("batch_processing_enabled", "true") == "true")
        self.max_parallel_jobs.set(self.config_manager.get("max_parallel_jobs", "2"))
        self.file_filters.set(self.config_manager.get("file_filters", "docx,pptx,pdf,txt"))
        
        # Load RAGFlow config
        self.rag_api_base.set(self.config_manager.get("rag_api_base", "http://localhost:9380"))
        self.rag_api_key.set(self.config_manager.get("rag_api_key", ""))

    def save_config(self):
        # Save GUI settings to ConfigManager
        self.config_manager.set("last_input_path", self.input_path.get())
        self.config_manager.set("last_output_path", self.output_path.get())
        self.config_manager.set("soffice_path", self.soffice_path.get())
        
        self.config_manager.set("log_level", self.log_level.get())
        self.config_manager.set("output_format", self.output_format.get())
        self.config_manager.set("batch_processing_enabled", str(self.batch_processing.get()).lower())
        self.config_manager.set("max_parallel_jobs", self.max_parallel_jobs.get())
        self.config_manager.set("file_filters", self.file_filters.get())
        
        # Save RAGFlow config
        self.config_manager.set("rag_api_base", self.rag_api_base.get())
        self.config_manager.set("rag_api_key", self.rag_api_key.get())
        
        self.config_manager.save_config()

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
        
        # Clear status tree
        for item in self.file_status_tree.get_children():
            self.file_status_tree.delete(item)
            
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
                progress_callback=self.update_progress,
                file_converted_callback=self.on_file_converted,
                status_callback=self.update_file_status
            )
        except Exception as e:
            log_info(f"Critical Error: {e}")
        finally:
            self.root.after(0, self.on_conversion_finished)

    def update_file_status(self, file_path, status, message):
        self.root.after(0, lambda: self._update_file_status_ui(file_path, status, message))

    def _update_file_status_ui(self, file_path, status, message):
        # Find item in tree
        fname = os.path.basename(file_path)
        found = None
        for item in self.file_status_tree.get_children():
            if self.file_status_tree.item(item, "values")[0] == fname:
                found = item
                break
        
        if found:
            self.file_status_tree.set(found, column="status", value=status)
            self.file_status_tree.set(found, column="message", value=message)
        else:
            self.file_status_tree.insert('', 'end', values=(fname, status, message))
        
        # Scroll to bottom if new or updated
        if found:
            self.file_status_tree.see(found)
        else:
            children = self.file_status_tree.get_children()
            if children:
                self.file_status_tree.see(children[-1])

    def update_progress(self, current, total):
        self.root.after(0, lambda: self._update_progress_ui(current, total))

    def _update_progress_ui(self, current, total):
        if self.progress['mode'] == 'indeterminate':
            self.progress['mode'] = 'determinate'
            self.progress['maximum'] = total
        self.progress['value'] = current
        self.status_bar.config(text=f"进度: {current}/{total}")

    def on_file_converted(self, file_path):
        """Callback when a file is converted"""
        self.root.after(0, lambda: self._add_to_rag_list(file_path))

    def _add_to_rag_list(self, file_path):
        # Add to internal list
        fname = os.path.basename(file_path)
        item = {
            "path": file_path,
            "name": fname,
            "status": "Ready", # Ready, Uploading, Done, Failed
            "id": ""
        }
        self.converted_files.append(item)
        
        # Add to Treeview
        # Check if already exists?
        # For simplicity, just append.
        # Use [x] for selected by default
        self.rag_file_list.insert('', 'end', values=("[x]", fname, "转换完成", "未上传"))

    def init_rag_tab(self, parent):
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1) # List area

        # 1. Config Area
        cfg_frame = ttk.LabelFrame(parent, text="RAGFlow 配置", padding="5")
        cfg_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=5)
        cfg_frame.columnconfigure(1, weight=1)

        ttk.Label(cfg_frame, text="API Base URL:").grid(row=0, column=0, sticky='w')
        ttk.Entry(cfg_frame, textvariable=self.rag_api_base).grid(row=0, column=1, sticky='ew', padx=5)
        
        ttk.Label(cfg_frame, text="API Key:").grid(row=1, column=0, sticky='w')
        ttk.Entry(cfg_frame, textvariable=self.rag_api_key, show="*").grid(row=1, column=1, sticky='ew', padx=5)
        
        ttk.Button(cfg_frame, text="连接/刷新KB", command=self.refresh_kb_list).grid(row=1, column=2)

        # 2. Control Area
        ctrl_frame = ttk.Frame(parent, padding="5")
        ctrl_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(ctrl_frame, text="目标知识库:").pack(side='left')
        self.kb_combo = ttk.Combobox(ctrl_frame, textvariable=self.selected_kb_id, state="readonly", width=30)
        self.kb_combo.pack(side='left', padx=5)
        
        ttk.Button(ctrl_frame, text="新建KB...", command=self.show_new_kb_dialog).pack(side='left', padx=5)
        ttk.Button(ctrl_frame, text="上传选中文件", command=self.upload_selected_files).pack(side='right', padx=5)
        ttk.Button(ctrl_frame, text="全选/反选", command=self.toggle_all_selection).pack(side='right', padx=5)

        # 3. List Area
        list_frame = ttk.Frame(parent)
        list_frame.grid(row=2, column=0, columnspan=2, sticky='nsew')
        
        columns = ('select', 'name', 'convert_status', 'upload_status')
        self.rag_file_list = ttk.Treeview(list_frame, columns=columns, show='headings', selectmode='browse')
        self.rag_file_list.heading('select', text='选择')
        self.rag_file_list.heading('name', text='文件名')
        self.rag_file_list.heading('convert_status', text='转换状态')
        self.rag_file_list.heading('upload_status', text='上传状态')
        
        self.rag_file_list.column('select', width=50, anchor='center')
        self.rag_file_list.column('name', width=300)
        self.rag_file_list.column('convert_status', width=100)
        self.rag_file_list.column('upload_status', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.rag_file_list.yview)
        self.rag_file_list.configure(yscrollcommand=scrollbar.set)
        
        self.rag_file_list.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind click for checkbox
        self.rag_file_list.bind('<Button-1>', self.on_rag_list_click)

    def on_rag_list_click(self, event):
        region = self.rag_file_list.identify("region", event.x, event.y)
        if region == "heading":
            return
            
        col = self.rag_file_list.identify_column(event.x)
        item_id = self.rag_file_list.identify_row(event.y)
        
        if col == '#1' and item_id: # '#1' corresponds to the first column 'select'
            # Toggle check
            current_val = self.rag_file_list.set(item_id, 'select')
            new_val = "[ ]" if "[x]" in current_val else "[x]"
            self.rag_file_list.set(item_id, 'select', value=new_val)

    def toggle_all_selection(self):
        # Toggle all based on first item
        children = self.rag_file_list.get_children()
        if not children: return
        
        first_val = self.rag_file_list.set(children[0], 'select')
        new_val = "[ ]" if "[x]" in first_val else "[x]"
        
        for item in children:
            self.rag_file_list.set(item, 'select', value=new_val)

    def refresh_kb_list(self):
        base_url = self.rag_api_base.get()
        api_key = self.rag_api_key.get()
        if not base_url or not api_key:
            messagebox.showerror("错误", "请先配置 API URL 和 Key")
            return
            
        self.status_bar.config(text="正在刷新知识库列表...")
        def _do_refresh():
            try:
                if not self.ragflow_client:
                    self.ragflow_client = RAGFlowClient(base_url, api_key)
                
                # Update headers in case key changed
                self.ragflow_client.headers["Authorization"] = f"Bearer {api_key}"
                self.ragflow_client.base_url = base_url.rstrip('/')

                data = self.ragflow_client.list_datasets()
                # data is list of dicts. Assume structure [{'id': '...', 'name': '...'}, ...]
                # Need to verify RAGFlow API structure. 
                # Assuming data is the list itself or data['data']
                # My client returns data.get('data').
                
                kbs = []
                self.kb_map = {} # name -> id
                if isinstance(data, list):
                    for item in data:
                        name = item.get('name', 'Unknown')
                        kid = item.get('id', '')
                        kbs.append(name)
                        self.kb_map[name] = kid
                
                self.root.after(0, lambda: self.kb_combo.config(values=kbs))
                if kbs:
                    self.root.after(0, lambda: self.kb_combo.current(0))
                
                log_info("知识库列表刷新成功")
                self.root.after(0, lambda: self.status_bar.config(text="知识库列表刷新成功"))
            except Exception as e:
                log_info(f"刷新失败: {e}")
                self.root.after(0, lambda: [messagebox.showerror("错误", f"刷新失败: {e}"), self.status_bar.config(text="刷新失败")])

        threading.Thread(target=_do_refresh, daemon=True).start()
        # Save RAG config on refresh action too
        self.save_config()

    def show_new_kb_dialog(self):
        # Simple dialog to get name and optional template
        # Since tkinter simpledialog is limited, we'll make a Toplevel
        top = tk.Toplevel(self.root)
        top.title("新建知识库")
        
        ttk.Label(top, text="知识库名称:").grid(row=0, column=0, padx=5, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(top, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="模板 (可选):").grid(row=1, column=0, padx=5, pady=5)
        tpl_var = tk.StringVar()
        # Use existing KB list
        kbs = self.kb_combo['values']
        ttk.Combobox(top, textvariable=tpl_var, values=kbs).grid(row=1, column=1, padx=5, pady=5)
        
        def _create():
            name = name_var.get()
            if not name: return
            
            # Logic to create
            tpl_name = tpl_var.get()
            tpl_id = self.kb_map.get(tpl_name) if hasattr(self, 'kb_map') else None
            
            def _bg_create():
                try:
                    self.ragflow_client.create_dataset(name, tpl_id)
                    self.root.after(0, lambda: [top.destroy(), self.refresh_kb_list()])
                    log_info(f"知识库 {name} 创建成功")
                except Exception as e:
                    log_info(f"创建失败: {e}")
            
            threading.Thread(target=_bg_create, daemon=True).start()
            
        ttk.Button(top, text="创建", command=_create).grid(row=2, column=0, columnspan=2, pady=10)

    def upload_selected_files(self):
        # selected_items = self.rag_file_list.selection() # Old way
        # New way: iterate all and check column 0
        children = self.rag_file_list.get_children()
        selected_items = []
        for item in children:
            if "[x]" in self.rag_file_list.set(item, 'select'):
                selected_items.append(item)
                
        if not selected_items:
            messagebox.showinfo("提示", "请先在列表中勾选要上传的文件")
            return
            
        kb_name = self.kb_combo.get()
        if not kb_name:
            messagebox.showerror("错误", "请选择目标知识库")
            return
            
        kb_id = self.kb_map.get(kb_name)
        if not kb_id:
            return

        # Prepare list
        files_to_upload = []
        for iid in selected_items:
            vals = self.rag_file_list.item(iid)['values']
            fname = vals[1] # Column 0 is checkbox, 1 is name
            # Find full path from self.converted_files
            # This is O(N), but list is small.
            for f in self.converted_files:
                if f['name'] == fname:
                    files_to_upload.append((iid, f))
                    break
        
        def _bg_upload():
            self.root.after(0, lambda: self.status_bar.config(text="正在获取知识库文档列表..."))
            
            # Fetch existing documents for deduplication
            existing_docs = set()
            try:
                # Fetch all docs (or at least first page with keywords search in future optimization)
                # For now, we list first 1000? Or just iterate. 
                # Assuming not too many files.
                res = self.ragflow_client.list_documents(kb_id, page=1, page_size=1000)
                if isinstance(res, dict) and 'docs' in res:
                    for doc in res['docs']:
                        existing_docs.add(doc.get('name'))
                # Handle list response if structure differs
                elif isinstance(res, list):
                     for doc in res:
                        existing_docs.add(doc.get('name'))
            except Exception as e:
                log_warn(f"Failed to list documents for deduplication: {e}")
                # Continue without deduplication? Or stop? 
                # Let's continue but log warning.
            
            self.root.after(0, lambda: self.status_bar.config(text=f"正在上传 {len(files_to_upload)} 个文件..."))
            success_count = 0
            fail_count = 0
            skip_count = 0
            
            for iid, f_obj in files_to_upload:
                if f_obj['name'] in existing_docs:
                    log_info(f"跳过已存在的文件: {f_obj['name']}")
                    self.root.after(0, lambda i=iid: self.rag_file_list.set(i, column='upload_status', value='跳过(已存在)'))
                    skip_count += 1
                    continue

                try:
                    self.root.after(0, lambda i=iid: self.rag_file_list.set(i, column='upload_status', value='上传中...'))
                    
                    # Upload
                    res = self.ragflow_client.upload_document(kb_id, f_obj['path'])
                    
                    # Extract doc_ids and trigger parsing
                    doc_ids = []
                    if isinstance(res, list):
                        for item in res:
                            if isinstance(item, dict) and 'id' in item:
                                doc_ids.append(item['id'])
                    elif isinstance(res, dict) and 'id' in res:
                        doc_ids.append(res['id'])
                    
                    if doc_ids:
                        self.root.after(0, lambda i=iid: self.rag_file_list.set(i, column='upload_status', value='触发解析...'))
                        self.ragflow_client.run_parsing(kb_id, doc_ids)
                        self.root.after(0, lambda i=iid: self.rag_file_list.set(i, column='upload_status', value='已启动解析'))
                    else:
                        log_warn(f"Upload response did not contain doc IDs: {res}")
                        self.root.after(0, lambda i=iid: self.rag_file_list.set(i, column='upload_status', value='上传完成(未解析)'))

                    success_count += 1
                    
                except Exception as e:
                    self.root.after(0, lambda i=iid: self.rag_file_list.set(i, column='upload_status', value='失败'))
                    log_info(f"Upload failed for {f_obj['name']}: {e}")
                    fail_count += 1

            msg = f"上传完成: 成功 {success_count}, 失败 {fail_count}, 跳过 {skip_count}"
            self.root.after(0, lambda: [self.status_bar.config(text=msg), messagebox.showinfo("上传结果", msg)])

        threading.Thread(target=_bg_upload, daemon=True).start()

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
