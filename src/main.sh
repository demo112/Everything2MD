#!/bin/bash

# Everything2MD - 文档转换工具主程序
# 作者: AI Assistant
# 日期: 2024

# 初始化脚本，创建项目目录结构

echo "正在创建 Everything2MD 项目目录结构..."

# 创建目录结构
mkdir -p src/core
mkdir -p src/components
mkdir -p src/utils
mkdir -p tests/fixtures
mkdir -p tests/expected
mkdir -p components

echo "目录结构创建完成!"

# 创建初始文件
echo "创建初始文件..."

# 创建 everything2md.sh 主程序入口
cat > everything2md.sh << 'EOF'
#!/bin/bash

# Everything2MD - 将各种文档格式转换为 Markdown
# 支持格式: doc, docx, ppt, pptx

# 默认参数
VERBOSE=false
BATCH_MODE=false
INPUT=""
OUTPUT=""

# 显示帮助信息
show_help() {
    echo "Usage: $0 [-h] [-b] [-v] input [output]"
    echo ""
    echo "参数:"
    echo "  input          输入文件或目录路径"
    echo "  output         输出文件或目录路径（可选）"
    echo "  -h, --help     显示帮助信息"
    echo "  -b, --batch    批量转换模式"
    echo "  -v, --verbose  详细输出模式"
    echo ""
}

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -b|--batch)
            BATCH_MODE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -*)
            echo "未知参数: $1"
            show_help
            exit 1
            ;;
        *)
            if [[ -z "$INPUT" ]]; then
                INPUT="$1"
            elif [[ -z "$OUTPUT" ]]; then
                OUTPUT="$1"
            else
                echo "参数过多"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# 检查输入参数
if [[ -z "$INPUT" ]]; then
    echo "错误: 请指定输入文件或目录"
    show_help
    exit 1
fi

# 输出详细信息
if [[ "$VERBOSE" == true ]]; then
    echo "输入: $INPUT"
    echo "输出: ${OUTPUT:-未指定}"
    echo "批量模式: $BATCH_MODE"
    echo "详细模式: $VERBOSE"
fi

echo "Everything2MD 初始化完成!"
echo "请继续实现具体功能。"
EOF

# 添加执行权限
chmod +x everything2md.sh

echo "everything2md.sh 主程序入口创建完成!"

echo "任务1: 项目初始化和目录结构创建 已完成!"