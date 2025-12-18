# TASK: Image Recognition (解析增强)

## 1. Dependency & Configuration

-   [ ] **Task 1.1**: Update `requirements.txt` (Ensure `httpx` is present, usually is).
-   [ ] **Task 1.2**: Update `src/core/config.py`.
    -   Add `image_recognition` defaults in `get_default_config`.
    -   Add getters/setters for new keys.

## 2. Core Implementation

-   [ ] **Task 2.1**: Create `src/core/image_recognition.py`.
    -   Implement `ImageRecognizer` class.
    -   Implement `recognize_image` using `httpx` (Async).
    -   Implement `process_markdown` (Sync wrapper managing async loop).
    -   Implement Markdown regex parsing and replacement.
    -   **Prompt Strategy**: Update system prompt to output structured data (Visual Type, Title, Data Points, Trends).
    -   **Injection Format**: Handle multi-line structured descriptions with blockquote prefixes.

## 3. Integration

-   [ ] **Task 3.1**: Modify `src/core/engine.py`.
    -   Import `ImageRecognizer`.
    -   In `convert_file`, add logic to call `process_markdown` after conversion if enabled.

## 4. User Interface

-   [ ] **Task 4.1**: Modify `src/gui/main.py`.
    -   Add `init_parsing_tab` method.
    -   Create "解析增强" tab in Notebook.
    -   Add widgets for Enabled, API Base, API Key, Model, Max Jobs.
    -   Bind widgets to `ConfigManager`.

## 5. Verification

-   [ ] **Task 5.1**: Create test script `tests/test_image_recognition.py`.
    -   Mock `httpx` response.
    -   Test Markdown parsing and injection.
-   [ ] **Task 5.2**: Manual verification with GUI.