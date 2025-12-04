# TASK_修复文件选择组件

## 1. 原子任务
- [ ] **Task 1: 修正 list_files 逻辑**
  - 修改 `web/backend/main.py`。
  - 引入 `platform` 模块或使用 `os.name`。
  - 分离 Windows 和 Linux 的根目录处理逻辑。

- [ ] **Task 2: 修正 bash 路径查找**
  - 修改 `web/backend/main.py` 中的 `convert` 函数。
  - 在非 Windows 环境下直接使用 `bash`。

- [ ] **Task 3: 重建并验证**
  - 重建 Docker 镜像 (代码变更需要重启/重建，取决于挂载方式，但为了稳妥建议重建)。
  - 验证 Web 界面文件选择功能。

## 2. 依赖关系
Task 1 & Task 2 -> Task 3
