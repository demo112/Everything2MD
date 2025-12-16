# FINAL_UI自动化测试

## 1. 项目总结
本项目成功引入了基于 `pywinauto` 的 UI 自动化测试框架，解决了 Tkinter 应用在 Windows 平台下缺乏真实交互测试手段的问题。

**主要产出**:
1.  **测试框架**: 建立了 `test/ui` 目录，配置了 `conftest.py` 处理应用生命周期。
2.  **核心 Fixtures**:
    -   `app_process`: 自动启动和清理应用进程。
    -   `main_window`: 自动连接到主窗口，支持精确标题匹配。
    -   `cleanup_processes`: 健壮的僵尸进程清理机制。
3.  **测试用例**: 实现了冒烟测试 (`test_launch.py`)。
4.  **构建集成**: 更新了 `run_tests.ps1`，支持一键运行 UI 测试。

## 2. 架构回顾
- **Driver Layer**: `pywinauto` (win32 backend) + `psutil`。
- **Test Layer**: `pytest` + Fixtures。
- **SUT**: `src/gui/main.py` (Tkinter)。

## 3. 下一步建议
- **扩展测试用例**: 编写完整的转换流程测试 (选择文件 -> 点击转换 -> 验证文件生成)。
- **CI/CD 集成**: 在 Windows Runner 上启用 UI 测试。
- **可访问性增强**: 在 GUI 代码中为关键控件添加 `name` 属性，提升自动化测试的稳定性。
