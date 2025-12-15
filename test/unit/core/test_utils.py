import pytest
import logging
from src.core.utils import setup_gui_logging, log_info, log_error

def test_logger():
    # Setup a mock callback
    logs = []
    def callback(level, msg):
        logs.append((level, msg))
        
    setup_gui_logging(callback)
    
    log_info("test info")
    log_error("test error")
    
    assert ("INFO", "test info") in logs
    assert ("ERROR", "test error") in logs
