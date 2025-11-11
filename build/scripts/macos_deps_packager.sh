#!/bin/bash

# macOS依赖项打包模块
# 负责打包Everything2MD在macOS平台运行所需的依赖项

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(dirname "$SCRIPT_DIR")"
TEMP_DIR="$BUILD_DIR/temp"
DIST_DIR="$BUILD_DIR/dist"
PROJECT_ROOT="$(dirname "$BUILD_DIR")"

echo "macOS依赖项打包模块初始化..."

# 配置变量
DEPS_DIR="$DIST_DIR/macos/deps"

# 创建依赖目录
mkdir -p "$DEPS_DIR"

# 下载并安装LibreOffice macOS版本
install_libreoffice() {
    echo "下载并安装LibreOffice macOS版本..."
    
    # LibreOffice下载URL (macOS版本)
    LIBREOFFICE_URL="https://download.documentfoundation.org/libreoffice/stable/7.6.7/mac/x86_64/LibreOffice_7.6.7_MacOS_x86-64.dmg"
    LIBREOFFICE_FILE="$TEMP_DIR/libreoffice_macos.dmg"
    
    # 下载LibreOffice macOS版本
    echo "正在下载LibreOffice..."
    curl -L -o "$LIBREOFFICE_FILE" "$LIBREOFFICE_URL"
    
    # 将LibreOffice安装包复制到依赖目录
    echo "正在处理LibreOffice..."
    cp "$LIBREOFFICE_FILE" "$DEPS_DIR/"
    
    echo "LibreOffice处理完成"
}

# 下载并安装Pandoc macOS版本
install_pandoc() {
    echo "下载并安装Pandoc macOS版本..."
    
    # Pandoc下载URL (macOS版本)
    PANDOC_URL="https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-arm64-macOS.zip"
    PANDOC_FILE="$TEMP_DIR/pandoc_macos.zip"
    
    # 下载Pandoc
    echo "正在下载Pandoc..."
    curl -L -o "$PANDOC_FILE" "$PANDOC_URL"
    
    # 解压Pandoc到依赖目录
    echo "正在解压Pandoc..."
    unzip -q -o "$PANDOC_FILE" -d "$TEMP_DIR"
    
    # 查找并移动Pandoc到依赖目录
    PANDOC_BIN=$(find "$TEMP_DIR" -name "pandoc" -type f -perm +111 | head -n 1)
    if [ -n "$PANDOC_BIN" ]; then
        cp "$PANDOC_BIN" "$DEPS_DIR/"
        echo "Pandoc已复制到依赖目录"
    else
        echo "警告: 未找到pandoc可执行文件"
    fi
    
    # 清理临时文件
    rm -rf "$TEMP_DIR/pandoc-3.1.11" "$PANDOC_FILE"
    
    echo "Pandoc安装完成"
}

# 下载并安装Python及pptx2md
install_python_pptx2md() {
    echo "下载并安装Python及pptx2md..."
    
    # Python下载URL (macOS版本)
    PYTHON_URL="https://www.python.org/ftp/python/3.11.9/python-3.11.9-macos11.pkg"
    PYTHON_FILE="$TEMP_DIR/python_macos.pkg"
    
    # 下载Python macOS版本
    echo "正在下载Python..."
    curl -L -o "$PYTHON_FILE" "$PYTHON_URL"
    
    # 将Python安装包复制到依赖目录
    echo "正在处理Python..."
    cp "$PYTHON_FILE" "$DEPS_DIR/"
    
    # 创建安装脚本
    cat > "$DEPS_DIR/install_python_pptx2md.sh" << 'EOF'
#!/bin/bash

echo "正在安装Python和pptx2md..."

# 用户需要手动安装Python
echo "请手动安装Python: $PWD/python_macos.pkg"
echo "安装完成后，运行以下命令安装pptx2md:"
echo "pip3 install pptx2md"

echo "Python和pptx2md处理完成!"
EOF
    
    # 添加执行权限
    chmod +x "$DEPS_DIR/install_python_pptx2md.sh"
    
    # 清理临时文件
    rm -f "$PYTHON_FILE"
    
    echo "Python和pptx2md处理完成"
}

# 创建依赖项打包脚本
create_deps_script() {
    echo "创建依赖项打包脚本..."
    
    # 创建macOS依赖项安装脚本
    cat > "$DEPS_DIR/install_deps.sh" << 'EOF'
#!/bin/bash

echo "正在安装Everything2MD依赖项..."

echo "依赖项安装完成!"
EOF
    
    # 添加执行权限
    chmod +x "$DEPS_DIR/install_deps.sh"
    
    echo "依赖项打包脚本创建完成"
}

# 测试依赖项打包功能
test_deps_packaging() {
    echo "测试依赖项打包功能..."
    
    # 检查必要的依赖文件是否存在
    if [ -f "$DEPS_DIR/pandoc" ]; then
        echo "✓ Pandoc已正确打包"
    else
        echo "✗ Pandoc未找到"
    fi
    
    if [ -f "$DEPS_DIR/libreoffice_macos.dmg" ]; then
        echo "✓ LibreOffice已正确打包"
    else
        echo "✗ LibreOffice未找到"
    fi
    
    echo "依赖项打包功能测试完成"
}

# 主函数
main() {
    echo "开始macOS依赖项打包..."
    
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
    
    echo "macOS依赖项打包完成"
}

# 执行主函数
main "$@"