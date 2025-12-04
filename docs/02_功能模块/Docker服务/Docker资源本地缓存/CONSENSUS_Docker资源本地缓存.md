# CONSENSUS_Docker资源本地缓存

## 1. 目标定义
构建一套机制，将 Docker 镜像所需的 APT 和 PyPI 依赖预先下载到本地 `docker_resources` 目录，并修改 Dockerfile 以优先使用本地资源进行构建。

## 2. 核心变更
### 2.1 新增脚本
- `prepare_offline_resources.ps1`: 启动临时容器，下载所有依赖并导出到本地。

### 2.2 目录结构
```
docker_resources/
├── apt/          # 存放 .deb 文件
└── pip/          # 存放 .whl 文件
```

### 2.3 Dockerfile 修改
- 增加 `COPY docker_resources/apt /tmp/apt`
- 使用 `dpkg -iR /tmp/apt` 安装系统包。
- 增加 `COPY docker_resources/pip /tmp/pip`
- 使用 `pip install --no-index --find-links=/tmp/pip` 安装 Python 包。

## 3. 验收标准
- [ ] 运行脚本能成功下载大量 `.deb` 和 `.whl` 文件。
- [ ] 断开网络（或模拟）情况下，`docker build` 能成功构建镜像。
- [ ] 镜像体积和功能与原版一致。
