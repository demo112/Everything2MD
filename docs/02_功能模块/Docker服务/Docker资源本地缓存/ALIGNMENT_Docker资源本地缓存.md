# ALIGNMENT_Docker资源本地缓存

## 1. 需求分析
- **目标**: 将构建 Docker 镜像所需的所有外部资源（APT 包、PyPI 包）预先下载到本地目录。
- **目的**: 
  - 加速 Docker 构建过程。
  - 支持在离线或受限网络环境下构建。
  - 确保构建环境的一致性和可复现性。

## 2. 资源清单
### 2.1 APT 依赖 (Ubuntu 22.04)
- `bash`, `tzdata`, `locales`
- `libreoffice` (体积较大，关键)
- `pandoc`, `poppler-utils`, `file`, `jq`
- `python3`, `python3-pip`, `python3-venv`
- `fonts-noto-cjk`

### 2.2 PyPI 依赖
- `pptx2md`
- `requirements.txt` 中的所有包 (`fastapi`, `uvicorn`, `pytest`, `websockets` 等)

## 3. 技术方案
### 3.1 下载策略
由于宿主机是 Windows，无法直接下载 Ubuntu 的 `.deb` 包。我们将使用一个临时 Docker 容器作为“下载器”：
1. **APT 包**: 启动 Ubuntu 容器，运行 `apt-get install --download-only`，将 `/var/cache/apt/archives` 下的 `.deb` 文件拷贝到宿主机 `docker_resources/apt`。
2. **PyPI 包**: 启动 Ubuntu 容器（确保环境一致），运行 `pip download`，将 `.whl` 文件拷贝到宿主机 `docker_resources/pip`。

### 3.2 构建策略
修改 `Dockerfile`：
- **阶段 1 (Base)**: 设置源（可选，用于下载基础镜像）。
- **阶段 2 (Install)**: 
  - `COPY docker_resources/apt /tmp/apt`
  - `RUN dpkg -i /tmp/apt/*.deb || apt-get install -f -y` (优先本地安装，缺漏则联网，或严格离线)。
  - `COPY docker_resources/pip /tmp/pip`
  - `RUN pip install --no-index --find-links=/tmp/pip ...`

## 4. 假设与约束
- 用户已安装 Docker。
- 允许在“准备阶段”联网下载资源。
- 本地目录 `docker_resources` 将被提交到版本控制或作为构建制品分发。

## 5. 待确认问题
- 是否需要完全离线？(假设是，尽可能做到 `apt-get` 不再请求网络)
- `libreoffice` 依赖众多，`--download-only` 必须捕获完整的递归依赖树。

## 6. 决策
- 采用 **"Downloader Container" 模式**，确保下载的包与目标镜像架构/版本完全匹配。
- 创建 `prepare_offline_resources.ps1` 脚本自动化此过程。
