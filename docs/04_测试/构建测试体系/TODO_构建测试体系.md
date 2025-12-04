# TODO_构建测试体系

## 待办事项列表

1.  **CI/CD 集成**
    - [ ] 创建 `.github/workflows/test.yml`。
    - [ ] 在 CI 环境中安装 Bats 和 Python 依赖。

2.  **测试覆盖率提升**
    - [ ] 增加 `src/modules/config_migrator.py` 的测试。
    - [ ] 增加更多边缘情况的测试（如文件权限错误）。

3.  **Shell 测试增强**
    - [ ] 确保 Bats 测试在 Windows 环境下的稳定性（依赖 Bash 环境，如 Git Bash）。

4.  **文档完善**
    - [ ] 在 `README.md` 中添加测试运行指南。
