# CONSENSUS: 带上下文的图片解析

## 1. 需求共识

确认在图片识别流程中增加“上下文感知”能力。 具体而言，将 Markdown 文档中图片引用位置前后的文本提取出来，作为辅助信息发送给多模态 LLM。

## 2. 规格说明

-   **上下文长度**: 默认提取前后各 500 字符。
-   **配置项**: 用户可在配置文件或 GUI（如果支持高级配置）中调整长度。目前先在 ConfigManager 中支持读取，GUI 暂不强制要求暴露此高级选项，除非用户有明确要求（本任务优先实现后端逻辑）。
-   **Prompt 变更**: `text     ...     - **Context**: The following text surrounds the image in the document:     """     [PREVIOUS TEXT]     ...     [NEXT TEXT]     """     Please use this context to better understand the image content.     ...`

## 3. 验收标准

1.  代码修改后，`image_recognition.py` 能正确提取上下文。
2.  发送给 LLM 的 Payload 中包含 Context 信息（可以通过日志或 Mock 测试验证）。
3.  现有功能（无上下文或上下文为空）不受影响。