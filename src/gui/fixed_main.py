#!/usr/bin/env python3
"""
修复版本的GUI类，解决配置保存的问题
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import json
import threading

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class FixedEverything2MDGUI:
    """修复版本的GUI类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Everything2MD - 修复版")
        self.root.geometry("600x500")
        
        # 获取项目根目录和配置管理器路径
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_manager_path = os.path.join(self.project_root, "src", "modules", "config_manager.sh")
        
        # 检查配置管理器是否存在
        if not os.path.exists(self.config_manager_path):
            raise FileNotFoundError(f"配置管理器不存在: {self.config_manager_path}")
        
        # 初始化配置变量
        self.log_level = tk.StringVar()
        self.output_format = tk.StringVar()
        self.batch_processing = tk.BooleanVar()
        self.max_parallel_jobs = tk.StringVar()
        self.file_filters = tk.StringVar()
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # 创建界面
        self.create_widgets()
        
        # 加载配置
        self.load_config()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建笔记本控件用于标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建基本设置标签页
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="基本设置")
        
        # 创建批量处理标签页
        batch_frame = ttk.Frame(notebook)
        notebook.add(batch_frame, text="批量处理")
        
        # 创建路径设置标签页
        path_frame = ttk.Frame(notebook)
        notebook.add(path_frame, text="路径设置")
        
        # 基本设置标签页内容
        ttk.Label(basic_frame, text="日志级别:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        log_level_combo = ttk.Combobox(basic_frame, textvariable=self.log_level, 
                                      values=["DEBUG", "INFO", "WARN", "ERROR"])
        log_level_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(basic_frame, text="输出格式:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        output_format_combo = ttk.Combobox(basic_frame, textvariable=self.output_format,
                                          values=["markdown", "html", "txt"])
        output_format_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 批量处理标签页内容
        ttk.Checkbutton(batch_frame, text="启用批量处理", variable=self.batch_processing).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(batch_frame, text="最大并行任务数:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        max_parallel_jobs_spin = ttk.Spinbox(batch_frame, from_=1, to=16, textvariable=self.max_parallel_jobs,
                                            width=10)
        max_parallel_jobs_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(batch_frame, text="文件过滤器:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        file_filters_entry = ttk.Entry(batch_frame, textvariable=self.file_filters, width=30)
        file_filters_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(batch_frame, text="格式: docx,pptx,pdf,txt").grid(row=3, column=1, sticky=tk.W, padx=5, pady=0)
        
        # 路径设置标签页内容
        ttk.Label(path_frame, text="输入路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        input_path_frame = ttk.Frame(path_frame)
        input_path_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(input_path_frame, textvariable=self.input_path, width=30).pack(side=tk.LEFT)
        ttk.Button(input_path_frame, text="浏览", command=self.browse_input_path).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(path_frame, text="输出路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        output_path_frame = ttk.Frame(path_frame)
        output_path_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(output_path_frame, textvariable=self.output_path, width=30).pack(side=tk.LEFT)
        ttk.Button(output_path_frame, text="浏览", command=self.browse_output_path).pack(side=tk.LEFT, padx=(5, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="恢复默认设置", command=self.restore_defaults).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="开始转换", command=self.start_conversion).pack(side=tk.RIGHT)
    
    def browse_input_path(self):
        """浏览输入路径"""
        path = filedialog.askdirectory()
        if path:
            self.input_path.set(path)
    
    def browse_output_path(self):
        """浏览输出路径"""
        path = filedialog.askdirectory()
        if path:
            self.output_path.set(path)
    
    def load_config(self):
        """加载配置"""
        try:
            # 使用配置管理器获取配置值
            cmd = ["bash", self.config_manager_path]
            
            # 获取各个配置项
            self.log_level.set(self.get_config_value(cmd, "log_level"))
            self.output_format.set(self.get_config_value(cmd, "output_format"))
            self.batch_processing.set(self.get_config_value(cmd, "batch_processing_enabled") == "true")
            self.max_parallel_jobs.set(self.get_config_value(cmd, "max_parallel_jobs"))
            self.file_filters.set(self.get_config_value(cmd, "file_filters"))
            self.input_path.set(self.get_config_value(cmd, "last_input_path"))
            self.output_path.set(self.get_config_value(cmd, "last_output_path"))
            
            print("配置加载成功")
        except Exception as e:
            print(f"配置加载失败: {e}")
            self.restore_defaults()
    
    def get_config_value(self, cmd, key):
        """获取配置值"""
        try:
            result = subprocess.run(cmd + ["get_config", key], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            # 如果获取失败，返回默认值
            defaults = {
                "log_level": "INFO",
                "output_format": "markdown",
                "batch_processing_enabled": "true",
                "max_parallel_jobs": "2",
                "file_filters": "docx,pptx,pdf,txt",
                "last_input_path": "",
                "last_output_path": ""
            }
            return defaults.get(key, "")
    
    def restore_defaults(self):
        """恢复默认设置"""
        self.log_level.set("INFO")
        self.output_format.set("markdown")
        self.batch_processing.set(True)
        self.max_parallel_jobs.set("2")
        self.file_filters.set("docx,pptx,pdf,txt")
        self.input_path.set("")
        self.output_path.set("")
        print("已恢复默认设置")
    
    def save_config(self):
        """修复版本的配置保存方法"""
        try:
            # 构建配置命令
            cmd = ["bash", self.config_manager_path]
            
            # 收集所有配置值
            config_values = {
                "log_level": self.log_level.get(),
                "output_format": self.output_format.get(),
                "batch_processing_enabled": "true" if self.batch_processing.get() else "false",
                "max_parallel_jobs": str(self.max_parallel_jobs.get()),
                "file_filters": self.file_filters.get(),
                "last_input_path": self.input_path.get(),
                "last_output_path": self.output_path.get()
            }
            
            # 验证所有配置值
            all_valid = True
            validation_errors = []
            
            for key, value in config_values.items():
                # 特殊处理文件过滤器
                if key == "file_filters":
                    filters = [f.strip() for f in value.split(',') if f.strip()]
                    value = ",".join(filters)
                    config_values[key] = value
                
                # 验证每个配置项
                try:
                    # 使用配置管理器验证单个配置项
                    validation_cmd = cmd + ["set_config", key, value]
                    result = subprocess.run(validation_cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        error_msg = result.stderr.strip() if result.stderr else "验证失败"
                        validation_errors.append(f"{key}: {error_msg}")
                        all_valid = False
                except Exception as e:
                    validation_errors.append(f"{key}: {str(e)}")
                    all_valid = False
            
            if not all_valid:
                error_message = "\n".join(validation_errors)
                print(f"配置验证失败:\n{error_message}")
                messagebox.showerror("配置验证失败", f"以下配置项验证失败:\n{error_message}")
                return False
            
            # 如果所有配置都有效，则设置配置值
            for key, value in config_values.items():
                subprocess.run(cmd + ["set_config", key, value], check=True)
            
            # 保存所有配置
            subprocess.run(cmd + ["save_config"], check=True)
            
            print("配置保存成功")
            messagebox.showinfo("成功", "配置已成功保存")
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            print(f"配置保存失败: {error_msg}")
            messagebox.showerror("配置保存失败", f"配置保存失败:\n{error_msg}")
            return False
        except Exception as e:
            print(f"配置保存失败: {e}")
            messagebox.showerror("配置保存失败", f"配置保存失败:\n{str(e)}")
            return False
    
    def start_conversion(self):
        """开始转换"""
        # 保存配置
        if not self.save_config():
            return
        
        # 获取输入和输出路径
        input_path = self.input_path.get()
        output_path = self.output_path.get()
        
        if not input_path or not output_path:
            messagebox.showerror("错误", "请设置输入路径和输出路径")
            return
        
        # 运行转换命令
        try:
            conversion_cmd = [
                "bash",
                os.path.join(self.project_root, "src", "modules", "conversion_manager.sh"),
                input_path,
                output_path
            ]
            
            # 在新线程中运行转换
            thread = threading.Thread(target=self.run_conversion, args=(conversion_cmd,))
            thread.daemon = True
            thread.start()
            
            messagebox.showinfo("开始转换", "转换已在后台开始运行")
        except Exception as e:
            messagebox.showerror("转换失败", f"启动转换失败:\n{str(e)}")
    
    def run_conversion(self, cmd):
        """运行转换命令"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("转换完成")
            else:
                error_msg = result.stderr.strip() if result.stderr else "转换失败"
                print(f"转换失败: {error_msg}")
        except Exception as e:
            print(f"转换出错: {e}")

def main():
    """主函数"""
    root = tk.Tk()
    app = FixedEverything2MDGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()