# Consensus: Web文件选择器优化及全盘访问

## 需求定义
1. **UI/UX 优化**：
   - 移除 `index.html` 中的内联样式。
   - 在 `style.css` 中统一管理 Modal 样式，适配暗黑模式（Dark Theme）。
   - 修复布局问题，确保 Modal 居中且响应式。
2. **功能增强**：
   - 支持在 Web 界面浏览宿主机的 C, D, E, F 盘。
   - 增加 "我的电脑" (ROOT) 视图，列出所有挂载的盘符。
   - 优化 "上一级" 导航逻辑，支持从子目录返回到盘符列表。

## 技术实现方案
1. **Docker**:
   - 修改 `docker-compose.yml`，将 C:/, D:/, E:/, F:/ 挂载到 `/mnt/c`, `/mnt/d` 等。
2. **Backend (Python/FastAPI)**:
   - 修改 `list_files` API。
   - 当 `path="ROOT"` 时，返回挂载点列表（/mnt/c, /mnt/d...）和项目目录。
3. **Frontend (HTML/JS/CSS)**:
   - 重构 Modal HTML 结构，使用 `modal-overlay` 和 `modal` 类。
   - CSS 使用 CSS Variables (`--bg-color`, `--text-color`) 确保主题一致性。
   - JS 增加对 `ROOT` 路径的特殊处理，以及对象格式的文件列表数据的支持。

## 验收标准
- 文件选择器背景色与主色调一致，文字清晰可见。
- 点击文件选择器，初始显示或可通过 "上一级" 到达 "我的电脑" 视图。
- 能看到 C, D, E, F 盘，并能点击进入浏览文件。
- 能正确选择文件并返回路径。
