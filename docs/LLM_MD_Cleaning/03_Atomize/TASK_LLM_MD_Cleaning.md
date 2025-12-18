# TASK: LLM Markdown Cleaning (解析增强 - 结构化清洗)

## 1. 配置与基础
- [ ] **Task 1.1**: 更新 `src/core/config.py`。
    - 添加 `structure_cleaning` 默认配置。
    - 添加 getter/setter。
- [ ] **Task 1.2**: 创建 `src/core/structure_cleaner.py`。
    - 定义 `StructureCleaner` 类框架。
    - 实现 `_strip_markdown` (文本规范化) 逻辑。
    - 编写单元测试验证 `_strip_markdown` 的准确性 (确保能忽略格式差异但捕获内容差异)。

## 2. 核心逻辑实现
- [ ] **Task 2.1**: 实现 LLM 调用逻辑 `_call_llm`。
    - 使用 `httpx`。
    - 实现重试机制 (可选)。
- [ ] **Task 2.2**: 实现完整流程 `clean_markdown`。
    - 读取 -> LLM -> 校验 -> 写入。
    - 添加详细日志。

## 3. 集成
- [ ] **Task 3.1**: 修改 `src/core/engine.py`。
    - 在 `convert_file` 流程末尾（图片识别之后）集成 `StructureCleaner`。
    - 确保异步调用的正确性（`process_markdown` 可能是同步包装异步，参考 `ImageRecognizer`）。

## 4. UI 实现
- [ ] **Task 4.1**: 修改 `src/gui/main.py`。
    - 重构 "解析增强" 页签布局。
    - 添加 "结构化清洗" 配置区。
    - 绑定 ConfigManager。

## 5. 验证与测试
- [ ] **Task 5.1**: 编写集成测试 `tests/test_structure_cleaning.py`。
    - Mock LLM 响应。
    - 测试 "内容一致" 场景 (Pass)。
    - 测试 "内容被篡改" 场景 (Fail & Rollback)。
- [ ] **Task 5.2**: 手动验证 (Run GUI)。
