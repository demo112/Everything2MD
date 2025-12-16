import pytest
import subprocess
import time
import os
import sys
import psutil
from pywinauto import Application, Desktop
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).resolve().parents[2]
GUI_SCRIPT = PROJECT_ROOT / "src" / "gui" / "main.py"

@pytest.fixture(scope="session")
def app_path():
    """返回要测试的应用路径 (脚本或exe)"""
    if not GUI_SCRIPT.exists():
        pytest.fail(f"GUI script not found at {GUI_SCRIPT}")
    return str(GUI_SCRIPT)

@pytest.fixture(scope="function")
def cleanup_processes():
    """清理可能残留的 Everything2MD 进程"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # 检查 cmdline 是否包含我们的脚本
            if proc.info['cmdline'] and 'main.py' in ' '.join(proc.info['cmdline']) and 'python' in proc.info['name']:
                print(f"Killing zombie process: {proc.info['pid']}")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    yield

@pytest.fixture(scope="function")
def app_process(app_path, cleanup_processes):
    """启动应用程序进程，并在测试结束后清理"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    
    # 启动应用
    cmd = [sys.executable, app_path]
    print(f"Starting app: {cmd}")
    proc = subprocess.Popen(cmd, env=env)
    
    # 增加等待时间，确保窗口创建
    time.sleep(5)
    
    yield proc
    
    # 清理
    if proc.poll() is None:
        print("Terminating app process...")
        try:
            parent = psutil.Process(proc.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
        except psutil.NoSuchProcess:
            pass
        proc.wait(timeout=5)

@pytest.fixture(scope="function")
def main_window(app_process):
    """连接到主窗口并返回 pywinauto WindowSpecification"""
    # 尝试 win32 backend，对 Tkinter 支持可能更好
    app = Application(backend="win32")
    
    try:
        # 使用精确标题匹配，避免匹配到 IDE 窗口
        target_title = "Everything2MD - 文档转换工具"
        print(f"Connecting to window with title: '{target_title}'")
        
        # 尝试连接
        app.connect(title=target_title, timeout=10)
        
        # 获取主窗口
        window = app.window(title=target_title)
        window.wait("visible", timeout=10)
        
        # 将焦点带到前台，避免其他窗口遮挡导致交互失败
        try:
            window.set_focus()
        except Exception:
            print("Warning: Could not set focus to window")
            
        return window
    except Exception as e:
        print(f"ERROR: {e}")
        # 如果连接失败，尝试打印当前所有窗口
        try:
            print("\nSearching for windows (fallback debug)...")
            windows = Desktop(backend="win32").windows()
            for w in windows:
                if "Everything" in w.window_text():
                     print(f"Found candidate: '{w.window_text()}'")
        except:
            pass
        pytest.fail(f"Failed to connect to application: {e}")
