# 任务分解：Web端文件选择器适配

## 任务列表

- [ ] **T1. 后端 API 实现**
  - 文件：`web/backend/main.py`
  - 内容：实现 `/api/fs/list` 接口。
  - 逻辑：接收 path，返回绝对路径、父目录、子文件夹列表、文件列表。支持 `only_dir` 过滤。

- [ ] **T2. 前端 Modal 结构与样式**
  - 文件：`web/frontend/index.html`
  - 内容：添加 `#filePickerModal` 的 HTML 结构。
  - 样式：添加对应的 CSS，确保居中显示、滚动条等。

- [ ] **T3. 前端逻辑实现**
  - 文件：`web/frontend/script.js`
  - 内容：
    - `openFilePicker(targetInputId, type)`: 打开 Modal。
    - `fetchFileList(path)`: 调用 API。
    - `renderFileList(data)`: 渲染列表。
    - 事件绑定：双击进入，单击选中，确认返回。

- [ ] **T4. 替换原有调用**
  - 文件：`web/frontend/script.js`
  - 内容：将“选择文件/目录”按钮的 `onclick` 事件从调用 `/api/system/select-path` 改为调用 `openFilePicker`。

## 依赖关系
T1 -> T3
T2 -> T3
T3 -> T4
