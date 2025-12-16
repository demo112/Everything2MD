import pytest
from unittest.mock import patch, MagicMock
import subprocess
from src.core.converters.ppt import PptConverter

@pytest.fixture
def converter():
    return PptConverter()

def test_run_subprocess_with_context_and_timeout(converter):
    """
    测试当提供 context 和 timeout 时，_run_subprocess 是否正确处理参数。
    特别是验证 timeout 参数不应该传递给 Popen 构造函数，而应该传递给 communicate。
    """
    context = MagicMock()
    cmd = ["echo", "test"]
    timeout_val = 30
    
    # Mock subprocess.Popen
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (b"output", b"error")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
        
        # 调用被测方法
        converter._run_subprocess(cmd, context=context, timeout=timeout_val, check=True)
        
        # 验证 Popen 调用参数
        # 关键点：Popen 不应接收 timeout 参数
        args, kwargs = mock_popen.call_args
        assert "timeout" not in kwargs, "timeout 参数不应传递给 subprocess.Popen"
        
        # 验证 communicate 调用参数
        # 关键点：communicate 应接收 timeout 参数
        mock_proc.communicate.assert_called_once_with(timeout=timeout_val)
        
        # 验证 context 设置
        context.set_process.assert_called()

def test_run_subprocess_without_context_with_timeout(converter):
    """
    测试没有 context 时，_run_subprocess 应调用 subprocess.run，并正确传递 timeout。
    """
    cmd = ["echo", "test"]
    timeout_val = 30
    
    with patch("subprocess.run") as mock_run:
        converter._run_subprocess(cmd, context=None, timeout=timeout_val)
        
        # 验证 subprocess.run 接收了 timeout 参数
        args, kwargs = mock_run.call_args
        assert kwargs["timeout"] == timeout_val

def test_run_subprocess_capture_output(converter):
    """
    测试 capture_output 参数的处理。
    """
    context = MagicMock()
    cmd = ["echo", "test"]
    
    with patch("subprocess.Popen") as mock_popen:
        mock_proc = MagicMock()
        mock_proc.communicate.return_value = (b"out", b"err")
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc
        
        converter._run_subprocess(cmd, context=context, capture_output=True)
        
        args, kwargs = mock_popen.call_args
        assert kwargs["stdout"] == subprocess.PIPE
        assert kwargs["stderr"] == subprocess.PIPE
