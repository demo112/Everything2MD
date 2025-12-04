# 任务分解：执行 Dockerfile 指引

## 任务列表

- [ ] **T1. 解释概念**
  - 向用户解释 Dockerfile 的作用及如何生效。

- [ ] **T2. 执行构建**
  - 代替用户执行构建命令，确保环境最新。
  - 命令：`docker compose up -d --build --force-recreate`

- [ ] **T3. 验证服务**
  - 检查容器状态。
  - 确认 Web 服务端口开放。

## 依赖关系
T1 -> T2 -> T3
