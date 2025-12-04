# 使用 ARG 允许灵活切换镜像源
# 默认使用 DaoCloud 国内加速: m.daocloud.io/docker.io/library
# 如果失效，可尝试: swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io
ARG UBUNTU_REGISTRY=m.daocloud.io/docker.io/library

FROM ${UBUNTU_REGISTRY}/ubuntu:22.04

# 设置国内APT源，加速依赖安装
RUN sed -i 's|archive.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list \
 && sed -i 's|security.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list

# 优先尝试本地离线安装 APT 包
COPY docker_resources/apt /tmp/apt
RUN if [ -d "/tmp/apt" ] && [ "$(ls -A /tmp/apt/*.deb 2>/dev/null)" ]; then \
        echo "Installing from local apt cache..."; \
        apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y /tmp/apt/*.deb; \
    else \
        echo "Local apt cache not found, downloading..."; \
        apt-get update \
        && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
           bash \
           tzdata \
           locales \
           libreoffice \
           pandoc \
           poppler-utils \
           file \
           jq \
           python3 \
           python3-pip \
           python3-venv \
           python3-tk \
           fonts-noto-cjk; \
    fi \
 && rm -rf /var/lib/apt/lists/* /tmp/apt

# 本地化环境与中文支持
ENV TZ=Asia/Shanghai \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 配置虚拟环境 (venv)
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 配置 pip 国内镜像并安装依赖
COPY requirements.txt /tmp/requirements.txt
COPY docker_resources/pip /tmp/pip
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
 && if [ -d "/tmp/pip" ] && [ "$(ls -A /tmp/pip/*.whl 2>/dev/null)" ]; then \
        echo "Installing from local pip cache..."; \
        pip3 install --no-cache-dir --no-index --find-links=/tmp/pip pptx2md -r /tmp/requirements.txt; \
    else \
        echo "Local pip cache not found, downloading..."; \
        pip3 install --no-cache-dir pptx2md \
        && pip3 install --no-cache-dir -r /tmp/requirements.txt; \
    fi \
 && rm -rf /tmp/pip

WORKDIR /work

# 默认不复制代码，运行时通过挂载宿主机目录提供源码
# 容器默认命令可由用户覆盖；保留为交互式shell
CMD ["bash"]
 