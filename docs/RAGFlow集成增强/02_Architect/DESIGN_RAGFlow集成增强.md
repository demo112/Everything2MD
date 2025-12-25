# DESIGN: RAGFlow集成增强

## 1. 系统架构

### 1.1 模块依赖
```mermaid
graph TD
    GUI[GUI (Tkinter)] --> Engine[ConversionEngine]
    GUI --> RAG[RAGFlowClient]
    Engine --> FS[FileSystem]
    RAG --> API[RAGFlow API]
    GUI --> Config[ConfigManager]
```

### 1.2 核心组件设计

#### 1.2.1 `src/core/ragflow_client.py`
负责所有与 RAGFlow 的网络交互。
*   **方法**:
    *   `list_datasets(page=1, page_size=100)`: 获取知识库列表。
    *   `create_dataset(name, template_id)`: 创建知识库。
    *   `upload_document(dataset_id, file_path)`: 上传文件。
    *   `parse_documents(dataset_id, doc_ids)`: 启动解析。

#### 1.2.2 `src/gui/main.py` (GUI重构)
*   引入 `ttk.Notebook`。
*   **Tab 1: 转换控制**: 原有的输入输出配置、开始按钮、日志显示。
*   **Tab 2: RAGFlow 分发**:
    *   **Config Area**: API Base URL, API Key (带掩码显示/隐藏切换)。
    *   **Control Area**: 
        *   KB Dropdown (Combobox).
        *   Buttons: "Refresh KB", "New KB", "Upload Selected".
    *   **File List**: `ttk.Treeview`
        *   Columns: File Name, Convert Status, Upload Status, Info.
*   **交互逻辑**:
    *   `on_conversion_progress`: 更新 Tab 1 进度条。
    *   `on_file_converted(file_path)`: 在 Tab 2 的 Treeview 中添加一行，状态为 "Ready"。
    *   `on_upload_click`: 获取 Treeview 中选中的文件 -> 异步调用 `RAGFlowClient.upload` -> 更新 Treeview 状态。

## 2. 接口定义

### 2.1 `RAGFlowClient`
```python
class RAGFlowClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def list_datasets(self, page=1, page_size=100) -> dict:
        """返回知识库列表"""
        pass

    def create_dataset(self, name: str, template_id: str = None) -> str:
        """创建知识库，返回 id"""
        pass

    def upload_document(self, dataset_id: str, file_path: str) -> str:
        """上传文件，返回 doc_id"""
        pass
        
    def run_parsing(self, dataset_id: str, doc_ids: list[str]):
        """启动解析"""
        pass
```

## 3. 异常处理
*   **网络错误**: 捕获 `httpx.RequestError`，在 GUI 中弹窗提示或在状态栏显示红字。
*   **API 错误**: 解析响应 JSON，非成功状态码则报错。
*   **部分失败**: 批量上传时，单个失败不影响整体，Treeview 中标记该行为 "Failed"。

## 4. 安全性
*   API Key 不在日志中打印。
*   上传时仅读取指定文件。
