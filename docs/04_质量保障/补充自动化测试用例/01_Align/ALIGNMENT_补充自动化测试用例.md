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

## 4. 需求分析 (Updated)
### 4.1 原始需求
- 为核心功能模块（RAGFlowClient, Converters）补充自动化测试用例。
- **新增需求 (v1.1)**: 用户反馈新增功能覆盖不够，经分析主要指 GUI 层 (`src/gui/main.py`) 缺乏测试覆盖 (目前 0%)。

### 4.2 范围界定
- **In Scope**:
    - `src/core/ragflow_client.py`: API 交互逻辑 (已完成)
    - `src/core/converters/`: 转换器核心逻辑 (已完成)
    - `src/gui/main.py`: 
        - 配置加载与保存逻辑
        - 按钮事件绑定的业务逻辑调用 (如触发转换、连接 RAGFlow)
        - 界面状态更新逻辑 (Mock Tkinter)
- **Out of Scope**:
    - 真实的 UI 渲染测试 (Pixel-perfect testing)
    - `tkinter` 库本身的测试

### 4.3 关键挑战与策略
- **挑战**: GUI 代码强依赖 `tkinter`，在无头环境难以运行。
- **策略**: 使用 `unittest.mock` 对 `tkinter` 进行全面 Mock，将 UI 组件视为“黑盒”，只验证 Controller 层的逻辑（即 ViewModel 逻辑）。

## 5. 最终共识
-   使用 `pytest` + `unittest.mock`。
-   覆盖 `RAGFlowClient`, `PptConverter`, `OfficeConverter`。
-   重点覆盖异常处理逻辑。
