# 项目治理共识文档 (CONSENSUS)

## 1. 核心目标
构建一个清晰、统一、高质量的项目全景视图，并清理历史债务（测试目录冗余）。

## 2. 执行方案

### 2.1 文档整理 (Documentation)
*   **保留**：`docs/01_核心系统`, `02_功能模块`, `03_维护与修复` 现有层级。
*   **新增**：`docs/00_Global` 用于存放整体项目文档。
*   **输出**：`docs/00_Global/Project_Unified_Manual.md`。
    *   **Part 1 (L1 User)**: 安装指南、功能清单、使用手册（Web/CLI）、配置说明。
    *   **Part 2 (L2 Architect)**: 系统架构图、模块依赖、数据流、Docker设计。
    *   **Part 3 (L3 Developer)**: 目录结构说明、核心类/函数签名、开发规范、测试指南。

### 2.2 测试系统重构 (Testing)
*   **合并**：将 `tests/*.py` 移动到 `test/unit/legacy_tests/` (或具体对应模块)，初步隔离，确保 `pytest` 能发现。
*   **配置**：更新 `pytest.ini` 确保包含新路径（如果 `testpaths = test` 则自动包含）。
*   **验证**：运行全量测试，修复因路径变更导致的 import 错误。

### 2.3 代码与一致性 (Consistency)
*   **同步**：检查 `src/core` 核心逻辑与 `DESIGN` 文档的一致性。
*   **规范**：统一 Python 代码风格 (black/flake8 检查，如果环境有)。

## 3. 任务边界
*   **不包含**：大规模重写现有业务逻辑（仅限于为了测试通过而做的最小修复）。
*   **包含**：文档生成、测试目录合并、全量回归测试。

## 4. 验收标准
1.  `tests/` 文件夹不存在。
2.  `pytest` 运行结果 All Passed (允许少量 Skip，不允许 Fail)。
3.  `Project_Unified_Manual.md` 存在且内容完整（覆盖 L1-L3）。
