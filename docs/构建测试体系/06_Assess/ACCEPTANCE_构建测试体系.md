# ACCEPTANCE: 构建完善的测试体系

## 1. 验收概览
| 验收项 | 状态 | 说明 |
| :--- | :--- | :--- |
| 测试目录重构 | ✅ 已完成 | `test/unit`, `test/integration` 结构清晰 |
| 核心单元测试 | ✅ 已完成 | `ConfigManager`, `ConversionEngine` 测试通过 |
| 集成测试 | ✅ 已完成 | `test_full_conversion_flow` 验证了从文件到引擎的流程 |
| 运行便捷性 | ✅ 已完成 | `python run_tests.py` 一键运行 |
| 覆盖率报告 | ✅ 已完成 | 生成 HTML 报告，当前总覆盖率 48% |

## 2. 详细验收记录

### Task 1: 目录结构
- [x] `test/unit/core` 包含 Config, Engine, Utils, RAGClient 测试。
- [x] `test/unit/gui` 包含 GUI 逻辑测试。
- [x] `test/integration` 包含 Web API 和 文件流测试。
- [x] `pytest.ini` 和 `conftest.py` 配置正确。

### Task 2: 单元测试
- [x] `test_config.py`: 修复了 `ConfigManager` 初始化参数问题，测试通过。
- [x] `test_engine.py`: 修复了 `convert_file` 返回值断言和 Mock 缩进问题，测试通过。
- [x] `test_gui_logic.py`: 修复了 Mock 断言和路径 Mock 问题，测试通过。

### Task 3: 集成测试
- [x] `test_web_api.py`: 修复了 Mock `config_manager` 的问题，测试通过。
- [x] `test_conversion_flow.py`: 验证了 .txt 转换流程。

## 3. 遗留问题与改进
- **覆盖率**: 当前 48% 的覆盖率主要受限于 `src/modules` (Shell脚本) 未计入 Python 覆盖率，以及 `office.py` / `ppt.py` 的外部工具调用未完全覆盖。
- **GUI 测试**: 仅测试了逻辑，未进行端到端 UI 点击测试（符合策略）。
