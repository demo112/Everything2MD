#!/usr/bin/env python3
"""
Everything2MD GUI主程序
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import os
import threading
import queue
import json

class Everything2MDGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Everything2MD - 文档转换工具")
        self.root.geometry("700x500")
        
        # 初始化变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.log_level = tk.StringVar(value="INFO")
        self.output_format = tk.StringVar(value="markdown")
        self.batch_processing = tk.BooleanVar(value=True)
        self.max_parallel_jobs = tk.StringVar(value="2")
        self.file_filters = tk.StringVar(value="docx,pptx,pdf,txt")
        
        self.is_converting = False
        self.process = None
        
        # 加载配置
        self.load_config()
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 输入选择
        ttk.Label(main_frame, text="输入路径:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.input_path).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        ttk.Button(main_frame, text="浏览...", command=self.browse_input).grid(row=0, column=2, pady=2)
        
        # 输出选择
        ttk.Label(main_frame, text="输出路径:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.output_path).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        ttk.Button(main_frame, text="浏览...", command=self.browse_output).grid(row=1, column=2, pady=2)
        
        # 参数配置
        config_frame = ttk.LabelFrame(main_frame, text="转换配置", padding="5")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        config_frame.columnconfigure(1, weight=1)
        
        # 日志级别
        ttk.Label(config_frame, text="日志级别:").grid(row=0, column=0, sticky=tk.W, pady=2)
        log_level_combo = ttk.Combobox(config_frame, textvariable=self.log_level, values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly")
        log_level_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(0, 5))
        
        # 输出格式
        ttk.Label(config_frame, text="输出格式:").grid(row=0, column=2, sticky=tk.W, pady=2)
        output_format_combo = ttk.Combobox(config_frame, textvariable=self.output_format, values=["markdown", "html", "txt"], state="readonly")
        output_format_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=2)
        
        # 批量处理
        ttk.Label(config_frame, text="批量处理:").grid(row=1, column=0, sticky=tk.W, pady=2)
        batch_checkbox = ttk.Checkbutton(config_frame, text="启用", variable=self.batch_processing)
        batch_checkbox.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # 并行任务数
        ttk.Label(config_frame, text="并行任务数:").grid(row=1, column=2, sticky=tk.W, pady=2)
        max_jobs_spinbox = ttk.Spinbox(config_frame, textvariable=self.max_parallel_jobs, from_=1, to=16, width=5)
        max_jobs_spinbox.grid(row=1, column=3, sticky=tk.W, pady=2)
        
        # 文件过滤器
        ttk.Label(config_frame, text="文件过滤器:").grid(row=2, column=0, sticky=tk.W, pady=2)
        file_filters_entry = ttk.Entry(config_frame, textvariable=self.file_filters)
        file_filters_entry.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        self.settings_button = ttk.Button(button_frame, text="配置管理", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)
        
        # 进度显示
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 状态显示
        self.status_text = tk.Text(main_frame, height=10, wrap=tk.WORD)
        self.status_text.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 配置文本框滚动条
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # 配置主框架的行权重
        main_frame.rowconfigure(5, weight=1)
        
    def browse_input(self):
        """浏览选择输入路径"""
        if self.input_path.get() and os.path.exists(self.input_path.get()):
            initial_dir = self.input_path.get()
        else:
            initial_dir = os.path.expanduser("~")
            
        path = filedialog.askopenfilename(
            title="选择输入文件",
            initialdir=initial_dir,
            filetypes=[
                ("所有文件", "*.*"),
                ("Word文档", "*.docx *.doc"),
                ("Excel文档", "*.xlsx"),
                ("PowerPoint文档", "*.pptx *.ppt"),
                ("文本文件", "*.txt"),
                ("PDF文件", "*.pdf")
            ]
        )
        
        if path:
            self.input_path.set(path)
            
    def browse_output(self):
        """浏览选择输出路径"""
        if self.output_path.get() and os.path.exists(os.path.dirname(self.output_path.get())):
            initial_dir = os.path.dirname(self.output_path.get())
        else:
            initial_dir = os.path.expanduser("~")
            
        path = filedialog.askdirectory(
            title="选择输出目录",
            initialdir=initial_dir
        )
        
        if path:
            self.output_path.set(path)
            
    def load_config(self):
        """从配置文件加载配置到GUI"""
        try:
            cmd = [
                "bash", 
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "modules", "config_manager.sh")
            ]
            
            # 加载日志级别
            result = subprocess.run(cmd + ["get_config", "log_level"], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                self.log_level.set(result.stdout.strip())
                
            # 加载输出格式
            result = subprocess.run(cmd + ["get_config", "output_format"], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                self.output_format.set(result.stdout.strip())
                
            # 加载批量处理设置
            result = subprocess.run(cmd + ["get_config", "batch_processing_enabled"], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                self.batch_processing.set(result.stdout.strip().lower() == "true")
                
            # 加载并行任务数
            result = subprocess.run(cmd + ["get_config", "max_parallel_jobs"], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                self.max_parallel_jobs.set(result.stdout.strip())
                
            # 加载文件过滤器
            result = subprocess.run(cmd + ["get_config", "file_filters"], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                # 将JSON数组转换为逗号分隔的字符串
                filters_str = result.stdout.strip()
                if filters_str.startswith('[') and filters_str.endswith(']'):
                    filters = json.loads(filters_str)
                    self.file_filters.set(','.join(filters))
                else:
                    self.file_filters.set(filters_str)
                    
            print("配置加载成功")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"配置加载失败: {e}")
            messagebox.showwarning("警告", "配置文件不存在或格式错误，将使用默认配置")
            
            # 使用默认配置
            self.log_level.set("INFO")
            self.output_format.set("markdown")
            self.batch_processing.set(True)
            self.max_parallel_jobs.set("2")
            self.file_filters.set("docx,pptx,pdf,txt")
            return False
                
    def save_config(self):
        """保存配置文件"""
        try:
            # 构建配置命令
            cmd = [
                "bash", 
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "modules", "config_manager.sh")
            ]
            
            # 设置配置值
            subprocess.run(cmd + ["set_config", "log_level", self.log_level.get()], check=True)
            subprocess.run(cmd + ["set_config", "output_format", self.output_format.get()], check=True)
            subprocess.run(cmd + ["set_config", "batch_processing_enabled", 
                                "true" if self.batch_processing.get() else "false"], check=True)
            subprocess.run(cmd + ["set_config", "max_parallel_jobs", self.max_parallel_jobs.get()], check=True)
            
            # 保存文件过滤器
            filters = [f.strip() for f in self.file_filters.get().split(',') if f.strip()]
            subprocess.run(cmd + ["set_config", "file_filters", ",".join(filters)], check=True)
            
            # 保存路径设置 - 使用配置管理器命令
            subprocess.run(cmd + ["set_config", "last_input_path", self.input_path.get()], check=True)
            subprocess.run(cmd + ["set_config", "last_output_path", self.output_path.get()], check=True)
            
            # 保存所有配置
            subprocess.run(cmd + ["save_config"], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"配置保存失败: {e}")
            return False
        except Exception as e:
            messagebox.showerror("错误", f"配置保存失败: {e}")
            return False
            
    def open_settings(self):
        """打开配置管理窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("配置管理")
        settings_window.geometry("500x400")
        settings_window.resizable(False, False)
        
        # 设置窗口居中
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # 创建配置管理界面
        self.create_settings_widgets(settings_window)
        
    def create_settings_widgets(self, parent):
        """创建配置管理界面"""
        # 主框架
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置管理标签页
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本设置标签页
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="基本设置")
        
        # 转换设置标签页
        conversion_frame = ttk.Frame(notebook, padding="10")
        notebook.add(conversion_frame, text="转换设置")
        
        # 高级设置标签页
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="高级设置")
        
        # 基本设置内容
        self.create_basic_settings(basic_frame)
        
        # 转换设置内容
        self.create_conversion_settings(conversion_frame)
        
        # 高级设置内容
        self.create_advanced_settings(advanced_frame)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # 保存按钮
        ttk.Button(button_frame, text="保存配置", command=self.save_settings).pack(side=tk.RIGHT, padx=5)
        
        # 恢复默认按钮
        ttk.Button(button_frame, text="恢复默认", command=self.restore_defaults).pack(side=tk.RIGHT, padx=5)
        
        # 取消按钮
        ttk.Button(button_frame, text="取消", command=parent.destroy).pack(side=tk.RIGHT, padx=5)
        
    def create_basic_settings(self, parent):
        """创建基本设置界面"""
        # 日志级别
        ttk.Label(parent, text="日志级别:").grid(row=0, column=0, sticky=tk.W, pady=5)
        log_level_combo = ttk.Combobox(parent, textvariable=self.log_level, values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly")
        log_level_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        
        # 输出格式
        ttk.Label(parent, text="输出格式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        output_format_combo = ttk.Combobox(parent, textvariable=self.output_format, values=["markdown", "html", "txt"], state="readonly")
        output_format_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))
        
        # 配置列权重
        parent.columnconfigure(1, weight=1)
        
    def create_conversion_settings(self, parent):
        """创建转换设置界面"""
        # 批量处理
        ttk.Label(parent, text="批量处理:").grid(row=0, column=0, sticky=tk.W, pady=5)
        batch_checkbox = ttk.Checkbutton(parent, text="启用批量处理", variable=self.batch_processing)
        batch_checkbox.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 并行任务数
        ttk.Label(parent, text="并行任务数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        max_jobs_spinbox = ttk.Spinbox(parent, textvariable=self.max_parallel_jobs, from_=1, to=16, width=5)
        max_jobs_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 文件过滤器
        ttk.Label(parent, text="文件过滤器:").grid(row=2, column=0, sticky=tk.W, pady=5)
        file_filters_entry = ttk.Entry(parent, textvariable=self.file_filters, width=30)
        file_filters_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(parent, text="格式: docx,pptx,pdf,txt").grid(row=3, column=1, sticky=tk.W, pady=2)
        
        # 配置列权重
        parent.columnconfigure(1, weight=1)
        
    def create_advanced_settings(self, parent):
        """创建高级设置界面"""
        # 备份管理
        ttk.Label(parent, text="配置备份:").grid(row=0, column=0, sticky=tk.W, pady=5)
        backup_button = ttk.Button(parent, text="创建备份", command=self.create_backup)
        backup_button.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 备份列表
        ttk.Label(parent, text="可用备份:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.backup_listbox = tk.Listbox(parent, height=6)
        self.backup_listbox.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # 恢复按钮
        restore_button = ttk.Button(parent, text="恢复选中备份", command=self.restore_backup)
        restore_button.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 加载备份列表
        self.load_backup_list()
        
        # 配置列权重和行权重
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(1, weight=1)
        
    def save_settings(self):
        """保存配置设置"""
        if self.save_config():
            messagebox.showinfo("成功", "配置已保存")
            
    def restore_defaults(self):
        """恢复默认设置"""
        if messagebox.askyesno("确认", "确定要恢复默认设置吗？"):
            self.log_level.set("INFO")
            self.output_format.set("markdown")
            self.batch_processing.set(True)
            self.max_parallel_jobs.set("2")
            self.file_filters.set("docx,pptx,pdf,txt")
            
    def create_backup(self):
        """创建配置备份"""
        try:
            cmd = [
                "bash", 
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "modules", "config_manager.sh")
            ]
            
            subprocess.run(cmd + ["backup_config"], check=True)
            messagebox.showinfo("成功", "配置备份已创建")
            self.load_backup_list()
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("错误", f"备份创建失败: {e}")
            
    def load_backup_list(self):
        """加载备份列表"""
        try:
            cmd = [
                "bash", 
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "modules", "config_manager.sh")
            ]
            
            result = subprocess.run(cmd + ["list_backups"], capture_output=True, text=True, check=True)
            
            # 清空列表
            if hasattr(self, 'backup_listbox'):
                self.backup_listbox.delete(0, tk.END)
                
                # 添加备份文件
                for line in result.stdout.strip().split('\n')[1:]:  # 跳过标题行
                    if line.strip():
                        self.backup_listbox.insert(tk.END, line.strip())
                        
        except subprocess.CalledProcessError:
            pass
            
    def restore_backup(self):
        """恢复选中备份"""
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请选择一个备份文件")
            return
            
        backup_file = self.backup_listbox.get(selection[0])
        
        if messagebox.askyesno("确认", f"确定要恢复备份文件吗？\n{backup_file}"):
            try:
                cmd = [
                    "bash", 
                    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "modules", "config_manager.sh")
                ]
                
                subprocess.run(cmd + ["restore_config", backup_file], check=True)
                
                # 重新加载配置
                self.load_config()
                messagebox.showinfo("成功", "配置已恢复")
                
            except subprocess.CalledProcessError as e:
                messagebox.showerror("错误", f"备份恢复失败: {e}")
            
    def start_conversion(self):
        """开始转换过程"""
        # 验证输入
        if not self.input_path.get():
            messagebox.showerror("错误", "请选择输入文件或目录")
            return
            
        if not self.output_path.get():
            messagebox.showerror("错误", "请选择输出目录")
            return
            
        # 检查输入路径是否存在
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("错误", "输入路径不存在")
            return
            
        # 禁用开始按钮，启用取消按钮
        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.is_converting = True
        
        # 清空状态文本
        self.status_text.delete(1.0, tk.END)
        
        # 启动进度条
        self.progress.start()
        
        # 在新线程中执行转换
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
        
    def run_conversion(self):
        """执行转换过程"""
        try:
            # 构建命令
            script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.sh")
            cmd = ["bash", script_path]
            
            # 添加参数
            cmd.extend(["-i", self.input_path.get()])
            
            # 如果输出路径是一个目录，则构建完整的输出文件路径
            output_path = self.output_path.get()
            if os.path.isdir(output_path):
                input_filename = os.path.basename(self.input_path.get())
                output_filename = os.path.splitext(input_filename)[0] + ".md"
                output_path = os.path.join(output_path, output_filename)
            
            cmd.extend(["-o", output_path])
            
            if self.log_level.get() != "INFO":
                cmd.extend(["-l", self.log_level.get()])
                
            # 执行命令
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 读取输出
            for line in self.process.stdout:
                if not self.is_converting:
                    break
                self.root.after(0, self.update_status, line)
                
            # 等待进程结束
            self.process.wait()
            
            # 更新UI
            self.root.after(0, self.conversion_finished)
            
        except Exception as e:
            self.root.after(0, self.conversion_error, str(e))
            
    def update_status(self, message):
        """更新状态显示"""
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
        
    def conversion_finished(self):
        """转换完成处理"""
        self.progress.stop()
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.is_converting = False
        self.process = None
        
        # 显示完成消息
        messagebox.showinfo("完成", "转换完成!")
        
    def conversion_error(self, error_message):
        """转换错误处理"""
        self.progress.stop()
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.is_converting = False
        self.process = None
        
        # 显示错误消息
        messagebox.showerror("错误", f"转换过程中发生错误:\n{error_message}")
        
    def cancel_conversion(self):
        """取消转换过程"""
        if self.process and self.is_converting:
            self.process.terminate()
            self.is_converting = False
            
        self.progress.stop()
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        
        # 显示取消消息
        self.status_text.insert(tk.END, "\n转换已取消\n")
        self.status_text.see(tk.END)

def main():
    root = tk.Tk()
    app = Everything2MDGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()