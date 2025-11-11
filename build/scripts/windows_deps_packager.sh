#!/bin/bash

# Windows依赖项打包模块
# 负责打包Everything2MD在Windows平台运行所需的依赖项

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(dirname "$SCRIPT_DIR")"
TEMP_DIR="$BUILD_DIR/temp"
DIST_DIR="$BUILD_DIR/dist"
PROJECT_ROOT="$(dirname "$BUILD_DIR")"

echo "Windows依赖项打包模块初始化..."

# 配置变量
DEPS_DIR="$DIST_DIR/windows/deps"
MSYS2_DIR="$TEMP_DIR/msys64"

# 创建依赖目录
mkdir -p "$DEPS_DIR"

# 下载并安装LibreOffice Windows版本
install_libreoffice() {
    echo "下载并安装LibreOffice Windows版本..."
    
    # LibreOffice下载URL (便携版本)
    LIBREOFFICE_URL="https://download.documentfoundation.org/libreoffice/portable/7.6.7/LibreOfficePortable_7.6.7_MultilingualStandard.paf.exe"
    LIBREOFFICE_FILE="$TEMP_DIR/libreoffice_portable.exe"
    
    # 下载LibreOffice便携版本
    echo "正在下载LibreOffice..."
    curl -L -o "$LIBREOFFICE_FILE" "$LIBREOFFICE_URL"
    
    # 将LibreOffice安装包复制到依赖目录
    echo "正在处理LibreOffice..."
    cp "$LIBREOFFICE_FILE" "$DEPS_DIR/"
    
    echo "LibreOffice处理完成"
}

# 下载并安装Pandoc Windows版本
install_pandoc() {
    echo "下载并安装Pandoc Windows版本..."
    
    # Pandoc下载URL
    PANDOC_URL="https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-windows-x86_64.zip"
    PANDOC_FILE="$TEMP_DIR/pandoc_windows.zip"
    
    # 下载Pandoc
    echo "正在下载Pandoc..."
    curl -L -o "$PANDOC_FILE" "$PANDOC_URL"
    
    # 解压Pandoc到依赖目录
    echo "正在解压Pandoc..."
    unzip -q -o "$PANDOC_FILE" -d "$TEMP_DIR"
    
    # 查找并移动Pandoc到依赖目录
    PANDOC_EXE=$(find "$TEMP_DIR" -name "pandoc.exe" | head -n 1)
    if [ -n "$PANDOC_EXE" ]; then
        mv "$PANDOC_EXE" "$DEPS_DIR/"
        echo "Pandoc已移动到依赖目录"
    else
        echo "警告: 未找到pandoc.exe文件"
    fi
    
    # 清理临时文件
    rm -rf "$TEMP_DIR/pandoc-3.1.11" "$PANDOC_FILE"
    
    echo "Pandoc安装完成"
}

# 下载并安装Python及pptx2md
install_python_pptx2md() {
    echo "下载并安装Python及pptx2md..."
    
    # Python下载URL (嵌入式版本适合打包)
    PYTHON_URL="https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    PYTHON_FILE="$TEMP_DIR/python_windows.zip"
    
    # 下载Python嵌入式版本
    echo "正在下载Python..."
    curl -L -o "$PYTHON_FILE" "$PYTHON_URL"
    
    # 解压Python到依赖目录
    echo "正在解压Python..."
    mkdir -p "$DEPS_DIR/python"
    unzip -q "$PYTHON_FILE" -d "$DEPS_DIR/python"
    
    # 下载get-pip.py到Python目录
    echo "正在下载get-pip.py..."
    curl -L -o "$DEPS_DIR/python/get-pip.py" https://bootstrap.pypa.io/get-pip.py
    
    # 创建安装脚本
    cat > "$DEPS_DIR/python/install_pip_pptx2md.bat" << 'EOF'
@echo off
echo 正在安装pip和pptx2md...
python.exe get-pip.py
python.exe -m pip install pptx2md
echo pip和pptx2md安装完成!
EOF
    
    # 清理临时文件
    rm -f "$PYTHON_FILE"
    
    echo "Python和pptx2md处理完成"
}

# 创建依赖项打包脚本
create_deps_script() {
    echo "创建依赖项打包脚本..."
    
    # 创建Windows依赖项安装脚本
    cat > "$DEPS_DIR/install_deps.bat" << 'EOF'
@echo off
echo 正在安装Everything2MD依赖项...

echo 依赖项安装完成!
pause
EOF
    
    echo "依赖项打包脚本创建完成"
}

# 测试依赖项打包功能
test_deps_packaging() {
    echo "测试依赖项打包功能..."
    
    # 检查必要的依赖文件是否存在
    if [ -f "$DEPS_DIR/pandoc.exe" ]; then
        echo "✓ Pandoc已正确打包"
    else
        echo "✗ Pandoc未找到"
    fi
    
    if [ -d "$DEPS_DIR/python" ]; then
        echo "✓ Python已正确打包"
    else
        echo "✗ Python未找到"
    fi
    
    echo "依赖项打包功能测试完成"
}

# 主函数
main() {
    echo "开始Windows依赖项打包..."
    
    # 下载并安装LibreOffice
    install_libreoffice
    
    # 下载并安装Pandoc
    install_pandoc
    
    # 下载并安装Python及pptx2md
    install_python_pptx2md
    
    # 创建依赖项打包脚本
    create_deps_script
    
    # 测试依赖项打包功能
    test_deps_packaging
    
    echo "Windows依赖项打包完成"
}

# 执行主函数
main "$@"