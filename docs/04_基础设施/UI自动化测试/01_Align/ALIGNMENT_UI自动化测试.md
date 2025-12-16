# ALIGNMENT_UI自动化测试

## 1. 项目上下文分析

### 1.1 现有架构
- **GUI 框架**: Python Tkinter (`src/gui/main.py`)
- **运行环境**: Windows (主要), Linux/macOS (兼容)
- **现有测试**:
    - `test/python/test_web_api.py`: FastAPI 接口测试
    - `test/python/test_gui_logic.py`: GUI 逻辑层单元测试 (Mock 了 tkinter)
    - `test/bats/*.bats`: Shell 脚本集成测试
- **依赖管理**: `requirements.txt`

### 1.2 需求理解
- **目标**: 引入 UI 自动化测试框架。
- **核心要求**: 覆盖**真实的用户交互场景**。
- **用户建议**: 提到了 `pytest-qt` 作为示例。

## 2. 关键发现与冲突
- **冲突点**: 用户提到的 `pytest-qt` 是专为 PyQt/PySide (Qt 框架) 设计的测试插件，而本项目当前使用的是 **Tkinter** 框架。
- **结论**: 无法直接使用 `pytest-qt`。必须选择适配 Tkinter 且能模拟真实交互的框架。

## 3. 智能决策策略 (待确认)

为了满足“覆盖真实用户交互场景”的需求，针对 Tkinter + Windows 环境，有以下备选方案：

### 方案 A: 使用 pywinauto (推荐)
- **原理**: 使用 Windows UI Automation (UIA) 或 Win32 API 直接控制应用程序窗口。
- **优点**:
    - **最真实**: 模拟操作系统级别的鼠标点击和键盘输入，完全模拟用户行为。
    - **黑盒测试**: 不需要侵入源代码，测试已打包的 exe 或运行中的进程。
    - **Windows 友好**: 在 Windows 平台上表现极佳。
- **缺点**: 跨平台支持较弱 (Linux 上需要 at-spi)。

### 方案 B: Tkinter 原生事件模拟
- **原理**: 使用 Tkinter 的 `widget.event_generate()` 方法在代码层面触发事件。
- **优点**: 跨平台，运行速度快，无需额外安装重型依赖。
- **缺点**: 属于“灰盒/白盒”测试，不够“真实”（绕过了 OS 的输入驱动层）。

### 方案 C: 图像识别 (PyAutoGUI / Sikuli)
- **原理**: 基于屏幕截图匹配坐标。
- **缺点**: 极不稳定，维护成本高，强烈不推荐。

## 4. 疑问澄清与决策点 (Q&A)

### Q1: 确认测试框架选型
鉴于项目使用 Tkinter，且要求“真实交互”，**建议采用 `pytest` + `pywinauto`**。
- `pytest`: 作为测试运行器和断言库（符合项目现有规范）。
- `pywinauto`: 作为 UI 驱动层，启动应用并模拟点击。

**请确认**: 是否同意使用 `pywinauto` 替代用户提到的 `pytest-qt`？

### Q2: 测试范围
- **范围**: 启动应用 -> 设置路径 -> 点击转换 -> 验证结果文件。
- **前置条件**: 需要在测试环境中构建出可执行文件或直接通过 Python 启动进程。

## 5. 初始规范 (Draft)
- **测试目录**: `test/ui/`
- **文件命名**: `test_e2e_*.py`
- **依赖**: `pytest`, `pywinauto`, `psutil`
