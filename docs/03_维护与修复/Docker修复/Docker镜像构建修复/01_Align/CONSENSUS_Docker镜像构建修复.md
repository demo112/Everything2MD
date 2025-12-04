# 共识文档：Docker镜像构建修复

## 1. 核心目标
修复 Docker 镜像构建过程中 `python3-tk` 依赖未正确安装的问题，并确保容器运行时能正确加载新镜像，同时保留合理的缓存策略。

## 2. 实施方案
### 2.1 构建策略
- **保留缓存**：不使用 `--no-cache` 全局禁用缓存。
- **触发更新**：依赖 Docker 自身的层缓存失效机制。由于 `Dockerfile` 中 `apt-get install` 行已修改（添加了 `python3-tk`），Docker **必须** 重新执行该层。
- **验证构建**：观察构建日志，确认 `apt-get install` 包含 `python3-tk`。

### 2.2 部署策略
- **强制重建容器**：使用 `docker compose up -d --force-recreate` 或先 `down` 再 `up`，确保容器基于新镜像启动，而非重用旧容器。
- **清理悬空镜像**：构建完成后，清理 `<none>` 标签的旧镜像以释放空间（可选）。

### 2.3 验证标准
1. **构建成功**：`docker compose build` 无错误。
2. **依赖存在**：容器内执行 `python3 -c "import tkinter"` 无报错。
3. **服务正常**：Web 服务启动正常，`/api/system/select-path` 接口在 Docker 环境下即使不支持 GUI 也能优雅降级（返回错误提示而非崩溃）。

## 3. 风险控制
- 如果 Dockerfile 修改未触发重建，检查是否修改了错误的文件或未保存。
- 如果 `apt-get` 极慢，确认是否使用了国内源（已配置阿里云源）。

## 4. 交付物
- 验证通过的 Docker 镜像。
- 运行正常的容器实例。
