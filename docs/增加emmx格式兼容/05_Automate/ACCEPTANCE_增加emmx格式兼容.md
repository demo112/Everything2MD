# ACCEPTANCE: 增加 emmx 格式兼容

## 1. 执行记录
- **Task 1 (EmmxConverter)**: 已实现。支持 `doc/document.json` 和 `mindmap.json` 结构。
- **Task 2 (Engine 集成)**: 已完成。更新了 `detect_type` 和 `convert_file`。
- **Task 3 (单元测试)**: 创建了 `tests/test_emmx.py`，覆盖了标准结构和扁平结构，测试通过。
- **Task 4 (GUI 更新)**: 已更新默认文件过滤器，添加了 `emmx`。

## 2. 验证结果
- **功能测试**: 模拟的 MindMaster 文件成功转换为 Markdown，层级结构正确。
- **异常处理**: 针对非 zip 文件或不合法的 emmx 文件，代码中已包含异常处理逻辑。

## 3. 遗留问题
- 无。
