# ACCEPTANCE: Docker适配修复

## 1. 问题分析
- **现象**: 用户反馈 Docker 容器运行后服务异常，日志显示崩溃。
- **原因**:
    1.  `web/backend/main.py` 引入了 `tkinter` 库用于实现本地系统弹窗。
    2.  Docker 基础镜像（Ubuntu）未安装 `python3-tk`，导致 `ImportError`。
    3.  即便安装了库，Docker 容器（Headless 环境）默认不支持 GUI 操作，会导致运行时 `TclError`。

## 2. 修复方案
- **Dockerfile**: 添加 `python3-tk` 依赖安装。
- **后端 (main.py)**:
    -   增加 `try-except ImportError` 块，允许在无 `tkinter` 环境下启动服务。
    -   API `/api/system/select-path` 增加环境检测，如果无法弹窗，返回明确错误提示。
- **前端 (index.html)**:
    -   移除输入框的 `readonly` 属性，允许用户在无法使用弹窗时手动输入路径。

## 3. 验证结果
- [x] **Docker 构建**: `docker compose up -d --build` 成功执行。
- [x] **容器启动**: `docker logs` 显示服务已正常启动 (`Application startup complete`)。
- [x] **功能降级**: 在 Docker 环境下点击“选文件”应提示错误（或如果配置了 X11 则弹窗），但不影响核心转换功能。手动输入路径仍可工作。

## 4. 结论
Docker 环境已修复，服务恢复正常运行。
