#!/bin/bash

# Everything2MD macOS启动器
# 用于检测依赖项并运行Everything2MD转换工具

# 获取应用程序包路径
APP_PATH=$(dirname "$0")/../..
RESOURCES_PATH="$APP_PATH/Contents/Resources"
FRAMEWORKS_PATH="$APP_PATH/Contents/Frameworks"
DEPS_PATH="$RESOURCES_PATH/deps"

# 设置环境变量
export PATH="$DEPS_PATH:$DEPS_PATH/python:$PATH"

# 检查依赖项目录
if [ ! -d "$DEPS_PATH" ]; then
    # 如果在应用包中找不到依赖项，尝试在安装目录中查找
    INSTALL_DIR=$(dirname "$APP_PATH")
    DEPS_PATH="$INSTALL_DIR/deps"
    
    if [ ! -d "$DEPS_PATH" ]; then
        echo "错误: 未找到依赖项目录"
        exit 1
    fi
fi

# 检查依赖项
echo "检查依赖项..."

MISSING_DEPS=()

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "注意: 请确保已安装Python 3.x"
fi

# 检查Pandoc
if [ ! -x "$DEPS_PATH/pandoc/bin/pandoc" ]; then
    MISSING_DEPS+=("Pandoc")
else
    export PATH="$DEPS_PATH/pandoc/bin:$PATH"
fi

# 检查LibreOffice
if ! command -v libreoffice &> /dev/null && [ ! -d "$DEPS_PATH/libreoffice" ]; then
    MISSING_DEPS+=("LibreOffice")
else
    # 如果LibreOffice在deps目录中，添加到PATH
    if [ -d "$DEPS_PATH/libreoffice" ]; then
        export PATH="$DEPS_PATH/libreoffice:$PATH"
    fi
fi

# 检查依赖项是否缺失
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "错误: 以下依赖项未找到: ${MISSING_DEPS[*]}"
    echo "请安装缺失的依赖项后再运行程序"
    exit 1
fi

# 运行Everything2MD
echo "运行Everything2MD..."
"$RESOURCES_PATH/src/main.sh" "$@"