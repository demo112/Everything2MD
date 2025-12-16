# LibreOffice启动超时修复 - 技术设计

## 1. 修复方案
修改 `_run_subprocess` 方法（涉及 `PptConverter` 和 `OfficeConverter`）：
1. 在调用 `subprocess.Popen` 之前，从 `kwargs` 中 `pop` 出 `timeout` 参数。
2. 将提取出的 `timeout` 参数传递给 `proc.communicate(timeout=timeout)`。

## 2. 代码变更示意
```python
def _run_subprocess(self, cmd, context=None, **kwargs):
    if context:
        # ... 其他参数处理 ...
        
        # 修复点：提取 timeout
        timeout = kwargs.pop('timeout', None)
        
        proc = subprocess.Popen(cmd, **kwargs)
        context.set_process(proc)
        try:
            # 修复点：传入 timeout
            stdout, stderr = proc.communicate(timeout=timeout)
            # ...
```

## 3. 测试设计
新增单元测试文件 `test/unit/core/converters/test_subprocess_helper.py`。
- 测试用例 1：`test_run_subprocess_with_context_and_timeout`
  - 验证：当传入 `context` 和 `timeout` 时，`timeout` 未传给 `Popen`，但传给了 `communicate`。
- 测试用例 2：`test_run_subprocess_without_context_with_timeout`
  - 验证：当无 `context` 时，`timeout` 正确传给 `subprocess.run`。
