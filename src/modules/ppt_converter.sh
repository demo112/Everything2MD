#!/bin/bash

# PPT转换器模块

# 检查LibreOffice是否已安装
check_libreoffice_installed() {
    if ! command -v libreoffice >/dev/null 2>&1; then
        handle_error "LibreOffice未安装，请先安装LibreOffice"
        return 1
    fi
    return 0
}

# 使用LibreOffice将PPT文件转换为Markdown
convert_ppt_to_md() {
    local input_file="$1"
    local output_path="$2"
    
    # 检查LibreOffice是否已安装
    if ! check_libreoffice_installed; then
        return 1
    fi
    
    # 创建输出目录（如果不存在）
    mkdir -p "$(dirname "$output_path")"
    
    # 创建临时目录
    local temp_dir=$(mktemp -d)
    
    # 处理文件名中的特殊字符，创建安全的临时文件路径
    local safe_input_file="$temp_dir/$(basename "$input_file")"
    cp "$input_file" "$safe_input_file"
    
    # 使用LibreOffice直接转换为PDF（不使用服务模式）
    libreoffice --headless --convert-to pdf --outdir "$temp_dir" "$safe_input_file"
    
    # 检查转换是否成功
    local convert_result=$?
    if [[ $convert_result -ne 0 ]]; then
        rm -rf "$temp_dir"
        handle_error "LibreOffice转换PPT到PDF失败: $input_file (错误代码: $convert_result)"
        return 1
    fi
    
    # 获取转换后的PDF文件路径
    local pdf_file=""
    for file in "$temp_dir"/*.pdf; do
        if [[ -f "$file" ]]; then
            pdf_file="$file"
            break
        fi
    done
    
    # 检查PDF文件是否存在
    if [[ -z "$pdf_file" || ! -f "$pdf_file" ]]; then
        rm -rf "$temp_dir"
        handle_error "LibreOffice转换后未找到生成的PDF文件: $input_file"
        return 1
    fi
    
    # 使用pdftotext提取文本内容
    if command -v pdftotext >/dev/null 2>&1; then
        # 提取纯文本，使用UTF-8编码
        pdftotext -layout -enc UTF-8 "$pdf_file" "$output_path"
    elif command -v pandoc >/dev/null 2>&1; then
        # 使用Pandoc将PDF转换为Markdown
        pandoc -f pdf -t markdown "$pdf_file" -o "$output_path" --extract-media="$(dirname "$output_path")/images"
    else
        # 如果没有pdftotext或pandoc，直接复制PDF文件
        cp "$pdf_file" "$output_path"
        rm -rf "$temp_dir"
        handle_error "没有可用的PDF转文本工具(pdftotext或pandoc)"
        return 1
    fi
    
    # 检查转换是否成功
    if [[ $? -ne 0 ]]; then
        rm -rf "$temp_dir"
        handle_error "PDF到Markdown转换失败: $input_file"
        return 1
    fi
    
    # 检查输出文件是否存在
    if [[ ! -f "$output_path" ]]; then
        rm -rf "$temp_dir"
        handle_error "转换后未找到生成的Markdown文件: $output_path"
        return 1
    fi
    
    # 清理临时目录
    rm -rf "$temp_dir"
    
    log_info "成功转换PPT文件: $input_file -> $output_path"
}