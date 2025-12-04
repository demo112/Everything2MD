# ACCEPTANCE_Docker资源本地缓存

## 1. 验收标准
- [x] **下载脚本**: `prepare_offline_resources.ps1` 能够成功下载 APT 和 PyPI 依赖到 `docker_resources/`。
- [x] **Dockerfile 更新**: 支持优先使用本地缓存文件进行构建。
- [x] **离线构建能力**: 在拥有缓存的情况下，构建过程不再依赖外网下载大文件（APT/PyPI）。
- [x] **构建验证**: `docker-compose build` 成功完成。

## 2. 验证记录
- **资源准备**: 运行脚本，生成 `docker_resources/apt` (包含 .deb) 和 `docker_resources/pip` (包含 .whl)。
- **构建过程**: Docker 构建日志显示 `Installing from local apt cache...` 和 `Installing from local pip cache...`，证明逻辑生效。
- **构建耗时**: 依赖安装阶段速度显著提升（取决于本地 IO），且不消耗外网带宽。

## 3. 结论
任务完成。项目现在具备了离线构建或快速重构建的能力。
