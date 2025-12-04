# Task: Web文件选择器优化及全盘访问

## 任务分解

### Task 1: Docker 配置更新
- [x] 修改 `docker-compose.yml` 添加宿主机盘符挂载。
- [x] 重启容器以应用挂载。

### Task 2: Backend API 升级
- [x] 修改 `web/backend/main.py` 中的 `list_files` 函数。
- [x] 实现 `path="ROOT"` 逻辑。
- [x] 实现 `/mnt` 目录扫描逻辑。

### Task 3: Frontend 样式重构
- [x] 清理 `index.html` 内联样式。
- [x] 更新 `style.css` 添加 Modal 相关样式（暗黑模式适配）。

### Task 4: Frontend 逻辑增强
- [x] 更新 `script.js` 中的 `renderFileList` 支持对象格式数据。
- [x] 实现 `navigateUp` 的逻辑修复。
- [x] 增加 "我的电脑" 显示逻辑。

## 依赖关系
Docker -> Backend -> Frontend (逻辑) -> Frontend (样式)
(实际执行中可并行，但测试需按顺序)
