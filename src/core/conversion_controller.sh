#!/bin/bash

# 转换流程控制器
# 控制整个文件转换流程，根据文件类型调用相应的转换组件

# 加载依赖模块
source ./utils/logger.sh
source ./utils/file_manager.sh
source ./components/libreoffice.sh
source ./components/pandoc.sh
source ./components/pptx2md.sh

# 处理 Office 文件 (doc, docx, ppt, pptx)
# 参数:
#   $1 - 输入文件路径
#   $2 - 输出文件路径
process_office_file() {
    local input_file="$1"
    local output_file="$2"
    
    log_info "开始处理 Office 文件: $input_file"
    
    # 获取文件扩展名
    local file_ext=$(echo "${input_file##*.}" | tr '[:upper:]' '[:lower:]')
    
    # 对于 PPTX 文件，直接使用 pptx2md 转换
    if [[ "$file_ext" == "pptx" ]]; then
        log_info "检测到 PPTX 文件，使用 pptx2md 进行转换"
        convert_pptx_to_markdown "$input_file" "$output_file"
        return $?
    fi
    
    # 对于其他 Office 文件，先转换为 PDF，再转换为 Markdown
    local temp_dir=$(create_temp_dir)
    local pdf_file="$temp_dir/$(get_file_name "$input_file").pdf"
    
    log_info "使用 LibreOffice 将 Office 文件转换为 PDF"
    if convert_to_pdf "$input_file" "$temp_dir"; then
        log_info "使用 Pandoc 将 PDF 转换为 Markdown"
        convert_pdf_to_markdown "$pdf_file" "$output_file"
        local result=$?
        # 清理临时目录
        rm -rf "$temp_dir"
        return $result
    else
        log_error "LibreOffice 转换失败"
        # 清理临时目录
        rm -rf "$temp_dir"
        return 1
    fi
}

# 处理 PDF 文件
# 参数:
#   $1 - 输入文件路径
#   $2 - 输出文件路径
process_pdf_file() {
    local input_file="$1"
    local output_file="$2"
    
    log_info "开始处理 PDF 文件: $input_file"
    convert_pdf_to_markdown "$input_file" "$output_file"
    return $?
}

# 处理已知格式文件（直接复制或简单转换）
# 参数:
#   $1 - 输入文件路径
#   $2 - 输出文件路径
#   $3 - 文件类型
process_known_file() {
    local input_file="$1"
    local output_file="$2"
    local file_type="$3"
    
    log_info "开始处理 $file_type 文件: $input_file"
    
    # 创建输出目录
    local output_dir=$(dirname "$output_file")
    mkdir_p "$output_dir"
    
    case "$file_type" in
        markdown)
            log_info "Markdown 文件，直接复制"
            cp "$input_file" "$output_file"
            ;;
        text)
            log_info "文本文件，直接复制"
            cp "$input_file" "$output_file"
            ;;
        *)
            log_error "不支持的文件类型: $file_type"
            return 1
            ;;
    esac
    
    echo "$output_file"
    return 0
}