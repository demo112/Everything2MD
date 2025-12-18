# ALIGNMENT: 补充自动化测试用例

## 1. 项目上下文分析
- **现状**：项目包含核心文档转换功能（Office, PPT）和 RAGFlow 集成客户端。
- **问题**：目前 `tests/` 目录下仅有 `config_persistence`, `emmx`, `image_recognition` 的测试，核心转换逻辑和 RAGFlow 客户端缺乏测试覆盖。最近的修复（如 PPT 修复）需要回归测试保障。
- **目标**：为核心转换模块和 RAGFlow 客户端补充自动化测试用例，提高代码可靠性。

## 2. 需求理解确认
### 2.1 待测试模块
1.  **RAGFlowClient** (`src/core/ragflow_client.py`)
    -   功能：与 RAGFlow API 交互（列表、创建数据集、上传文档）。
    -   测试策略：使用 `unittest.mock` 模拟 `httpx.Client` 的响应，验证请求参数构建和响应处理逻辑。
2.  **PptConverter** (`src/core/converters/ppt.py`)
    -   功能：PPT/PPTX 转 Markdown/PDF。包含 `pptx2md` 调用和 LibreOffice 降级逻辑。
    -   测试策略：Mock `subprocess.run` 和 `subprocess.Popen`，验证命令构建逻辑；Mock `pptx2md` 模块验证调用逻辑。
3.  **OfficeConverter** (`src/core/converters/office.py`)
    -   功能：Office 文档转 Markdown/PDF。包含 LibreOffice 和 Pandoc 调用。
    -   测试策略：Mock `subprocess.run`，验证 LibreOffice 和 Pandoc 的命令参数。

### 2.2 边界确认
-   **不包含**：真实的 API 调用（不依赖外部 RAGFlow 服务）。
-   **不包含**：真实的 LibreOffice/Pandoc 执行（环境依赖太重，仅验证命令构建和异常处理）。
-   **包含**：正常流程、异常流程（网络错误、命令失败）、边界条件（空输入、文件不存在）。

## 3. 智能决策策略
-   **Mock 优先**：鉴于外部依赖（API, Office 软件）的不稳定性，单元测试应优先使用 Mock。
-   **Pytest 框架**：沿用项目现有的 `pytest` 框架。

## 4. 关键决策点
-   **Mock 深度**：是 Mock 整个 `httpx` 库，还是 Mock `_handle_response`？
    -   *决策*：Mock `httpx.Client` 以验证 URL、Header 和 Params 是否正确。
-   **测试文件位置**：
    -   `tests/test_ragflow_client.py`
    -   `tests/test_ppt_converter.py`
    -   `tests/test_office_converter.py`

## 5. 最终共识
-   使用 `pytest` + `unittest.mock`。
-   覆盖 `RAGFlowClient`, `PptConverter`, `OfficeConverter`。
-   重点覆盖异常处理逻辑。
