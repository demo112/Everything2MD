#!/bin/bash

# 创建Windows安装包脚本

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$BUILD_DIR/dist"
INSTALLER_DIR="$DIST_DIR/windows"
PROJECT_ROOT="$(dirname "$BUILD_DIR")"

echo "创建Windows安装包..."

# 设置版本信息
VERSION="1.0.0"
BUILD_DATE=$(date +%Y%m%d)

# 创建发行版目录
FINAL_DIR="$DIST_DIR/Everything2MD-Windows-$VERSION-$BUILD_DATE"
mkdir -p "$FINAL_DIR"

# 复制所有文件到发行版目录
echo "复制文件到发行版目录..."
cp -r "$INSTALLER_DIR"/* "$FINAL_DIR/"

# 创建安装脚本
echo "创建安装脚本..."
cat > "$FINAL_DIR/install.bat" << 'EOF'
@echo off
echo Everything2MD Windows安装脚本
echo =============================

echo 正在设置环境...

echo.
echo 安装完成！
echo 您可以通过双击 everything2md.bat 来运行Everything2MD
echo 或者通过命令行使用: everything2md.bat [选项]
echo 例如: everything2md.bat -i input.docx -o output.md
pause
EOF

# 创建启动脚本
echo "创建启动脚本..."
cat > "$FINAL_DIR/everything2md.bat" << 'EOF'
@echo off
setlocal enabledelayedexpansion

:: Everything2MD Windows启动器
:: 用于检测依赖项并运行Everything2MD转换工具

echo Everything2MD - 文档转换工具 (Windows版本)
echo ========================================

:: 设置路径
set "SCRIPT_DIR=%~dp0"
set "DEPS_DIR=%SCRIPT_DIR%deps"
set "SRC_DIR=%SCRIPT_DIR%src"

:: 检查依赖项目录
if not exist "%DEPS_DIR%" (
    echo 错误: 未找到依赖项目录
    pause
    exit /b 1
)

:: 将依赖项添加到PATH
set "PATH=%DEPS_DIR%;%DEPS_DIR%\python;%PATH%"

:: 检查必要的依赖项
echo 检查依赖项...
set "MISSING_DEPS="

:: 检查LibreOffice
if not exist "%DEPS_DIR%\libreoffice_portable.exe" (
    set "MISSING_DEPS=!MISSING_DEPS! LibreOffice"
)

:: 检查Pandoc
if not exist "%DEPS_DIR%\pandoc.exe" (
    set "MISSING_DEPS=!MISSING_DEPS! Pandoc"
)

:: 检查Python
if not exist "%DEPS_DIR%\python\python.exe" (
    set "MISSING_DEPS=!MISSING_DEPS! Python"
)

:: 如果有缺失的依赖项，显示错误
if defined MISSING_DEPS (
    echo 错误: 以下依赖项未找到: %MISSING_DEPS%
    echo 请运行 install_deps.bat 安装依赖项
    pause
    exit /b 1
)

:: 检查源代码目录
if not exist "%SRC_DIR%" (
    echo 错误: 未找到源代码目录
    pause
    exit /b 1
)

:: 运行Everything2MD主程序
echo 所有依赖项检查通过，正在启动Everything2MD...
echo.

:: 使用Python运行主程序
"%DEPS_DIR%\python\python.exe" "%SRC_DIR%\main.sh" %*

:: 保持窗口打开以便查看输出
if errorlevel 1 (
    echo.
    echo 程序执行出现错误
) else (
    echo.
    echo 程序执行完成
)

echo.
pause
EOF

# 创建README文件
echo "创建README文件..."
cat > "$FINAL_DIR/README.txt" << 'EOF'
Everything2MD - 文档转换工具 (Windows版本)
=========================================

简介:
Everything2MD是一个将各种文档格式转换为Markdown的工具。

支持的格式:
- Microsoft Word (.docx)
- Microsoft PowerPoint (.pptx)
- PDF (.pdf)
- 纯文本文件 (.txt)

使用方法:
1. 双击 everything2md.bat 运行程序
2. 或者通过命令行使用:
   everything2md.bat -i input.docx -o output.md

依赖项:
- LibreOffice (用于处理Office文档)
- Pandoc (用于文档格式转换)
- Python (运行环境)

目录结构:
- deps/: 依赖项目录
- src/: 源代码目录
- everything2md.bat: 主程序启动脚本
- install.bat: 安装脚本

注意:
首次使用时，请确保所有依赖项都已正确安装。
如果遇到问题，请查看deps目录中的install_deps.bat脚本。
EOF

echo "Windows发行版已生成: $FINAL_DIR"
echo "创建Windows安装包完成"