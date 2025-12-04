# ALIGNMENT_Docker页面访问修复

## 1. 原始需求与边界确认
**需求描述**：
用户反馈 "docker中无法打开页面"。这通常意味着容器内的 Web 服务没有被正确暴露，或者 Web 服务根本没有启动。

**核心目标**：
1.  分析当前 Docker 配置为何无法提供 Web 访问。
2.  修改 Docker 配置以启动 Web 服务并暴露端口。
3.  确保遵循 6A 工作流和用户规则（使用国内源，删除旧容器）。

**边界**：
- **包含**：
  - 修改 `docker-compose.yml`。
  - 修改 `Dockerfile`（如果需要安装 Web 依赖）。
  - 验证 Web 服务是否可用。
- **不包含**：
  - 重写 Web 后端代码（除非是简单的启动脚本问题）。

## 2. 项目现状分析
**现有配置**：
- `docker-compose.yml`：仅挂载了目录，没有 `ports` 映射。
- `Dockerfile`：`CMD ["bash"]`，默认进入交互式 Shell，**没有启动 Web 服务器**。
- Web 后端代码位于 `web/backend/main.py`，是一个 FastAPI 应用。

**问题点**：
1.  **未暴露端口**：`docker-compose.yml` 缺少 `- ports: "8000:8000"`。
2.  **未启动服务**：容器启动命令是 `bash`，而不是启动 FastAPI 应用。
3.  **依赖缺失**：`Dockerfile` 中只安装了 `pptx2md`，没有安装 `fastapi`, `uvicorn` 等 Web 依赖。

## 3. 歧义澄清 (Q&A)
- **Q**: 用户想访问哪个页面？
  - **A**: 项目中有 `web/frontend` 和 `web/backend`，推测是想访问这个 Web UI。
- **Q**: 如何启动 Web 服务？
  - **A**: 应该运行 `uvicorn web.backend.main:app --host 0.0.0.0 --port 8000`。
- **Q**: 依赖在哪里？
  - **A**: 项目根目录有 `requirements.txt`，但 Dockerfile 似乎没有使用它。需要将 `requirements.txt` 复制到镜像中并安装。

**方案**：
1.  修改 `Dockerfile`：复制 `requirements.txt` 并安装依赖。
2.  修改 `docker-compose.yml`：映射端口 `8000`，并修改启动命令（或者保持 bash 但提供启动脚本）。
    - 考虑到用户可能想同时用 CLI，建议保持 `CMD` 为启动脚本，或者在 `docker-compose.yml` 中覆盖。
    - 更稳妥的是：在 `Dockerfile` 中准备好环境，`docker-compose.yml` 中定义 `command` 启动 Web 服务。

**依赖检查**：
`requirements.txt` 包含 `fastapi`, `uvicorn` 等吗？我需要检查一下。
