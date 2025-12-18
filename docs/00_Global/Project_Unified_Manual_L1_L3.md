# Everything2MD 项目统一文档 (Unified Project Manual)

> **版本**: 1.0.0
> **生成日期**: 2025-12-18
> **覆盖范围**: L1 (用户), L2 (架构), L3 (开发)

---

# 第一部分：L1 用户指南 (User Guide)

## 1.1 项目简介
Everything2MD 是一个全能的文档转换工具，致力于将各类办公文档（Word, Excel, PPT, PDF）高效转换为 Markdown 格式，便于知识管理和 AI 知识库构建。

**核心特性**:
*   **多格式支持**: Office (.doc, .docx, .ppt, .pptx, .xls, .xlsx), PDF, Images.
*   **双模式运行**: 
    *   **GUI 界面**: 图形化操作，简单直观。
    *   **命令行 (CLI)**: 适合服务器部署和批量脚本处理。
*   **Docker 支持**: 提供开箱即用的 Docker 镜像，免去繁琐的环境配置。

## 1.2 快速开始

### 方式一：Docker 运行 (推荐)
最简单的使用方式，无需安装本地依赖。

```bash
# 1. 下载 Docker 资源
git clone https://github.com/your-repo/Everything2MD.git
cd Everything2MD

# 2. 启动服务 (需配置 .env 文件，参考 docker_resources/ 目录)
docker-compose up -d
```

### 方式二：Windows 本地运行
直接运行打包好的可执行文件（如果有）或通过 Python 源码运行。

**源码运行前置要求**:
*   Python 3.10+
*   LibreOffice (必须安装并添加到 PATH)
*   Pandoc (必须安装)

```powershell
# 1. 安装依赖
python -m pip install -r requirements.txt

# 2. 启动 GUI
python src/gui/main.py

# 3. 启动 CLI 批量转换
# (需 Git Bash 或 WSL 运行 shell 脚本，或使用 Python 对应入口)
bash src/main.sh -i "C:\MyDocs" -o "C:\Output"
```

## 1.3 功能操作说明

### Web GUI 界面
1.  启动程序后，浏览器访问 `http://localhost:8000` (如果配置了 Web 服务) 或直接操作桌面窗口。
2.  点击 **"选择文件/目录"** 按钮导入文档。
3.  点击 **"开始转换"**。
4.  转换完成后，可在右侧预览或点击 **"打开输出目录"**。

### 命令行 (CLI) 参数
*   `-i, --input`: 输入文件或目录路径。
*   `-o, --output`: 输出文件或目录路径。
*   `-b, --batch`: 强制启用批量模式。

---

# 第二部分：L2 系统架构 (System Architecture)

## 2.1 架构概览
Everything2MD 采用 **混合架构 (Hybrid Architecture)**，结合了 Shell 脚本的灵活性（用于 CLI 编排）和 Python 的强大生态（用于 GUI、复杂逻辑及 Web 服务）。

```mermaid
graph TD
    User[用户] -->|CLI| Shell[Shell Entry (src/main.sh)]
    User -->|GUI| PyGUI[Python GUI (src/gui/main.py)]
    
    subgraph "Core Logic (Python)"
        Engine[Conversion Engine]
        Detect[Type Detection]
        Config[Config Manager]
    end
    
    subgraph "Shell Modules"
        ModArgs[Arg Parser]
        ModDetect[File Detector]
        ModConv[Converters (Wrappers)]
    end
    
    Shell --> ModArgs
    Shell --> ModDetect
    Shell --> ModConv
    
    PyGUI --> Config
    PyGUI --> Engine
    Engine --> Detect
    
    subgraph "External Tools"
        Libre[LibreOffice]
        Pandoc[Pandoc]
        PPTX[pptx2md]
    end
    
    ModConv --> Libre
    ModConv --> Pandoc
    Engine --> Libre
    Engine --> Pandoc
```

## 2.2 核心流程

### 2.2.1 转换流水线
无论是 CLI 还是 GUI，核心转换逻辑遵循以下步骤：
1.  **输入接收**: 接收文件路径或目录。
2.  **类型检测 (Detection)**: 
    *   通过后缀名或 `file` 命令判断文件类型。
    *   分类为: `office`, `ppt`, `pdf`, `text`, `image` 等。
3.  **路由分发 (Routing)**:
    *   `Office/PDF` -> `LibreOffice` 转 PDF/HTML -> `Pandoc` 转 Markdown。
    *   `PPTX` -> `pptx2md` 直接提取。
    *   `Images` -> `OCR Engine` (如果有)。
4.  **后处理 (Post-processing)**:
    *   图片资源提取与路径修正。
    *   Markdown 格式清理 (去除冗余空行等)。

### 2.2.2 Docker 设计
*   **Base Image**: 基于 `python:3.10-slim` 或包含 LibreOffice 的基础镜像。
*   **Volumes**: 映射宿主机目录以读取输入和写入输出。
*   **Env**: 通过环境变量配置 `TZ`, `LANG` 等。

---

# 第三部分：L3 开发指南 (Developer Guide)

## 3.1 代码结构 (Code Structure)

```text
Everything2MD/
├── src/
│   ├── core/                 # Python 核心逻辑
│   │   ├── converters/       # 具体转换器实现 (Office, PPT, EMMX)
│   │   ├── engine.py         # 转换引擎入口
│   │   └── config.py         # 配置管理
│   ├── gui/                  # Python GUI 实现 (Tkinter/PyQt)
│   ├── modules/              # Shell 脚本模块 (CLI 功能)
│   │   ├── libreoffice_converter.sh
│   │   └── ...
│   ├── main.sh               # CLI 入口脚本
│   └── filters/              # Pandoc Lua 过滤器
├── test/                     # 测试集合
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── fixtures/             # 测试用例文件
└── docs/                     # 项目文档
```

## 3.2 核心类定义 (Core API)

### `src.core.engine.ConversionEngine`
负责协调转换任务的执行。

*   `__init__(config_manager)`: 初始化引擎。
*   `detect_type(path) -> str`: 检测文件类型。
*   `convert_file(input_path, output_path, callback) -> Path`: 执行单个文件转换。

### `src.core.converters.base.BaseConverter`
所有转换器的抽象基类。

*   `convert(input_path, output_path, **kwargs) -> Path`: 必须实现的抽象方法。

## 3.3 开发规范

### 6A 工作流
本项目严格遵循 6A 工作流（Align, Architect, Atomize, Approve, Automate, Assess）。任何功能变更需先更新 `docs/` 下的对应文档。

### 测试要求
*   **工具**: `pytest` (Python), `bats` (Shell).
*   **覆盖率**: 新增功能必须包含单元测试。
*   **运行方式**:
    ```bash
    # 运行所有测试
    pytest
    
    # 运行 Shell 测试
    ./test/bats/bin/bats test/integration/
    ```

### 日志规范
系统必须具备全链路日志记录能力。Python 使用 `src.core.utils` 中的日志函数，Shell 使用 `modules/logger.sh`。

---
*End of Document*
