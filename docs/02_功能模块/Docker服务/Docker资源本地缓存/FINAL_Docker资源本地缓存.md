# FINAL_Docker资源本地缓存

## 1. 项目摘要
为 Docker 镜像构建过程引入了本地资源缓存机制。通过预先下载 APT 和 PyPI 依赖包，实现了构建过程的离线化和加速。

## 2. 主要变更
- **新增脚本**: `prepare_offline_resources.ps1` (Windows) 及其配套的 `docker_resources/download.sh` (Linux)。
- **新增目录**: `docker_resources/` 用于存储缓存的 `.deb` 和 `.whl` 文件。
- **Dockerfile**: 修改了安装逻辑，优先检查并使用 `/tmp/apt` 和 `/tmp/pip` 中的本地文件，如果不存在则回退到网络下载。

## 3. 成果产出
- 可复现的离线构建环境。
- 完整的资源下载工具链。

## 4. 使用指南
1. 运行 `.\prepare_offline_resources.ps1` 下载最新依赖。
2. 运行 `docker-compose build` 进行构建。
