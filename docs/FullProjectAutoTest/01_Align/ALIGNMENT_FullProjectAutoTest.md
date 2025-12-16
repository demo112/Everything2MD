# 项目对齐文档 (ALIGNMENT)

## 1. 项目上下文分析

### 1.1 现有项目结构
项目 `Everything2MD` 旨在将各种文件格式转换为 Markdown。
- **核心逻辑 (`src/core`)**: 包含文件转换 (`converters`), 核心引擎 (`engine.py`), 配置管理 (`config.py`), RAGFlow 集成 (`ragflow_client.py`)。
- **GUI (`src/gui`)**: 基于 Tkinter 的图形界面。
- **Web (`web`)**: 简单的 Web 界面。
- **脚本模块 (`src/modules`)**: Shell 脚本，用于处理依赖和转换。
- **测试 (`test`)**: 包含单元测试 (`unit`) 和集成测试 (`integration`)。

### 1.2 现有测试状况
- **测试框架**: `pytest`, `pytest-cov`, `pytest-mock`, `pytest-asyncio`。
- **当前覆盖率 (2025-12-16)**:
    - 总覆盖率: **57%**
    - `src\core\converters\office.py`: 67%
    - `src\core\converters\ppt.py`: 85%
    - `src\core\engine.py`: 72%
    - `src\core\ragflow_client.py`: 53%
    - `src\core\utils.py`: 37%
    - `src\gui\main.py`: 50%
    - `src\core\config.py`: 82%

## 2. 需求理解与确认

### 2.1 目标
- **全项目自动化测试覆盖率**: > 80%
- **核心功能覆盖率**: 100%

### 2.2 核心功能定义
核心功能是指直接影响文件转换质量和系统稳定性的模块。
- `src/core/converters/*.py` (所有转换器)
- `src/core/engine.py` (转换引擎)
- `src/core/config.py` (配置管理)
- `src/core/ragflow_client.py` (RAGFlow 集成)

### 2.3 任务边界
- 重点提升 Python 代码 (`src/core`, `src/gui`) 的测试覆盖率。
- Shell 脚本 (`src/modules`) 由于环境限制（Windows），主要通过 Python 集成测试或 Mock 来验证其调用逻辑，不强求在 Windows 下直接运行 BATS 测试，但需确保逻辑被覆盖。
- GUI 测试主要覆盖逻辑层，对于纯界面展示（Tkinter loop）可适当放宽，但核心回调逻辑需覆盖。

## 3. 智能决策策略

### 3.1 歧义与风险
- **环境依赖**: Office 转换依赖 LibreOffice/Pandoc，测试环境中可能不存在。
    - *策略*: 使用 `pytest-mock` 模拟外部命令调用，确保逻辑覆盖率达到 100%，同时保留跳过实际转换的集成测试（当环境不满足时）。
- **GUI 测试**: Tkinter 在无头环境（Headless）下可能难以测试。
    - *策略*: 将 GUI 逻辑与界面分离，重点测试逻辑类/函数。对于界面交互，使用 Mock 对象。

### 3.2 问题清单
1. 是否需要在 CI/CD 中运行测试？(当前仅本地运行) -> 假设本地运行。
2. 对于 `src/modules` 下的 Shell 脚本，是否需要编写对应的 Python 测试来模拟调用？ -> 是，确保 Python 调用 Shell 脚本的逻辑被覆盖。

## 4. 最终共识
- **目标**: 提升 `src` 目录下的 Python 代码覆盖率。
- **手段**: 补充单元测试，大量使用 Mock 解除环境依赖。
- **验收标准**:
    - `src/core` 下所有文件覆盖率 100%。
    - `src/gui` 覆盖率提升至 > 60% (重点覆盖逻辑)。
    - `src` 整体覆盖率 > 80%。
    - 所有测试通过 (`pytest` 运行无失败)。
