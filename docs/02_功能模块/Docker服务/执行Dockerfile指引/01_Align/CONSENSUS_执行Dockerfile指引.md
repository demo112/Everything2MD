# 共识文档：执行 Dockerfile 指引

## 1. 核心解释
`Dockerfile` 是构建蓝图，不能直接运行。
必须使用 `docker build` 或 `docker compose build` 命令来读取并执行其中的指令。

## 2. 操作指南
为了应用最近的所有更改（代码修复、依赖更新），我们需要让 Docker 根据这个 `Dockerfile` 重新打包镜像。

### 推荐命令
```bash
docker compose up -d --build --force-recreate
```
这条命令会：
1.  **读取 Dockerfile**：根据最新定义构建镜像。
2.  **重建容器**：使用新镜像启动服务。
3.  **清理旧环境**：确保没有残留的旧配置。

## 3. 验证
执行完上述命令后，通过浏览器访问 Web 界面，验证文件选择器是否正常工作。
