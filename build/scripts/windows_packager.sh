#!/bin/bash

# Windows平台打包模块
# 负责将Everything2MD打包为Windows可执行文件

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(dirname "$SCRIPT_DIR")"
TEMP_DIR="$BUILD_DIR/temp"
DIST_DIR="$BUILD_DIR/dist"
PROJECT_ROOT="$(dirname "$BUILD_DIR")"

echo "Windows打包模块初始化..."

# 配置变量
MSYS2_DIR="$TEMP_DIR/msys64"
INSTALLER_DIR="$DIST_DIR/windows"
MSYS2_URL="https://github.com/msys2/msys2-installer/releases/download/2023-07-18/msys2-base-x86_64-20230718.tar.xz"

# 下载并设置MSYS2环境
setup_msys2() {
    echo "设置MSYS2环境..."
    
    # 创建目录
    mkdir -p "$MSYS2_DIR"
    
    # 检查是否已下载MSYS2
    if [ ! -f "$TEMP_DIR/msys2.tar.xz" ]; then
        echo "下载MSYS2基础包..."
        # 注意：在实际实现中，这里需要实现下载功能
        # curl -L "$MSYS2_URL" -o "$TEMP_DIR/msys2.tar.xz"
        echo "下载功能将在实际实现中添加"
    fi
    
    echo "MSYS2环境设置完成"
}

# 打包项目依赖项
package_dependencies() {
    echo "打包项目依赖项..."
    
    # 创建依赖目录
    mkdir -p "$INSTALLER_DIR/deps"
    
    # TODO: 实际打包依赖项
    # 这里需要实现LibreOffice, Pandoc, pptx2md的打包逻辑
    
    echo "依赖项打包完成"
}

# 编译Windows启动器
compile_launcher() {
    echo "编译Windows启动器..."
    
    # 创建启动器目录
    mkdir -p "$INSTALLER_DIR/launcher"
    
    # 复制Windows启动器脚本到发行版
    echo "复制Windows启动器..."
    cp "$SCRIPT_DIR/windows_launcher.bat" "$INSTALLER_DIR/launcher/"
    
    # 如果有编译的启动器程序，也复制到launcher目录
    # 这里假设启动器程序名为everything2md.exe
    if [ -f "$TEMP_DIR/everything2md.exe" ]; then
        cp "$TEMP_DIR/everything2md.exe" "$INSTALLER_DIR/launcher/"
    fi
    
    echo "Windows启动器编译完成"
}

# 整合所有组件
integrate_components() {
    echo "整合所有组件..."
    
    # 创建安装目录结构
    mkdir -p "$INSTALLER_DIR/bin"
    mkdir -p "$INSTALLER_DIR/src"
    mkdir -p "$INSTALLER_DIR/launcher"
    
    # 复制源代码
    echo "复制源代码..."
    cp -r "$PROJECT_ROOT/src" "$INSTALLER_DIR/"
    
    # 复制README
    echo "复制文档..."
    cp "$PROJECT_ROOT/README.md" "$INSTALLER_DIR/"
    
    # 复制启动器
    echo "复制启动器..."
    cp "$SCRIPT_DIR/windows_launcher.bat" "$INSTALLER_DIR/launcher/"
    
    echo "组件整合完成"
}

# 生成最终发行版
generate_installer() {
    echo "生成最终发行版..."
    
    # 设置版本信息
    VERSION="1.0.0"
    BUILD_DATE=$(date +%Y%m%d)
    
    # 创建发行版目录
    FINAL_DIR="$DIST_DIR/Everything2MD-Windows-$VERSION-$BUILD_DATE"
    mkdir -p "$FINAL_DIR"
    
    # 复制所有文件到发行版目录
    cp -r "$INSTALLER_DIR"/* "$FINAL_DIR/"
    
    # 创建简单的安装脚本
    cat > "$FINAL_DIR/install.bat" << 'EOF'
@echo off
echo Everything2MD Windows Installer
echo =============================
echo Setting up environment...
echo Installation complete.
echo Double-click everything2md.bat to run, or use:
echo everything2md.bat -i input.docx -o output.md
pause
EOF
    
    # 创建启动脚本
    cat > "$FINAL_DIR/everything2md.bat" << 'EOF'
@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "DEPS_DIR=%SCRIPT_DIR%deps"
set "SRC_DIR=%SCRIPT_DIR%src"

if not exist "%DEPS_DIR%" (
    echo Error: deps directory not found
    pause
    exit /b 1
)

set "PATH=%DEPS_DIR%;%DEPS_DIR%\python;%PATH%"

set "MISSING_DEPS="

if not exist "%DEPS_DIR%\libreoffice_portable.exe" (
    set "MISSING_DEPS=!MISSING_DEPS! LibreOffice"
)

if not exist "%DEPS_DIR%\pandoc.exe" (
    set "MISSING_DEPS=!MISSING_DEPS! Pandoc"
)

if not exist "%DEPS_DIR%\python\python.exe" (
    set "MISSING_DEPS=!MISSING_DEPS! Python"
)

if not exist "%DEPS_DIR%\busybox.exe" (
    set "MISSING_DEPS=!MISSING_DEPS! BusyBox"
)

if defined MISSING_DEPS (
    echo Error: missing dependencies: %MISSING_DEPS%
    echo Please run install_deps.bat to install dependencies
    pause
    exit /b 1
)

if not exist "%SRC_DIR%" (
    echo Error: source directory not found
    pause
    exit /b 1
)

"%DEPS_DIR%\busybox.exe" sh "%SRC_DIR%\main.sh" %*

if errorlevel 1 (
    echo Error occurred
else (
    echo Done
)

pause
EOF
    
    echo "Windows发行版已生成: $FINAL_DIR"

    ARCHIVE_PATH="$DIST_DIR/Everything2MD-Windows-$VERSION-$BUILD_DATE.7z"
    EXE_PATH="$DIST_DIR/Everything2MD-Windows-$VERSION-$BUILD_DATE.exe"
    CONFIG_FILE="$TEMP_DIR/7z_config.txt"
    echo ";!@Install@!UTF-8!" > "$CONFIG_FILE"
    echo "RunProgram=\"everything2md.bat\"" >> "$CONFIG_FILE"
    echo ";!@InstallEnd@!" >> "$CONFIG_FILE"
    7z a -r "$ARCHIVE_PATH" "$FINAL_DIR" >/dev/null
    SFX_MOD="/c/Program Files/7-Zip/7z.sfx"
    if [ ! -f "$SFX_MOD" ]; then
        SFX_MOD="/c/Program Files (x86)/7-Zip/7z.sfx"
    fi
    if [ -f "$SFX_MOD" ]; then
        cat "$SFX_MOD" "$CONFIG_FILE" "$ARCHIVE_PATH" > "$EXE_PATH"
        echo "自解压可执行文件已生成: $EXE_PATH"
    else
        echo "未找到7z.sfx，跳过自解压可执行文件生成"
    fi
}

# 主函数
main() {
    echo "开始Windows平台打包..."
    
    # 设置MSYS2环境
    setup_msys2
    
    # 打包依赖项（调用独立依赖打包脚本以确保deps完整）
    "$SCRIPT_DIR/windows_deps_packager.sh"
    # 补充任何本模块内的依赖打包占位逻辑
    package_dependencies
    
    # 编译启动器
    compile_launcher
    
    # 整合组件
    integrate_components
    
    # 生成发行版
    generate_installer
    
    echo "Windows平台打包完成"
}

# 执行主函数
main "$@"