#!/bin/bash

# Everything2MD - 将各种文档格式转换为Markdown
# 作者: 
# 版本: 1.1
# 日期: 2025-11-11 

# 设置脚本在遇到错误时立即退出
set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 导入各个模块
source "$SCRIPT_DIR/modules/logger.sh"        # Logger first
source "$SCRIPT_DIR/modules/env_loader.sh"    # Load env vars (tools)
source "$SCRIPT_DIR/modules/argument_parser.sh"
source "$SCRIPT_DIR/modules/file_detector.sh"
source "$SCRIPT_DIR/modules/libreoffice_converter.sh"
source "$SCRIPT_DIR/modules/ppt_converter.sh"
source "$SCRIPT_DIR/modules/pptx2md_converter.sh"
source "$SCRIPT_DIR/modules/pandoc_converter.sh"
source "$SCRIPT_DIR/modules/file_copier.sh"
source "$SCRIPT_DIR/modules/dependency_checker.sh"
source "$SCRIPT_DIR/modules/batch_processor.sh"
source "$SCRIPT_DIR/modules/config_manager.sh"
source "$SCRIPT_DIR/modules/error_handler.sh"
# Logger is already loaded at the top
# source "$SCRIPT_DIR/modules/logger.sh"

# 主函数
main() {
    # 检查依赖
    check_dependencies
    
    # 解析参数
    parse_arguments "$@"
    
    # 智能判断：如果输入是目录，自动切换到批量模式
    if [[ -d "$INPUT_PATH" ]]; then
        log_info "输入路径是目录，自动切换到批量处理模式"
        process_batch "$INPUT_PATH"
    elif [[ "$BATCH_MODE" == "true" ]]; then
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
    
    # 处理输出路径逻辑
    # 1. 如果输出路径为空，默认为输入文件同目录下的同名 .md 文件
    if [[ -z "$output_path" ]]; then
        output_path="${input_file%.*}.md"
    # 2. 如果输出路径是一个已存在的目录，则在该目录下生成同名 .md 文件
    elif [[ -d "$output_path" ]]; then
        local filename=$(basename "$input_file")
        output_path="${output_path}/${filename%.*}.md"
    # 3. 如果输出路径以 / 结尾（即使用户想指定目录但目录不存在），也当作目录处理
    elif [[ "$output_path" == */ ]]; then
        mkdir -p "$output_path"
        local filename=$(basename "$input_file")
        output_path="${output_path}${filename%.*}.md"
    fi

    log_info "处理文件: $input_file -> $output_path"
    
    # 检测文件类型
    local file_type=$(detect_file_type "$input_file")
    
    # 根据文件类型选择处理方式
    case "$file_type" in
        "office")
            convert_office_to_md "$input_file" "$output_path"
            ;;
        "ppt")
            convert_ppt_to_md "$input_file" "$output_path"
            ;;
        "pptx")
            convert_pptx_to_md "$input_file" "$output_path"
            ;;
        "pdf")
            # 先用LibreOffice将PDF转换为HTML，再用Pandoc转换为Markdown
            convert_office_to_md "$input_file" "$output_path"
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