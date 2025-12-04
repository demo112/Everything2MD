# 共识文档：Web端文件选择器适配

## 1. 核心目标
开发一个基于 Web 的文件/目录选择器，替代原有的系统原生弹窗，以解决 Docker 环境下无法弹出文件选择框的问题。

## 2. 功能规格
### 2.1 后端 (FastAPI)
- **新增接口**：`GET /api/fs/list`
  - 参数：`path` (可选，默认为当前工作目录 `.` 或 `/work`)
  - 响应：
    ```json
    {
      "current_path": "/work/input",
      "parent_path": "/work",
      "items": [
        {"name": "folder1", "type": "directory"},
        {"name": "file1.docx", "type": "file"}
      ]
    }
    ```
  - 错误处理：路径不存在或无权限时返回 400/500 错误。

### 2.2 前端 (HTML/JS)
- **UI 组件**：新增一个模态框 (`<div id="file-picker-modal">`)。
  - 包含：当前路径显示、文件列表区域（图标+名称）、“取消”与“确定”按钮。
- **交互逻辑**：
  - 双击文件夹：调用 API 加载子目录。
  - 单击条目：高亮选中。
  - 点击确定：将选中项的完整路径填入主界面的输入框，并关闭模态框。

## 3. 实施步骤
1.  修改 `web/backend/main.py`：添加文件系统遍历 API。
2.  修改 `web/frontend/index.html`：添加 Modal HTML 结构和样式。
3.  修改 `web/frontend/script.js`：实现 Modal 的显示、数据加载、交互逻辑，并将原有的“选择文件”按钮事件绑定到此逻辑。

## 4. 验收标准
- 在 Docker 容器中运行服务，点击“选择文件”能弹出网页内的文件列表。
- 能正常进入文件夹、返回上一级。
- 选中文件后，输入框内显示正确的绝对路径。
