# TASK: 带上下文的图片解析

## 1. 配置更新
- [ ] **Task 1.1**: 更新 `src/core/config.py`，在默认配置中添加 `img_rec_context_length` (默认 500)，并确保可以通过 `ConfigManager` 读取。

## 2. 核心逻辑实现
- [ ] **Task 2.1**: 修改 `src/core/image_recognition.py` 中的 `_process_single_image` 方法，增加 `context` 参数，并在 Prompt 中加入 Context 信息。
- [ ] **Task 2.2**: 修改 `src/core/image_recognition.py` 中的 `_process_markdown_async` 方法，在遍历图片时计算上下文，并传递给 `_process_single_image`。

## 3. 验证与测试
- [ ] **Task 3.1**: 创建或更新单元测试 `tests/test_image_context.py`，验证：
    - 上下文提取逻辑正确（包括边界情况）。
    - Prompt 中正确包含了上下文。
