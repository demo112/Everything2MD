import logging
import sys
import shutil
import os
import platform
import subprocess
import winreg
from pathlib import Path
try:
    from .config import ConfigManager
except ImportError:
    # Fallback for utils test
    try:
        from src.core.config import ConfigManager
    except ImportError:
        ConfigManager = None

# 配置日志
logger = logging.getLogger("Everything2MD")
logger.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# GUI 回调处理器
class CallbackHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        msg = self.format(record)
        self.callback(record.levelname, msg)

def setup_gui_logging(callback):
    """设置 GUI 日志回调"""
    handler = CallbackHandler(callback)
    handler.setFormatter(logging.Formatter('%(message)s')) # GUI 中可能不需要时间戳，因为界面简洁
    logger.addHandler(handler)

def log_info(msg):
    logger.info(msg)

def log_error(msg):
    logger.error(msg)

def log_warn(msg):
    logger.warning(msg)

def get_soffice_path():
    """获取 LibreOffice 路径"""
    # 1. 优先从配置获取
    if ConfigManager:
        try:
            cm = ConfigManager()
            custom_path = cm.get("soffice_path")
            if custom_path and os.path.exists(custom_path):
                # If directory, try to find soffice.exe inside
                if os.path.isdir(custom_path):
                    candidate = os.path.join(custom_path, "program", "soffice.exe")
                    if os.path.exists(candidate):
                        return candidate
                    # Or maybe directly in the folder?
                    candidate_direct = os.path.join(custom_path, "soffice.exe")
                    if os.path.exists(candidate_direct):
                        return candidate_direct
                else:
                    return custom_path
        except Exception:
            pass

    if platform.system() == "Windows":
        # 2. 尝试注册表查找
        try:
            # 常见的注册表路径
            reg_paths = [
                r"SOFTWARE\LibreOffice\LibreOffice",
                r"SOFTWARE\WOW6432Node\LibreOffice\LibreOffice"
            ]
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        # 获取版本号子项
                        i = 0
                        while True:
                            try:
                                version = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, f"{version}\\Path") as path_key:
                                    install_path, _ = winreg.QueryValueEx(path_key, "Path")
                                    exe_path = os.path.join(install_path, "soffice.exe")
                                    if os.path.exists(exe_path):
                                        return exe_path
                            except OSError:
                                break
                            i += 1
                except FileNotFoundError:
                    continue
        except Exception as e:
            log_warn(f"注册表查找 LibreOffice 失败: {e}")

        # 3. 尝试常见路径 (模糊匹配)
        common_roots = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        ]
        
        for root in common_roots:
            if not root or not os.path.exists(root): continue
            try:
                for item in os.listdir(root):
                    if "libreoffice" in item.lower():
                        candidate = os.path.join(root, item, "program", "soffice.exe")
                        if os.path.exists(candidate):
                            return candidate
            except Exception:
                pass

        # 4. 尝试硬编码路径
        paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
        for p in paths:
            if os.path.exists(p):
                return p
    
    # 5. 尝试 PATH
    if shutil.which("soffice"):
        return "soffice"
        
    return None

def get_pandoc_path():
    """获取 Pandoc 路径"""
    # 1. 优先从配置获取
    if ConfigManager:
        try:
            cm = ConfigManager()
            custom_path = cm.get("pandoc_path")
            if custom_path and os.path.exists(custom_path):
                if os.path.isdir(custom_path):
                     candidate = os.path.join(custom_path, "pandoc.exe")
                     if os.path.exists(candidate):
                         return candidate
                else:
                    return custom_path
        except Exception:
            pass

    if platform.system() == "Windows":
        paths = [
            r"C:\Program Files\Pandoc\pandoc.exe",
            os.path.expanduser(r"~\AppData\Local\Pandoc\pandoc.exe")
        ]
        for p in paths:
            if os.path.exists(p):
                return p
                
    if shutil.which("pandoc"):
        return "pandoc"
        
    return None

def check_dependencies():
    """检查依赖"""
    missing = []
    if not get_soffice_path():
        missing.append("LibreOffice")
    if not get_pandoc_path():
        missing.append("Pandoc")
    
    if missing:
        raise RuntimeError(f"缺少必要依赖: {', '.join(missing)}")
    return True
