# ALIGNMENT: Image Recognition (解析增强)

## 1. 项目背景

Everything2MD 是一个将各种文档格式（Office, PDF 等）转换为 Markdown 的工具。它目前支持：
- Office 转 MD (使用 LibreOffice/Pandoc/pptx2md)
- PDF 转 MD
- Web UI 和桌面 GUI

## 2. 需求理解

用户希望通过增加 **图片识别** 功能来增强转换过程。

### 2.1 功能需求

1.  **图片识别**: 在文件转 MD 的过程中，识别图片并使用多模态大模型 (Multimodal LLM) 生成描述。
2.  **配置**:
    -   用户提供 LLM 配置 (OpenAI 兼容: Base URL, API Key, Model Name)。
    -   并发设置 (最大并发图片请求数)。
3.  **并发**:
    -   LLM 每次请求处理一张图片。
    -   支持并发请求，上限由用户定义。
4.  **UI**:
    -   增加一个新的页签 "解析增强"。
    -   该页签将包含配置设置。
5.  **策略**:
    -   模仿 RAGFlow 的策略 (可能是: OCR/描述 -> 插入文本到 MD)。
    -   将解析后的文本插入到原始文档中 **图片所在的位置**。

### 2.2 技术约束

-   **Docker**: 如果在 Docker 中运行，必须重新构建/重启。
-   **环境**: Windows 主机，但 Docker 容器使用 Ubuntu。代码似乎支持两者。
-   **依赖**: `fastapi`, `uvicorn` (Web), `tkinter` (可能用于 `src/gui/main.py`)。

## 3. 歧义与疑问

1.  **UI 目标**: "新页签" 是指桌面 GUI (`src/gui/main.py`) 还是 Web UI (`web/`)？
    -   *假设*: 用户提到 "两个页签"。我将检查哪个界面符合此描述。
2.  **集成点**:
    -   对于 Office 文件，`pptx2md` 或 `pandoc` 可能会处理图片。
    -   如果 `pandoc` 提取图片，我们需要拦截它们或对 MD 进行后处理以查找图片链接，处理图片并插入文本。
    -   用户说 "插入在位置"。如果我们对 MD 进行后处理，我们可以找到 `![alt](path)` 标签并替换/追加描述。

## 4. 提议方案

1.  **配置**: 将 LLM 配置存储在新的配置部分。
2.  **UI**: 将 "解析增强" 页签添加到 GUI。
3.  **后端/核心**:
    -   创建 `ImageProcessor` 类。
    -   使用异步 LLM 调用实现 `process_image(image_path)`。
    -   修改转换管道:
        -   步骤 1: 转换文档 -> MD + 图片 (标准流程)。
        -   步骤 2: 扫描 MD 中的图片链接。
        -   步骤 3: 处理图片 (并发)。
        -   步骤 4: 更新 MD 并添加描述。

## 5. 参考经验 (来自 `docs/知识库检索效果对比`)

-   **洞察**: Markdown 丢失图片信息。PDF/多模态保留它。
-   **目标**: 通过将图片描述嵌入到 Markdown 中来弥补这一差距。
