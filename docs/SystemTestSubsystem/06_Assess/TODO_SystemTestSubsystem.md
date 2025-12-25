# TODO_SystemTestSubsystem

## 待办事项

1.  **安装 Git Bash**: 为了运行 Bats 测试（Shell 脚本测试），请在宿主机安装 Git Bash。安装后 `run_tests.ps1` 将自动检测并使用它。
2.  **提升覆盖率**: `src\core\image_recognition.py` 的测试覆盖率仅为 14%，建议增加针对 OCR 和图像处理的测试用例。
3.  **持续集成**: 建议将 `scripts/run_tests.ps1` 集成到 CI/CD 流程中，确保每次提交都进行自动化验证。
