# ACCEPTANCE_SystemTestSubsystem

| 任务 ID | 描述 | 状态 | 备注 |
| :--- | :--- | :--- | :--- |
| T1 | 标准化目录结构 | Completed | `tests/` 已迁移至 `test/integration/` |
| T2 | 优化测试脚本 | Completed | `scripts/run_tests.ps1` 已更新支持 `.venv` 和 Git Bash 检测 |
| T3 | 执行全量系统测试 | Completed | Python 测试全部通过 (118/118) |
| T4 | 修复发现的问题 | Completed | 修复了缺失的 `pytest-cov`, `pytest-mock` 依赖 |
