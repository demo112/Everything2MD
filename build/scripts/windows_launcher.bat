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