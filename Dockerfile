FROM ubuntu:22.04

# 设置国内APT源，加速依赖安装
RUN sed -i 's|archive.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list \
 && sed -i 's|security.ubuntu.com|mirrors.aliyun.com|g' /etc/apt/sources.list \
 && apt-get update \
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
    fonts-noto-cjk \
 && rm -rf /var/lib/apt/lists/*

# 本地化环境与中文支持
ENV TZ=Asia/Shanghai \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 配置虚拟环境 (venv)
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 配置 pip 国内镜像并安装依赖
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ \
 && pip3 install --no-cache-dir pptx2md

WORKDIR /work

# 默认不复制代码，运行时通过挂载宿主机目录提供源码
# 容器默认命令可由用户覆盖；保留为交互式shell
CMD ["bash"]
