# ALIGNMENT: Enhance Image Parsing Logs (完善图片解析日志)

## 1. Project Context
Everything2MD 的图片解析功能使用多模态大模型 (如 GPT-4 Vision) 为文档中的图片生成描述。当前实现位于 `src/core/image_recognition.py`。
目前的日志记录较少，仅包含：
- 开始识别（图片总数）
- 找不到图片警告
- 图片编码错误
- API 请求异常
- 完成更新

## 2. Needs Understanding (需求理解)
用户希望“完善图片解析的日志功能”。这通常意味着需要更多的运行时信息来帮助：
1.  **故障排查**: 当解析失败或卡住时，知道具体卡在哪张图片，或者是因为网络/API 限制。
2.  **进度感知**: 在处理大量图片时，知道当前进度。
3.  **成本/性能监控**: 了解 API 耗时和可能的 Token 消耗。

### 2.1 Feature Requirements (功能需求)
1.  **详细的单图处理日志**:
    -   开始处理图片 (Info/Debug)
    -   图片编码成功 (Debug)
    -   API 请求发送 (Debug)
    -   API 响应接收 (含耗时) (Info)
    -   API 响应内容摘要 (Debug)
2.  **错误处理增强**:
    -   HTTP 错误时，记录状态码和响应内容（如果 API 返回了错误详情）。
    -   区分网络超时、认证失败、模型错误等。
3.  **进度反馈**:
    -   虽然 `asyncio.gather` 并发执行，但可以在每个任务完成时记录进度（例如 "Finished image X/N"）。

### 2.2 Technical Constraints (技术约束)
-   **LogManager**: 使用现有的 `src.core.utils.log_info` 等函数。
-   **Concurrency**: 保持现有的 `asyncio` 并发结构，日志应包含足够上下文（如图片文件名）以区分不同任务。
-   **Performance**: 日志记录不应显著影响性能（虽然 IO 密集型任务影响不大）。

## 3. Ambiguities & Uncertainties (歧义与不确定性)
-   **日志级别**: 详细日志是否应该默认为 INFO 级别？
    -   *决策*: 关键节点（如每张图片处理完成）设为 INFO，详细调试信息（如 Base64 长度、完整 Prompt）设为 DEBUG。
-   **UI 显示**: GUI 是否能显示所有 INFO 日志？
    -   *假设*: GUI 的日志窗口会显示 INFO 级别以上的日志。因此 INFO 日志不宜过多刷屏，但每张图片一行是可以接受的。

## 4. Decision Strategy (决策策略)
-   **进度日志**: 在 `_process_single_image` 成功或失败返回前记录。
-   **耗时统计**: 使用 `time.perf_counter()` 记录 API 调用耗时。
-   **错误详情**: `httpx.HTTPStatusError` 包含 `response` 对象，可以读取 text。
