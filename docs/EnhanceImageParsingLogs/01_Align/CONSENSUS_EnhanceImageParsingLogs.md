# CONSENSUS: Enhance Image Parsing Logs (完善图片解析日志)

## 1. 最终共识 (Final Consensus)
确认对 `src/core/image_recognition.py` 进行修改，以提供更详细的运行时日志。这对于排查 API 问题、监控处理进度以及优化性能至关重要。

### 1.1 日志规范
-   **开始处理**: INFO 级别，包含图片文件名和进度索引（例如 "Processing image 'pic1.png' (1/5)..."）。
-   **API 请求**: DEBUG 级别，记录发送请求时刻。
-   **成功响应**: INFO 级别，记录耗时（秒）和 Token 使用情况（如果 API 返回）。
-   **错误处理**: ERROR 级别，对于 HTTP 错误，必须记录状态码和响应体文本；对于其他错误，记录完整的异常信息。

### 1.2 技术实现
-   修改 `_process_markdown_async` 循环，使用 `enumerate` 获取索引，并将 `(index, total)` 传递给 `_process_single_image`。
-   在 `_process_single_image` 中使用 `time.perf_counter()` 计算耗时。
-   利用 `httpx` 的异常处理机制捕获详细的错误响应。

### 1.3 验收标准
-   运行图片解析时，日志窗口应清晰显示每张图片的开始和结束状态。
-   发生 API 错误时，日志中应能看到具体的错误原因（如 "401 Unauthorized"）。
-   正常处理结束时，应能看到总耗时信息（隐含在单张图片耗时中）。
