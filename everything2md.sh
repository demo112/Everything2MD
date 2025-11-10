#!/bin/bash

# Everything2MD 主程序
# 将各种办公文档格式转换为 Markdown 格式

# 设置脚本基础目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载依赖模块
source "$SCRIPT_DIR/src/utils/parser.sh"
source "$SCRIPT_DIR/src/utils/logger.sh"
source "$SCRIPT_DIR/src/utils/file_manager.sh"
source "$SCRIPT_DIR/src/core/file_type_detector.sh"
source "$SCRIPT_DIR/src/core/conversion_controller.sh"

# 显示版本信息
show_version() {
    echo "Everything2MD v1.0.0"
    echo "将各种办公文档格式转换为 Markdown 格式"
}

# 显示使用方法
show_usage() {
    echo "用法: $0 [选项] <输入文件> [输出文件]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -v, --verbose  启用详细输出"
    echo "  -V, --version  显示版本信息"
    echo ""
    echo "参数:"
    echo "  输入文件       要转换的源文件"
    echo "  输出文件       转换后的 Markdown 文件（可选，默认为输入文件同名的 .md 文件）"
    echo ""
    echo "支持的文件格式:"
    echo "  - Microsoft Word: .doc, .docx"
    echo "  - Microsoft PowerPoint: .ppt, .pptx"
    echo "  - PDF: .pdf"
    echo "  - 文本文件: .txt"
    echo "  - Markdown: .md, .markdown"
}

# 主函数
main() {
    # 解析命令行参数
    parse_args "$@"
    
    # 检查输入文件是否提供
    if [[ -z "$INPUT_FILE" ]]; then
        log_error "请提供输入文件"
        show_usage
        exit 1
    fi
    
    # 检查输入文件是否存在
    if ! file_exists "$INPUT_FILE"; then
        log_error "输入文件不存在: $INPUT_FILE"
        exit 1
    fi
    
    # 如果没有指定输出文件，则使用默认名称
    if [[ -z "$OUTPUT_FILE" ]]; then
        local input_name=$(get_file_name "$INPUT_FILE")
        OUTPUT_FILE="${input_name}.md"
    fi
    
    log_info "开始转换文件: $INPUT_FILE -> $OUTPUT_FILE"
    
    # 检测文件类型
    local file_type=$(detect_file_type "$INPUT_FILE")
    
    # 根据文件类型调用相应的处理函数
    case "$file_type" in
        office)
            process_office_file "$INPUT_FILE" "$OUTPUT_FILE"
            ;;
        pdf)
            process_pdf_file "$INPUT_FILE" "$OUTPUT_FILE"
            ;;
        markdown|text)
            process_known_file "$INPUT_FILE" "$OUTPUT_FILE" "$file_type"
            ;;
        unsupported)
            log_error "不支持的文件格式: $INPUT_FILE"
            exit 1
            ;;
        error)
            log_error "文件检测出错: $INPUT_FILE"
            exit 1
            ;;
    esac
    
    local result=$?
    
    if [[ $result -eq 0 ]]; then
        log_info "文件转换完成: $OUTPUT_FILE"
        exit 0
    else
        log_error "文件转换失败"
        exit 1
    fi
}

# 如果直接运行此脚本，则执行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
