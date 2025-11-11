#!/bin/bash

# Everything2MD 打包构建系统
# 支持Windows和macOS平台打包

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 导入配置
source "$SCRIPT_DIR/config/build.conf" 2>/dev/null || true

# 默认配置
PLATFORM=""
OUTPUT_DIR="$SCRIPT_DIR/dist"
TEMP_DIR="$SCRIPT_DIR/temp"
VERBOSE=false

# 显示帮助信息
show_help() {
    echo "Everything2MD 打包构建系统"
    echo
    echo "用法:"
    echo "  ./build.sh [选项]"
    echo
    echo "选项:"
    echo "  -p, --platform PLATFORM  目标平台 (windows|macos)"
    echo "  -o, --output DIR        输出目录 (默认: $OUTPUT_DIR)"
    echo "  -v, --verbose           详细输出"
    echo "  -c, --clean             清理构建产物"
    echo "  -h, --help              显示此帮助信息"
    echo
    echo "示例:"
    echo "  ./build.sh -p windows   构建Windows版本"
    echo "  ./build.sh -p macos     构建macOS版本"
    echo
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--platform)
                PLATFORM="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--clean)
                clean_build
                exit 0
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 清理构建产物
clean_build() {
    echo "清理构建产物..."
    rm -rf "$OUTPUT_DIR"/*
    rm -rf "$TEMP_DIR"/*
    echo "清理完成"
}

# 构建Windows版本
build_windows() {
    echo "开始构建Windows版本..."
    
    # 检查必要工具
    check_windows_tools
    
    # 创建Windows构建目录
    mkdir -p "$TEMP_DIR/windows"
    
    # 复制源代码
    copy_source_code "$TEMP_DIR/windows"
    
    # 调用Windows打包模块
    "$SCRIPT_DIR/scripts/windows_packager.sh"
    
    echo "Windows版本构建完成"
}

# 构建macOS版本
build_macos() {
    echo "开始构建macOS版本..."
    
    # 检查必要工具
    check_macos_tools
    
    # 创建macOS构建目录
    mkdir -p "$TEMP_DIR/macos"
    
    # 复制源代码
    copy_source_code "$TEMP_DIR/macos"
    
    # 调用macOS打包模块
    "$SCRIPT_DIR/scripts/macos_packager.sh"
    
    echo "macOS版本构建完成"
}

# 检查Windows构建工具
check_windows_tools() {
    echo "检查Windows构建工具..."
    # TODO: 实现Windows工具检查
    echo "工具检查完成"
}

# 检查macOS构建工具
check_macos_tools() {
    echo "检查macOS构建工具..."
    # TODO: 实现macOS工具检查
    echo "工具检查完成"
}

# 复制源代码
copy_source_code() {
    local target_dir="$1"
    echo "复制源代码到 $target_dir..."
    
    # 创建目录结构
    mkdir -p "$target_dir/src"
    
    # 复制主脚本
    cp "$PROJECT_ROOT/src/main.sh" "$target_dir/src/"
    
    # 复制模块
    cp -r "$PROJECT_ROOT/src/modules" "$target_dir/src/"
    
    # 复制文档
    cp -r "$PROJECT_ROOT/docs" "$target_dir/"
    
    # 复制README
    cp "$PROJECT_ROOT/README.md" "$target_dir/"
    
    echo "源代码复制完成"
}

# 主函数
main() {
    # 解析参数
    parse_arguments "$@"
    
    # 根据平台执行构建
    case "$PLATFORM" in
        "windows")
            build_windows
            ;;
        "macos")
            build_macos
            ;;
        "")
            echo "错误: 必须指定目标平台"
            show_help
            exit 1
            ;;
        *)
            echo "错误: 不支持的平台 '$PLATFORM'"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"