# TASK: 界面优化_中文及原生文件选择

## 任务列表

### Task 1: 后端系统弹窗接口
*   **文件**: `web/backend/main.py`
*   **输入**: 无
*   **输出**: 新增 API 接口
*   **步骤**:
    1.  导入 `tkinter` 和 `filedialog`。
    2.  实现 `select_path` 函数，处理主窗口隐藏和置顶。
    3.  注册路由 `/api/system/select-path`。
*   **依赖**: 无。

### Task 2: 前端界面中文化与改造
*   **文件**: `web/frontend/index.html`
*   **输入**: 现有 HTML
*   **输出**: 中文 HTML，移除模态框
*   **步骤**:
    1.  翻译所有文本。
    2.  修改输入框布局，为“输入路径”增加“选文件”和“选文件夹”两个按钮。
    3.  为“输出路径”增加“选文件夹”按钮。
    4.  移除 `#filePickerModal` 代码块。

### Task 3: 前端逻辑更新
*   **文件**: `web/frontend/script.js`
*   **输入**: 现有 JS
*   **输出**: 适配新 API 的 JS
*   **步骤**:
    1.  移除旧的 `fetchFiles`, `renderFileList`, `openFilePicker` (旧逻辑)。
    2.  新增 `selectPath(inputType, selectionType)` 函数。
    3.  调用后端 API 并更新 UI。
    4.  翻译 JS 中的提示信息。

### Task 4: 验证与清理
*   **文件**: 全局
*   **步骤**:
    1.  启动服务。
    2.  测试所有按钮。
    3.  测试转换流程。
    4.  确保 Docker/Shell 脚本调用不受影响（本次仅改 UI/API，不应影响）。
