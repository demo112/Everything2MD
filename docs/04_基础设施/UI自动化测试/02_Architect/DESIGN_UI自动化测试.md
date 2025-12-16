# DESIGN_UI自动化测试

## 1. 架构设计

```mermaid
graph TD
    TestRunner[pytest Runner]
    
    subgraph Test_Suite [UI Test Suite]
        Fixture[conftest.py / Fixtures]
        TC_Launch[test_e2e_launch.py]
        TC_Convert[test_e2e_conversion.py]
    end
    
    subgraph System_Under_Test [SUT]
        AppProcess[Everything2MD Process]
        GUI_Window[Main Window (Tkinter)]
    end
    
    subgraph Driver [Driver Layer]
        Pywinauto[pywinauto Application]
        Desktop[Desktop / UIA Backend]
    end
    
    TestRunner --> Fixture
    Fixture -- Start/Kill --> AppProcess
    Fixture -- Connect --> Pywinauto
    Pywinauto -- Controls --> GUI_Window
    TC_Launch --> Pywinauto
    TC_Convert --> Pywinauto
```

## 2. 目录结构
```text
test/
  ui/
    __init__.py
    conftest.py       # 定义 app_process, main_window 等 fixture
    test_launch.py    # 启动与基本元素检查
    test_workflow.py  # 完整转换流程测试
    utils.py          # 辅助工具（路径查找等）
```

## 3. 核心组件设计

### 3.1 Fixture 设计 (`conftest.py`)
- `app_path`: 自动定位 `src/gui/main.py` 或构建后的 `exe`。
- `app_process`:
  - Setup: 使用 `subprocess.Popen` 启动应用。
  - Teardown: 检查进程状态，强制 `kill`。
- `main_window`:
  - 依赖 `app_process`。
  - 使用 `pywinauto.Application().connect()` 连接进程。
  - 返回主窗口对象 `app.window(title="Everything2MD - 文档转换工具")`。

### 3.2 元素定位策略
由于 Tkinter 原生控件对 Accessibility 支持有限，主要通过以下属性定位：
- `title`: 窗口标题。
- `control_type`: 控件类型 (Button, Edit, Static)。
- `auto_id`: 若 Tkinter 代码中设置了 `name` 属性，可能映射为 AutomationId (需验证)。
- `best_match`: 模糊匹配文本。

### 3.3 测试数据隔离
- 使用 `tmp_path` fixture 生成临时的输入文件和输出目录。
- 确保测试产生的垃圾文件在测试结束后清理。

## 4. 接口规范
- 所有 UI 测试文件以 `test_ui_` 开头（或放在 `test/ui` 目录下）。
- 使用 `@pytest.mark.ui` 标记，以便在非 GUI 环境下跳过。
