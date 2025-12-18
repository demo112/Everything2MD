import logging
import logging.handlers
import sys
import os
import platform
import queue
from pathlib import Path


class GuiLogHandler(logging.Handler):
    """
    Custom handler to send logs to a queue for GUI display.
    """

    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        try:
            msg = self.format(record)
            # Send (levelname, msg) tuple to match existing GUI logic
            self.log_queue.put((record.levelname, msg))
        except Exception:
            self.handleError(record)


class LogManager:
    _instance = None
    _initialized = False

    @classmethod
    def setup(cls, log_level="INFO", gui_queue=None):
        if cls._initialized:
            return

        # 1. Determine Log Path
        if getattr(sys, "frozen", False):
            # Running as EXE: log next to executable
            base_dir = Path(sys.executable).parent
            log_dir = base_dir
        else:
            # Running as Script: logs/ folder in project root
            # src/core/logger.py -> src/core -> src -> root
            base_dir = Path(__file__).resolve().parent.parent.parent
            log_dir = base_dir / "logs"
            log_dir.mkdir(exist_ok=True)

        log_file = log_dir / "everything2md.log"

        # 2. Configure Root Logger
        root_logger = logging.getLogger()

        # Map string level to logging constant if needed
        if isinstance(log_level, str):
            level = getattr(logging, log_level.upper(), logging.INFO)
        else:
            level = log_level

        root_logger.setLevel(level)

        # Remove existing handlers to avoid duplicates
        if root_logger.hasHandlers():
            root_logger.handlers.clear()

        # Formatter
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)-8s] [%(module)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 3. File Handler (Rotating)
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file logging: {e}", file=sys.stderr)

        # 4. Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 5. GUI Handler
        if gui_queue:
            gui_handler = GuiLogHandler(gui_queue)
            # Use a simpler formatter for GUI display (just the message, or maybe include time?)
            # Existing GUI displays level by color, so just message is fine.
            # But let's keep the formatter simple.
            gui_formatter = logging.Formatter("%(message)s")
            gui_handler.setFormatter(gui_formatter)
            root_logger.addHandler(gui_handler)

        cls._initialized = True

        # 6. Setup Global Exception Hook
        sys.excepthook = cls.handle_exception

        # 7. Log Environment Info
        logger = cls.get_logger("LogManager")
        logger.info("=" * 50)
        logger.info("Everything2MD Session Started")
        logger.info(
            f"Platform: {platform.system()} {platform.release()} ({platform.machine()})"
        )
        logger.info(f"Python: {sys.version}")
        logger.info(f"Log File: {log_file}")
        logger.info(f"Frozen: {getattr(sys, 'frozen', False)}")
        logger.info("=" * 50)

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger = logging.getLogger()
        root_logger.critical(
            "Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback)
        )

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

    @staticmethod
    def mask_sensitive_config(config):
        """
        Recursively mask sensitive keys in a dictionary.
        """
        if not isinstance(config, dict):
            return config

        masked = config.copy()
        sensitive_keys = ["api_key", "password", "secret", "token"]

        for k, v in masked.items():
            if isinstance(v, dict):
                masked[k] = LogManager.mask_sensitive_config(v)
            elif any(s in k.lower() for s in sensitive_keys):
                masked[k] = "******"
        return masked
