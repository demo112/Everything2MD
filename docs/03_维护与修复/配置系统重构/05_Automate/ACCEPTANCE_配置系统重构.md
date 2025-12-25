# ACCEPTANCE_配置系统重构

## 任务执行记录

### TASK-001: 重构 ConfigManager
- [x] **执行状态**: 已完成
- [x] **代码变更**: `src/core/config.py` 引入 `_get_config_mapping`，重构 `get/set`。
- [x] **验证**: 单元测试 `test_config_manager_mapping` 通过。

### TASK-002: 重构 GUI 绑定
- [x] **执行状态**: 已完成
- [x] **代码变更**: `src/gui/main.py` 引入 `_init_config_bindings`，重构 `load_config/save_config`。
- [x] **验证**: 单元测试 `test_gui_binding` 通过。结构化清洗配置可正常保存和加载。

### TASK-003: 端到端验证
- [x] **执行状态**: 已完成
- [x] **验证结果**: `tests/verify_config_persistence.py` 运行成功，所有配置项持久化正常。
- [x] **兼容性**: 自动检测逻辑（Soffice/Pandoc）工作正常。

## 遗留问题
无。
