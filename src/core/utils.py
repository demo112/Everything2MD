import logging
import sys
import shutil
import os
import platform
import subprocess
import winreg
from pathlib import Path
from .logger import LogManager

try:
    from .config import ConfigManager
except ImportError:
    # Fallback for utils test
    try:
        from core.config import ConfigManager
    except ImportError:
        ConfigManager = None

# Get logger from LogManager
logger = LogManager.get_logger("core.utils")


def setup_gui_logging(callback):
    """
    Deprecated: Use LogManager.setup(gui_queue=...) instead.
    This function is kept for backward compatibility.
    """
    logger.warning("setup_gui_logging is deprecated. Use LogManager.setup().")


def log_info(msg):
    logger.info(msg)


def log_error(msg):
    logger.error(msg)


def log_warn(msg):
    logger.warning(msg)


def run_command_with_logging(cmd, **kwargs):
    """
    Execute subprocess command and log its output.
    """
    cmd_str = " ".join(str(x) for x in cmd)
    logger.info(f"Executing command: {cmd_str}")

    # Force capture_output and text mode to capture logs
    kwargs["capture_output"] = True
    kwargs["text"] = True

    # Default encoding to utf-8 to avoid Windows gbk issues
    if "encoding" not in kwargs:
        kwargs["encoding"] = "utf-8"
    if "errors" not in kwargs:
        kwargs["errors"] = "replace"

    try:
        # On Windows, prevent console window popping up
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = startupinfo

        result = subprocess.run(cmd, **kwargs)

        if result.returncode != 0:
            logger.error(f"Command failed with code {result.returncode}")
            if result.stdout:
                logger.error(f"Stdout: {result.stdout.strip()}")
            if result.stderr:
                logger.error(f"Stderr: {result.stderr.strip()}")
        else:
            logger.debug("Command execution successful")
            if result.stdout:
                preview = result.stdout.strip()
                if len(preview) > 500:
                    preview = preview[:500] + "... [truncated]"
                logger.debug(f"Stdout: {preview}")

        return result
    except Exception as e:
        logger.exception(f"Failed to execute command: {cmd_str}")
        raise


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
                r"SOFTWARE\WOW6432Node\LibreOffice\LibreOffice",
            ]
            for reg_path in reg_paths:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                        # 获取版本号子项
                        i = 0
                        while True:
                            try:
                                version = winreg.EnumKey(key, i)
                                with winreg.OpenKey(
                                    key, f"{version}\\Path"
                                ) as path_key:
                                    install_path, _ = winreg.QueryValueEx(
                                        path_key, "Path"
                                    )
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
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        ]

        for root in common_roots:
            if not root or not os.path.exists(root):
                continue
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
            os.path.expanduser(r"~\AppData\Local\Pandoc\pandoc.exe"),
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


def split_large_file(file_path: Path, max_size_mb: int) -> list:
    """
    Split a large file into smaller parts if it exceeds max_size_mb.
    Returns a list of paths (either [original] or [part1, part2, ...]).
    """
    file_path = Path(file_path)
    if not file_path.exists() or max_size_mb <= 0:
        return [file_path]

    threshold_bytes = max_size_mb * 1024 * 1024
    if file_path.stat().st_size <= threshold_bytes:
        return [file_path]

    log_info(
        f"File {file_path} size {file_path.stat().st_size} exceeds threshold {threshold_bytes}. Splitting..."
    )

    target_bytes = int(threshold_bytes * 0.9)
    parts = []

    try:
        # Check encoding, assume utf-8
        with open(file_path, "r", encoding="utf-8") as f:
            part_num = 1
            current_part_path = (
                file_path.parent / f"{file_path.stem}_part{part_num}{file_path.suffix}"
            )
            current_part_file = open(
                current_part_path, "w", encoding="utf-8", newline=""
            )
            current_size = 0
            parts.append(current_part_path)

            for line in f:
                line_bytes = len(line.encode("utf-8"))

                # If current part exceeds target (and not empty), start new part
                if current_size + line_bytes > target_bytes and current_size > 0:
                    current_part_file.close()
                    part_num += 1
                    current_part_path = (
                        file_path.parent
                        / f"{file_path.stem}_part{part_num}{file_path.suffix}"
                    )
                    current_part_file = open(
                        current_part_path, "w", encoding="utf-8", newline=""
                    )
                    current_size = 0
                    parts.append(current_part_path)

                current_part_file.write(line)
                current_size += line_bytes

            current_part_file.close()

        # Delete original file
        file_path.unlink()
        log_info(f"Split {file_path} into {len(parts)} parts.")
        return parts

    except Exception as e:
        log_error(f"Failed to split file {file_path}: {e}")
        return [file_path]
