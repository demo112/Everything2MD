# DESIGN: Enhance Image Parsing Logs (完善图片解析日志)

## 1. Architecture Design
本次修改仅涉及 `src/core/image_recognition.py` 内部逻辑增强，不改变模块间接口或整体架构。

### 1.1 Modified Components
-   **`ImageRecognizer` class**:
    -   `_process_markdown_async`: 负责分发任务，现在需要计算总数并传递进度信息。
    -   `_process_single_image`: 负责具体的 API 调用和日志记录。

## 2. Detailed Design

### 2.1 `_process_markdown_async`
-   **Logic**:
    -   获取 `matches` 后，计算 `total_images = len(matches)`。
    -   遍历 `matches` 时使用 `enumerate(matches, 1)` 获取 `index`。
    -   调用 `_process_single_image` 时，新增参数 `index` and `total_count`。

### 2.2 `_process_single_image`
-   **Signature**: `async def _process_single_image(self, image_path: Path, client: httpx.AsyncClient, semaphore: asyncio.Semaphore, index: int, total: int) -> str:`
-   **Logic**:
    1.  **Start Log**: `log_info(f"[{index}/{total}] Processing image: {image_path.name}...")`
    2.  **Timing**: `start_time = time.perf_counter()`
    3.  **API Call**:
        -   Existing logic to prepare payload.
        -   `response = await client.post(...)`
    4.  **Success Log**:
        -   `elapsed = time.perf_counter() - start_time`
        -   `log_info(f"[{index}/{total}] Successfully processed {image_path.name} in {elapsed:.2f}s.")`
    5.  **Error Handling**:
        -   `except httpx.HTTPStatusError as e`:
            -   `log_error(f"[{index}/{total}] API Error for {image_path.name}: Status {e.response.status_code}, Response: {e.response.text}")`
        -   `except Exception as e`:
            -   `log_error(f"[{index}/{total}] Error processing {image_path.name}: {e}")`

## 3. Data Flow
Markdown File -> Regex Match -> List of Images -> (Async Loop) -> [Log Start] -> API Request -> [Log End/Error] -> Description -> Markdown Update

## 4. Dependencies
-   `time`: Standard library, for timing.
-   `httpx`: Already used, for exception types.
