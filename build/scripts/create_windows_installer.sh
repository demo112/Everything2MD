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
echo Everything2MD Windows Installer
echo =============================
echo Setting up environment...
echo Installation complete.
echo Double-click everything2md.bat to run, or use:
echo everything2md.bat -i input.docx -o output.md
pause
EOF

# 创建启动脚本
echo "创建启动脚本..."
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

rem 探测并添加 LibreOffice 到 PATH
set "LO_CANDIDATE1=%SCRIPT_DIR%LibreOfficePortable\App\libreoffice\program"
set "LO_CANDIDATE2=%ProgramFiles%\LibreOffice\program"
set "LO_CANDIDATE3=%ProgramFiles(x86)%\LibreOffice\program"
if exist "%LO_CANDIDATE1%\soffice.exe" set "PATH=%LO_CANDIDATE1%;%PATH%"
if exist "%LO_CANDIDATE2%\soffice.exe" set "PATH=%LO_CANDIDATE2%;%PATH%"
if exist "%LO_CANDIDATE3%\soffice.exe" set "PATH=%LO_CANDIDATE3%;%PATH%"

set "MISSING_DEPS="

rem 如果未检测到 soffice.exe，则提示 LibreOffice 缺失
where soffice >nul 2>nul
if errorlevel 1 (
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
) else (
    echo Done
)

pause
EOF

# 创建README文件
echo "创建README文件..."
cat > "$FINAL_DIR/README.txt" << 'EOF'
Everything2MD - Document Conversion Tool (Windows)
=================================================
Usage:
1. Double-click everything2md.bat
2. Or CLI: everything2md.bat -i input.docx -o output.md
Dependencies:
- LibreOffice (Office documents)
- Pandoc (format conversion)
- Python (runtime)
- BusyBox (sh runtime)
Structure:
- deps/
- src/
- everything2md.bat
- install.bat
EOF

echo "Windows发行版已生成: $FINAL_DIR"
echo "创建Windows安装包完成"