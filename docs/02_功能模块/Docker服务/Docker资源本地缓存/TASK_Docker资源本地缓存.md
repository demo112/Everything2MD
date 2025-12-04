# TASK_Docker资源本地缓存

## 1. 原子任务
- [ ] **Task 1: 创建下载脚本**
  - 编写 `prepare_offline_resources.ps1`。
  - 实现 Docker 容器内下载 APT 和 PyPI 包的逻辑。

- [ ] **Task 2: 执行资源下载**
  - 运行脚本，验证 `docker_resources` 目录是否生成且包含文件。
  - 检查 `libreoffice` 等大包是否完整。

- [ ] **Task 3: 修改 Dockerfile**
  - 引入 `docker_resources`。
  - 改为优先使用本地文件安装。
  - 保留网络回退（可选，或完全离线）。

- [ ] **Task 4: 验证构建**
  - `docker build` 验证。
  - 验证功能是否正常。

## 2. 依赖关系
Task 1 -> Task 2 -> Task 3 -> Task 4
