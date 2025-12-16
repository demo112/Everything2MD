# 待办事项 (TODO)

## 1. 遗留问题
- **GUI 测试覆盖率**: 目前 `src/gui/main.py` 覆盖率为 71%，主要因为大量的 UI 布局代码难以通过单元测试覆盖。建议后续引入 UI 自动化测试工具（如 Sikuli 或 PyAutoGUI，虽然这通常属于集成测试范畴）。
- **Windows 注册表测试**: 虽然通过 Mock 覆盖了逻辑，但真实的注册表访问行为仅在 Windows 环境下有效，跨平台测试仍有局限性。

## 2. 后续建议
- **CI/CD 集成**: 将 `python run_tests.py` 集成到 GitHub Actions 或其他 CI 流程中，确保每次提交都不会降低覆盖率。
- **集成测试**: 增加端到端的集成测试，在真实环境（安装了 LibreOffice 和 Pandoc）中验证转换流程。
