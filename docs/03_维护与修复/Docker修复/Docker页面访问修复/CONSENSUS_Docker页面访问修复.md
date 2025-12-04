# CONSENSUS_Docker页面访问修复

## 1. 需求精确描述
修复 Docker 环境无法访问 Web 页面的问题。

**验收标准**：
1.  Docker 容器启动后，宿主机可以通过 `http://localhost:8000` 访问 Web 界面。
2.  容器内正确安装 FastAPI 及相关依赖。
3.  `docker-compose` 配置了端口映射。

## 2. 技术实现方案
1.  **修改 Dockerfile**：
    -   `COPY requirements.txt .`
    -   `RUN pip3 install -r requirements.txt` (在 pptx2md 之后)。
    -   确保 `requirements.txt` 包含 `fastapi`, `uvicorn`（已确认包含）。
2.  **修改 docker-compose.yml**：
    -   添加 `ports` 映射：`"8000:8000"`。
    -   修改 `command`：启动 uvicorn 服务。
        -   命令：`uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --reload`
        -   注意：由于代码是挂载进去的 (`.:/work`)，使用 `--reload` 可以支持热重载开发。

## 3. 任务边界
-   仅修复 Docker 相关的 Web 启动问题。
-   不修改 Web 代码本身（假设代码是好的）。
