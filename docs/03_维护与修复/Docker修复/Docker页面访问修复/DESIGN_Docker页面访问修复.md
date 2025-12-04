# DESIGN_Docker页面访问修复

## 1. 架构变更
-   **Docker 容器角色**：从单纯的 CLI 工具转变为 Web Server + CLI 工具。
-   **端口暴露**：新增 8000 端口映射。

## 2. 详细设计
**Dockerfile**:
```dockerfile
# ... (现有内容)
# 配置 pip 国内镜像并安装依赖
COPY requirements.txt /tmp/requirements.txt
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
 && pip3 install --no-cache-dir pptx2md \
 && pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /work
# ...
```

**docker-compose.yml**:
```yaml
services:
  everything2md:
    # ...
    ports:
      - "8000:8000"
    command: uvicorn web.backend.main:app --host 0.0.0.0 --port 8000 --reload
    # ...
```

## 3. 验证计划
1.  停止并删除现有容器。
2.  重新构建镜像。
3.  `docker-compose up -d`。
4.  访问 `http://localhost:8000/` (或者前端页面路径，FastAPI 默认可能没有根路由，需检查 main.py)。
    - 检查 `web/backend/main.py` 是否有静态文件挂载。如果没有，可能需要修改 python 代码来服务 frontend 目录。

**检查 Web 代码静态文件挂载**：
我需要再看一眼 `web/backend/main.py`，确认它是否 serve 了 `web/frontend`。
