# FINAL: Enhance Image Parsing Logs (完善图片解析日志)

## 1. Project Summary
本任务旨在完善图片解析功能的日志记录，以便于用户感知进度和开发者排查问题。通过修改 `src/core/image_recognition.py`，我们实现了详细的进度、耗时和错误日志。

## 2. Key Changes
-   **Progress Tracking**: 在 `_process_markdown_async` 中计算图片总数，并传递给处理函数。
-   **Detailed Logging**:
    -   `[Index/Total] Processing image: Name...`
    -   `[Index/Total] Successfully processed Name in X.XXs.`
-   **Robust Error Handling**: 专门捕获 `httpx.HTTPStatusError` 以记录 API 返回的具体错误信息。

## 3. Quality Assessment
-   **Code Quality**: 代码保持了原有的异步结构，新增逻辑清晰，未引入复杂性。
-   **Test Coverage**: 通过模拟脚本验证了日志输出格式和逻辑的正确性。

## 4. Next Steps
-   **GUI Integration**: 确认 GUI 的日志窗口能够自动滚动显示最新的 INFO 日志。
-   **Token Usage**: 目前仅记录了耗时，未来如果 API 响应标准统一，可以解析并记录 Token 消耗。
