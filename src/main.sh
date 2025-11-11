#!/bin/bash

# Everything2MD - 将各种文档格式转换为Markdown
# 作者: 
# 版本: 1.0
# 日期: 

# 设置脚本在遇到错误时立即退出
set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 导入各个模块
source "$SCRIPT_DIR/modules/argument_parser.sh"
source "$SCRIPT_DIR/modules/file_detector.sh"
source "$SCRIPT_DIR/modules/libreoffice_converter.sh"
source "$SCRIPT_DIR/modules/pptx2md_converter.sh"
source "$SCRIPT_DIR/modules/pandoc_converter.sh"
source "$SCRIPT_DIR/modules/file_copier.sh"
source "$SCRIPT_DIR/modules/dependency_checker.sh"
source "$SCRIPT_DIR/modules/batch_processor.sh"
source "$SCRIPT_DIR/modules/config_manager.sh"
source "$SCRIPT_DIR/modules/error_handler.sh"
source "$SCRIPT_DIR/modules/logger.sh"

# 主函数
main() {
    # 检查依赖
    check_dependencies
    
    # 解析参数
    parse_arguments "$@"
    
    # 如果是批量处理模式
    if [[ "$BATCH_MODE" == "true" ]]; then
        process_batch "$INPUT_PATH"
    else
        # 处理单个文件
        process_single_file "$INPUT_PATH" "$OUTPUT_PATH"
    fi
}

# 处理单个文件
process_single_file() {
    local input_file="$1"
    local output_path="$2"
    
    # 检测文件类型
    local file_type=$(detect_file_type "$input_file")
    
    # 根据文件类型选择处理方式
    case "$file_type" in
        "office")
            convert_office_to_md "$input_file" "$output_path"
            ;;
        "pptx")
            convert_pptx_to_md "$input_file" "$output_path"
            ;;
        "text")
            copy_text_file "$input_file" "$output_path"
            ;;
        *)
            handle_error "不支持的文件类型: $file_type"
            ;;
    esac
}

# 运行主函数
main "$@"