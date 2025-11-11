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

class Everything2MDGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Everything2MD - 文档转换工具")
        self.root.geometry("600x400")
        
        # 初始化变量
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.log_level = tk.StringVar(value="INFO")
        self.is_converting = False
        self.process = None
        
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
        ttk.Label(main_frame, text="日志级别:").grid(row=2, column=0, sticky=tk.W, pady=2)
        log_level_combo = ttk.Combobox(main_frame, textvariable=self.log_level, values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly")
        log_level_combo.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel_conversion, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
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
                ("Word文档", "*.docx"),
                ("Excel文档", "*.xlsx"),
                ("PowerPoint文档", "*.pptx"),
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
            cmd.extend(["-o", self.output_path.get()])
            
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