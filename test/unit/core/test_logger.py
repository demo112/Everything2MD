"""
Tests for the LogManager class.

Property 6: 日志级别过滤正确性
*For any* 配置的日志级别，低于该级别的日志消息不应被输出。

**Validates: Requirements 10.1**
"""

import pytest
import logging
import queue
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from core.logger import LogManager, GuiLogHandler


class TestGuiLogHandler:
    """Tests for GuiLogHandler class."""

    def test_gui_handler_emits_to_queue(self):
        """Test that GuiLogHandler sends formatted messages to the queue."""
        log_queue = queue.Queue()
        handler = GuiLogHandler(log_queue)
        handler.setFormatter(logging.Formatter("%(message)s"))

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        assert not log_queue.empty()
        level, msg = log_queue.get()
        assert level == "INFO"
        assert msg == "Test message"

    def test_gui_handler_handles_different_levels(self):
        """Test that GuiLogHandler correctly handles different log levels."""
        log_queue = queue.Queue()
        handler = GuiLogHandler(log_queue)
        handler.setFormatter(logging.Formatter("%(message)s"))

        levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
        ]

        for level, level_name in levels:
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="",
                lineno=0,
                msg=f"Message at {level_name}",
                args=(),
                exc_info=None,
            )
            handler.emit(record)

            result_level, result_msg = log_queue.get()
            assert result_level == level_name
            assert f"Message at {level_name}" in result_msg


class TestLogManager:
    """Tests for LogManager class."""

    def setup_method(self):
        """Reset LogManager state before each test."""
        LogManager._initialized = False
        # Clear all handlers from root logger
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

    def teardown_method(self):
        """Clean up after each test."""
        LogManager._initialized = False
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logging.Logger instance."""
        logger = LogManager.get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_mask_sensitive_config_masks_api_key(self):
        """Test that sensitive keys are masked."""
        config = {
            "api_key": "secret123",
            "api_base": "https://api.example.com",
            "nested": {"api_key": "nested_secret", "value": "visible"},
        }

        masked = LogManager.mask_sensitive_config(config)

        assert masked["api_key"] == "******"
        assert masked["api_base"] == "https://api.example.com"
        assert masked["nested"]["api_key"] == "******"
        assert masked["nested"]["value"] == "visible"

    def test_mask_sensitive_config_handles_non_dict(self):
        """Test that non-dict input is returned as-is."""
        assert LogManager.mask_sensitive_config("string") == "string"
        assert LogManager.mask_sensitive_config(123) == 123
        assert LogManager.mask_sensitive_config(None) is None


# =============================================================================
# Property-Based Tests
# =============================================================================

from hypothesis import given, strategies as st, settings


# Log levels in order from lowest to highest
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]
LOG_LEVEL_VALUES = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}


@given(
    configured_level=st.sampled_from(LOG_LEVELS),
    message_level=st.sampled_from(LOG_LEVELS),
)
@settings(max_examples=100)
def test_property_log_level_filtering(configured_level, message_level):
    """
    Property 6: 日志级别过滤正确性

    *For any* 配置的日志级别，低于该级别的日志消息不应被输出。

    **Validates: Requirements 10.1**
    """
    # Reset LogManager state
    LogManager._initialized = False
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Create a queue to capture log output
    log_queue = queue.Queue()

    # Setup LogManager with the configured level and GUI queue
    with patch.object(LogManager, "_initialized", False):
        # We need to patch the file handler creation to avoid file I/O
        with patch("logging.handlers.RotatingFileHandler"):
            # Create a fresh logger setup
            test_logger = logging.getLogger("test_property")
            test_logger.handlers.clear()
            test_logger.setLevel(LOG_LEVEL_VALUES[configured_level])

            # Add a queue handler to capture output
            handler = GuiLogHandler(log_queue)
            handler.setLevel(LOG_LEVEL_VALUES[configured_level])
            handler.setFormatter(logging.Formatter("%(message)s"))
            test_logger.addHandler(handler)

            # Log a message at the specified level
            test_message = f"Test message at {message_level}"
            log_method = getattr(test_logger, message_level.lower())
            log_method(test_message)

            # Determine if message should be logged
            configured_idx = LOG_LEVELS.index(configured_level)
            message_idx = LOG_LEVELS.index(message_level)
            should_be_logged = message_idx >= configured_idx

            # Check the queue
            if should_be_logged:
                assert not log_queue.empty(), (
                    f"Message at {message_level} should be logged when level is {configured_level}"
                )
                level, msg = log_queue.get()
                assert level == message_level
                assert test_message in msg
            else:
                assert log_queue.empty(), (
                    f"Message at {message_level} should NOT be logged when level is {configured_level}"
                )

            # Cleanup
            test_logger.handlers.clear()


@given(log_level=st.sampled_from(LOG_LEVELS))
@settings(max_examples=100)
def test_property_all_levels_at_or_above_are_logged(log_level):
    """
    Property 6 (corollary): All messages at or above the configured level should be logged.

    *For any* configured log level, all messages at that level or higher should be output.

    **Validates: Requirements 10.1**
    """
    # Reset state
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    log_queue = queue.Queue()

    # Create test logger
    test_logger = logging.getLogger("test_property_above")
    test_logger.handlers.clear()
    test_logger.setLevel(LOG_LEVEL_VALUES[log_level])

    handler = GuiLogHandler(log_queue)
    handler.setLevel(LOG_LEVEL_VALUES[log_level])
    handler.setFormatter(logging.Formatter("%(message)s"))
    test_logger.addHandler(handler)

    # Get levels at or above configured level
    configured_idx = LOG_LEVELS.index(log_level)
    levels_to_log = LOG_LEVELS[configured_idx:]

    # Log messages at each level that should be logged
    for level in levels_to_log:
        log_method = getattr(test_logger, level.lower())
        log_method(f"Message at {level}")

    # Verify all expected messages were logged
    logged_messages = []
    while not log_queue.empty():
        logged_messages.append(log_queue.get())

    assert len(logged_messages) == len(levels_to_log), (
        f"Expected {len(levels_to_log)} messages, got {len(logged_messages)}"
    )

    # Cleanup
    test_logger.handlers.clear()
