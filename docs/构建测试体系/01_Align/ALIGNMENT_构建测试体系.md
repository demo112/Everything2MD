# ALIGNMENT: 构建完善的测试体系

## 1. 项目上下文分析
项目 `Everything2MD` 已经历了从 Shell 脚本向 Python Core (`src/core`) 的重构，并新增了 Tkinter GUI 和 RAGFlow 集成。
当前的测试体系较为分散：
*   **Shell 测试**: `test/unit/*.bats`, `test/integration/*.bats` (遗留，部分可能失效)。
*   **Python 测试**: `test/python/` (GUI逻辑, Web API), `test/unit/test_ragflow_client.py` (新增)。
*   **缺失部分**: 新的 Python Core (`ConfigManager`, `ConversionEngine`, `Converters`) 缺乏系统的单元测试。

## 2. 原始需求与理解
用户指出“很多功能有基础问题”，要求“构建完善的测试体系持续保证项目质量”。
这表明目前的测试覆盖率不足，且缺乏统一的运行机制，导致回归错误容易发生。

**核心目标**:
1.  **统一测试框架**: 以 `pytest` 为主导，整合所有 Python 测试。
2.  **补全单元测试**: 覆盖 `src/core` 下的核心组件。
3.  **完善集成测试**: 模拟真实转换流程。
4.  **提供便捷入口**: 能够一键运行所有测试。

## 3. 智能决策与策略

### 3.1 架构策略
*   **目录重构**: 将 `test/` 目录按功能重组，明确区分 `unit` (单元测试) 和 `integration` (集成测试)。
*   **Mock 策略**: 对外部依赖（如 LibreOffice, RAGFlow API）使用 `unittest.mock` 进行模拟，确保测试运行速度和独立性。
*   **Shell 兼容**: 保留 BATS 测试用于验证遗留 Shell 模块（如果还在使用），但重点转移到 Python 测试。

### 3.2 关键决策点
*   **GUI 测试**: 使用 Mock 模拟 Tkinter 行为，测试 ViewModel/Controller 逻辑，避免真实的 GUI 弹窗干扰自动化测试。
*   **Core 测试**: 重点测试 `ConversionEngine` 的调度逻辑和 `ConfigManager` 的读写逻辑。

## 4. 验收标准
1.  **目录结构清晰**: `test/` 目录下结构规范，易于扩展。
2.  **核心覆盖**: `src/core` (Config, Engine, Utils, RAGFlowClient) 单元测试覆盖率 > 80%。
3.  **运行便捷**: 提供 `run_tests.py` 或更新 `Makefile`，一键运行通过。
4.  **CI 友好**: 测试结果可输出为 JUnit XML 或 HTML 报告。
