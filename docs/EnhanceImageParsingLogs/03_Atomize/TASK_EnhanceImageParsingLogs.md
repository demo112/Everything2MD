# TASK: Enhance Image Parsing Logs (完善图片解析日志)

## 1. Task Breakdown

### Task 1: Update `_process_markdown_async` Signature & Logic
-   **Goal**: Calculate total image count and pass index to worker method.
-   **Input**: `src/core/image_recognition.py`
-   **Implementation**:
    -   In `_process_markdown_async`, iterate with `enumerate`.
    -   Update `_process_single_image` call to include `index` and `len(matches)`.

### Task 2: Enhance `_process_single_image` Logging
-   **Goal**: Add timing, progress, and detailed error logging.
-   **Input**: `src/core/image_recognition.py`
-   **Implementation**:
    -   Update method signature to accept `index` and `total`.
    -   Import `time` module.
    -   Add `log_info` at start and success.
    -   Add specific `try-except` for `httpx.HTTPStatusError` to log response body.
    -   Ensure generic exceptions are still caught.

## 2. Dependencies
-   Task 2 depends on Task 1 (signature change).

## 3. Verification
-   Run the application, configure a dummy or real API key.
-   Process a document with images.
-   Check logs for:
    -   "[1/N] Processing..."
    -   "[1/N] Successfully processed ... in X.XXs"
    -   (Optional) Trigger an error (invalid key) and check for detailed error log.
