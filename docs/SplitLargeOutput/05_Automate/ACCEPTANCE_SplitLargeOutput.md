# ACCEPTANCE: 大文件自动切分策略

## 执行记录

### 1. 代码实现
- **配置**: `src/core/config.py` 已添加 `max_output_file_size_mb` (默认 50MB)。
- **核心**: `src/core/utils.py` 已添加 `split_large_file` 函数，支持按行切分和阈值检测。
- **集成**: `src/core/engine.py` 已集成切分逻辑，并更新了 `convert_file` 和 `run` 方法以支持多文件输出。

### 2. 测试验证
- **单元测试**: `tests/unit/test_splitter.py` 已创建并通过。
    - 验证了小文件不切分。
    - 验证了超限文件正确切分并删除原文件。
    - 验证了配置为 0 时禁用切分。
- **集成逻辑**: `engine.py` 能正确处理返回的文件列表，并逐个回调 `file_converted_callback`，确保 GUI 能展示所有分卷。

### 3. 结果确认
符合所有验收标准。
- [x] 配置生效
- [x] 触发切分
- [x] 大小合规
- [x] 内容完整
- [x] 原始清理

## 遗留问题
无。

## 结论
功能开发完成，已通过单元测试验证。
