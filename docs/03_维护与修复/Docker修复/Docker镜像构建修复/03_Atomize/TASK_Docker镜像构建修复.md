# 任务分解：Docker镜像构建修复

## 任务列表

- [ ] **T1. 验证 Dockerfile 内容**
  - 检查点：确认 `python3-tk` 存在于 `apt-get install` 列表中。
  - 检查点：确认镜像源配置正确。

- [ ] **T2. 执行 Docker 构建**
  - 命令：`docker compose build`
  - 验证：观察日志，确认 `apt-get install` 步骤被执行，且包含 `python3-tk`。
  - 预期：不使用 `--no-cache`，但应看到 "CACHED" 标记消失（针对 apt 层）。

- [ ] **T3. 重启容器服务**
  - 命令：`docker compose down` 然后 `docker compose up -d`
  - 或者：`docker compose up -d --force-recreate`

- [ ] **T4. 验证修复结果**
  - 命令：`docker exec everything2md python3 -c "import tkinter; print('Tkinter OK')"`
  - 预期输出：`Tkinter OK`

## 依赖关系
T1 -> T2 -> T3 -> T4
