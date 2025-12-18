# ALIGNMENT: Image Recognition (解析增强)

## 1. Project Context
Everything2MD is a tool to convert various document formats (Office, PDF, etc.) into Markdown.
It currently supports:
- Office to MD (using LibreOffice/Pandoc/pptx2md)
- PDF to MD
- Web UI and Desktop GUI (to be confirmed which one is primary or if both need update)

## 2. Needs Understanding
The user wants to enhance the conversion process by adding **Image Recognition**.

### 2.1 Feature Requirements
1.  **Image Recognition**: During file->MD conversion, identify images and use a Multimodal LLM to generate descriptions.
2.  **Configuration**:
    -   User provides LLM config (OpenAI compatible: Base URL, API Key, Model Name).
    -   Concurrency settings (Max concurrent image requests).
3.  **Concurrency**:
    -   LLM processes one image at a time per request.
    -   Support concurrent requests up to the user-defined limit.
4.  **UI**:
    -   Add a new tab "解析增强" (Parsing Enhancement).
    -   This tab will contain the configuration settings.
5.  **Strategy**:
    -   Mimic RAGFlow's strategy (likely: OCR/Describe -> Insert text into MD).
    -   Insert the parsed text **at the location of the image** in the original document.

### 2.2 Technical Constraints
-   **Docker**: If running in Docker, must rebuild/restart.
-   **Environment**: Windows host, but Docker container uses Ubuntu. Code seems to support both.
-   **Dependencies**: `fastapi`, `uvicorn` (Web), `tkinter` (likely for `src/gui/main.py`).

## 3. Ambiguities & Questions
1.  **UI Target**: Is the "new tab" for the Desktop GUI (`src/gui/main.py`) or the Web UI (`web/`)?
    -   *Hypothesis*: The user mentioned "two tabs". I will check which interface fits this description.
2.  **Integration Point**:
    -   For Office files, `pptx2md` or `pandoc` might handle images.
    -   If `pandoc` extracts images, we need to intercept them or post-process the MD to find image links, process the images, and insert text.
    -   User said "insert at the location". If we post-process MD, we can find `![alt](path)` tags and replace/append the description.

## 4. Proposed Solution
1.  **Configuration**: Store LLM config in a new config section.
2.  **UI**: Add the "Parsing Enhancement" tab to the GUI.
3.  **Backend/Core**:
    -   Create an `ImageProcessor` class.
    -   Implement `process_image(image_path)` using async LLM calls.
    -   Modify conversion pipeline:
        -   Step 1: Convert Doc -> MD + Images (standard).
        -   Step 2: Scan MD for image links.
        -   Step 3: Process images (concurrently).
        -   Step 4: Update MD with descriptions.

## 5. Reference Experience (from `docs/知识库检索效果对比`)
-   **Insight**: Markdown loses image info. PDF/Multimodal retains it.
-   **Goal**: Bridge this gap by embedding image descriptions into the Markdown.
