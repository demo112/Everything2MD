# FINAL: 带上下文的图片解析

## 1. 项目总结

本项目成功实现了在图片解析过程中携带上下文信息的功能。通过提取图片周围的文本并将其作为 Context 发送给多模态 LLM，预期能显著提升图片描述的准确性和相关性。

## 2. 交付成果

1.  **代码变更**:
    -   `src/core/config.py`: 新增 `img_rec_context_length` 配置项。
    -   `src/core/image_recognition.py`: 
        -   修改 `_process_markdown_async` 实现上下文切片提取。
        -   修改 `_process_single_image` 接收 `context` 参数并注入 Prompt。

2.  **测试**:
    -   新增 `tests/test_image_context.py`，覆盖了核心逻辑。

3.  **文档**:
    -   完整的 6A 工作流文档。

## 3. 遗留问题与建议

-   目前上下文长度默认 500 字符，可能在某些 Token 限制较严格的模型上需要调整。
-   建议后续观察实际运行效果，收集用户反馈，看是否需要引入更复杂的上下文提取策略（如基于段落而非字符数）。
