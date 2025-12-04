# ALIGNMENT_构建测试体系

## 1. 原始需求与边界确认
**需求描述**：构造项目的接口测试、单元测试体系。

**核心目标**：
1. 为现有的 Python 代码（Web Backend, GUI Logic）建立自动化测试。
2. 整合或完善现有的 Shell 脚本测试（Bats）。
3. 确保测试体系符合 6A 工作流标准。
4. 使用 pytest 作为 Python 测试框架。

**边界**：
- **包含**：
  - Web 后端接口测试 (FastAPI)。
  - 核心业务逻辑单元测试。
  - 测试环境搭建与配置。
- **不包含**：
  - 复杂的 GUI 交互自动化测试（Tkinter 自动化成本高，优先测试逻辑）。
  - 对第三方工具（Pandoc, LibreOffice）本身的测试（仅测试调用封装）。

## 2. 项目现状分析
**现有结构**：
- `web/backend/main.py`: FastAPI 应用，提供配置管理和 WebSocket 日志。
- `src/gui/main.py`: Tkinter GUI，包含部分配置管理和子进程调用逻辑。
- `src/modules/*.sh`: 核心业务逻辑脚本。
- `test/`: 现有的 Bats 测试集。

**技术栈**：
- Python 3.x (FastAPI, Tkinter)
- Shell (Bash)
- Testing: Bats (Shell), Pytest (Python - 待集成)

## 3. 歧义澄清 (Q&A)
- **Q**: 是否需要测试 GUI 界面点击？
  - **A**: 考虑到 ROI，优先测试 GUI 背后的逻辑函数和 Web API。GUI 界面测试可作为后续增强。
- **Q**: Shell 脚本测试是否需要迁移到 Python？
  - **A**: 不需要。保留 Bats 测试，Python 测试主要针对 Python 代码。
