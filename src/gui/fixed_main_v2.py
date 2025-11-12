#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fixed Everything2MD GUI Application
This version uses the fixed configuration manager to resolve encoding issues.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import subprocess
import sys

class FixedEverything2MDGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Everything2MD 配置管理器 (修复版)")
        self.root.geometry("600x700")
        
        # Configuration file path
        self.config_dir = os.path.expanduser("~/.config/everything2md")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        # Initialize configuration values with defaults
        self.config = {
            "log_level": tk.StringVar(value="INFO"),
            "output_format": tk.StringVar(value="markdown"),
            "batch_processing_enabled": tk.BooleanVar(value=True),
            "max_parallel_jobs": tk.StringVar(value="2"),
            "file_filters": tk.StringVar(value="docx,pptx,pdf,txt"),
            "last_input_path": tk.StringVar(value=""),
            "last_output_path": tk.StringVar(value="")
        }
        
        # Load configuration
        self.load_config()
        
        # Create GUI
        self.create_widgets()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update GUI variables with loaded values
                self.config["log_level"].set(config_data.get("log_level", "INFO"))
                self.config["output_format"].set(config_data.get("output_format", "markdown"))
                
                batch_settings = config_data.get("conversion_settings", {}).get("batch_processing", {})
                self.config["batch_processing_enabled"].set(batch_settings.get("enabled", True))
                self.config["max_parallel_jobs"].set(str(batch_settings.get("max_parallel_jobs", 2)))
                self.config["file_filters"].set(",".join(batch_settings.get("file_filters", ["docx", "pptx", "pdf", "txt"])))
                
                self.config["last_input_path"].set(config_data.get("last_input_path", ""))
                self.config["last_output_path"].set(config_data.get("last_output_path", ""))
                
                print("Configuration loaded successfully")
            else:
                print("Configuration file not found, using defaults")
        except Exception as e:
            print(f"Error loading configuration: {e}")
            
    def save_config_to_file(self):
        """Save configuration to file using the fixed config manager"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(self.config_dir, exist_ok=True)
            
            # Prepare configuration data
            config_data = {
                "log_level": self.config["log_level"].get(),
                "output_format": self.config["output_format"].get(),
                "conversion_settings": {
                    "batch_processing": {
                        "enabled": self.config["batch_processing_enabled"].get(),
                        "max_parallel_jobs": int(self.config["max_parallel_jobs"].get()),
                        "file_filters": [f.strip() for f in self.config["file_filters"].get().split(",") if f.strip()]
                    }
                },
                "last_input_path": self.config["last_input_path"].get(),
                "last_output_path": self.config["last_output_path"].get()
            }
            
            # Save to file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            print("Configuration saved successfully")
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
            
    def validate_config(self):
        """Validate configuration values"""
        errors = []
        
        # Validate log level
        log_level = self.config["log_level"].get()
        valid_log_levels = ["DEBUG", "INFO", "WARN", "WARNING", "ERROR"]
        if log_level not in valid_log_levels:
            errors.append(f"无效的日志级别: {log_level}")
            
        # Validate output format
        output_format = self.config["output_format"].get()
        valid_formats = ["markdown", "html", "txt"]
        if output_format not in valid_formats:
            errors.append(f"无效的输出格式: {output_format}")
            
        # Validate max parallel jobs
        try:
            max_jobs = int(self.config["max_parallel_jobs"].get())
            if max_jobs < 1 or max_jobs > 16:
                errors.append("并行任务数必须在1-16之间")
        except ValueError:
            errors.append("并行任务数必须是数字")
            
        # Validate file filters
        filters = self.config["file_filters"].get()
        if not filters.strip():
            errors.append("文件过滤器不能为空")
            
        return errors
        
    def save_config(self):
        """Save configuration after validation"""
        # Validate configuration
        errors = self.validate_config()
        if errors:
            error_msg = "\n".join(errors)
            messagebox.showerror("配置错误", f"以下配置项有误:\n\n{error_msg}")
            return False
            
        # Save configuration
        if self.save_config_to_file():
            messagebox.showinfo("成功", "配置已保存")
            return True
        else:
            messagebox.showerror("错误", "保存配置时发生错误")
            return False
            
    def select_input_path(self):
        """Select input path"""
        path = filedialog.askdirectory()
        if path:
            self.config["last_input_path"].set(path)
            
    def select_output_path(self):
        """Select output path"""
        path = filedialog.askdirectory()
        if path:
            self.config["last_output_path"].set(path)
            
    def create_widgets(self):
        """Create GUI widgets"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General settings tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="常规设置")
        self.create_general_tab(general_frame)
        
        # Batch processing tab
        batch_frame = ttk.Frame(notebook)
        notebook.add(batch_frame, text="批量处理")
        self.create_batch_tab(batch_frame)
        
        # Paths tab
        paths_frame = ttk.Frame(notebook)
        notebook.add(paths_frame, text="路径设置")
        self.create_paths_tab(paths_frame)
        
        # Control buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
    def create_general_tab(self, parent):
        """Create general settings tab"""
        # Log level
        ttk.Label(parent, text="日志级别:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        log_level_combo = ttk.Combobox(parent, textvariable=self.config["log_level"], 
                                      values=["DEBUG", "INFO", "WARN", "WARNING", "ERROR"], 
                                      state="readonly", width=20)
        log_level_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Output format
        ttk.Label(parent, text="输出格式:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        output_format_combo = ttk.Combobox(parent, textvariable=self.config["output_format"], 
                                          values=["markdown", "html", "txt"], 
                                          state="readonly", width=20)
        output_format_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
    def create_batch_tab(self, parent):
        """Create batch processing tab"""
        # Batch processing enabled
        batch_check = ttk.Checkbutton(parent, text="启用批量处理", 
                                     variable=self.config["batch_processing_enabled"])
        batch_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Max parallel jobs
        ttk.Label(parent, text="最大并行任务数:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        max_jobs_spin = ttk.Spinbox(parent, from_=1, to=16, textvariable=self.config["max_parallel_jobs"],
                                   width=10)
        max_jobs_spin.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # File filters
        ttk.Label(parent, text="文件过滤器:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        filters_entry = ttk.Entry(parent, textvariable=self.config["file_filters"], width=40)
        filters_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(parent, text="用逗号分隔文件扩展名，如: docx,pptx,pdf,txt").grid(
            row=3, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
    def create_paths_tab(self, parent):
        """Create paths tab"""
        # Input path
        ttk.Label(parent, text="输入路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        input_frame = ttk.Frame(parent)
        input_frame.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)
        ttk.Entry(input_frame, textvariable=self.config["last_input_path"]).grid(
            row=0, column=0, sticky=tk.EW)
        ttk.Button(input_frame, text="浏览", command=self.select_input_path).grid(
            row=0, column=1, padx=(5, 0))
        
        # Output path
        ttk.Label(parent, text="输出路径:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        output_frame = ttk.Frame(parent)
        output_frame.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        output_frame.columnconfigure(0, weight=1)
        ttk.Entry(output_frame, textvariable=self.config["last_output_path"]).grid(
            row=0, column=0, sticky=tk.EW)
        ttk.Button(output_frame, text="浏览", command=self.select_output_path).grid(
            row=0, column=1, padx=(5, 0))
        
        # Path notes
        ttk.Label(parent, text="留空以使用默认路径").grid(
            row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=2)

def main():
    root = tk.Tk()
    app = FixedEverything2MDGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()