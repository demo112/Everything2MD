# ACCEPTANCE_UI自动化测试

## 1. 验收项核对
- [x] **框架安装**: `requirements.txt` 已包含 `pywinauto` 和 `psutil`。
- [x] **测试通过**: `test/ui/test_launch.py` 成功运行。
  - 应用启动测试 (Pass)
  - 界面元素存在性测试 (Pass)
- [x] **文档完整**: 
  - `01_Align`: 需求与方案确认 (选定 pywinauto)。
  - `02_Architect`: 架构设计与目录结构。
  - `03_Atomize`: 任务拆分与执行。
- [x] **集成构建**: `run_tests.ps1` 支持 `test-ui` 参数。

## 2. 执行结果记录
- **测试环境**: Windows (Tkinter + pywinauto 0.6.9)。
- **测试覆盖**: 
  - 应用启动/关闭生命周期管理 (Fixtures)。
  - 进程清理 (避免僵尸进程)。
  - 窗口标题识别与连接。

## 3. 遗留问题与改进
- **元素定位**: 目前仅依赖 `title` 和粗粒度的 `best_match`。后续随着界面复杂化，可能需要为 Tkinter 控件添加 `name` 属性以获得稳定的 `AutomationId`。
- **跨平台**: UI 测试仅限于 Windows。Linux/Mac 需要跳过 (已通过 `@pytest.mark.skipif` 实现)。
