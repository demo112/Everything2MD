#!/bin/bash

# LibreOffice转换器模块

# 检查LibreOffice是否已安装
check_libreoffice_installed() {
    if ! command -v libreoffice >/dev/null 2>&1; then
        handle_error "LibreOffice未安装，请先安装LibreOffice"
        return 1
    fi
    return 0
}

# 使用LibreOffice将Office文档转换为Markdown
convert_office_to_md() {
    local input_file="$1"
    local output_path="$2"
    
    # 检查LibreOffice是否已安装
    if ! check_libreoffice_installed; then
        return 1
    fi
    
    # 创建临时目录
    local temp_dir=$(mktemp -d)
    
    # 使用LibreOffice转换为HTML
    libreoffice --headless --convert-to html --outdir "$temp_dir" "$input_file" >/dev/null 2>&1
    
    # 检查转换是否成功
    if [[ $? -ne 0 ]]; then
        rm -rf "$temp_dir"
        handle_error "LibreOffice转换失败: $input_file"
        return 1
    fi
    
    # 获取转换后的HTML文件路径
    local html_file="$temp_dir/$(basename "${input_file%.*}").html"
    
    # 检查HTML文件是否存在
    if [[ ! -f "$html_file" ]]; then
        rm -rf "$temp_dir"
        handle_error "LibreOffice转换后的HTML文件不存在: $html_file"
        return 1
    fi
    
    # 使用Pandoc将HTML转换为Markdown
    if command -v pandoc >/dev/null 2>&1; then
        pandoc -f html -t markdown "$html_file" -o "$output_path"
    else
        # 如果没有Pandoc，直接复制HTML文件
        cp "$html_file" "$output_path"
        log_warn "Pandoc未安装，无法将HTML转换为Markdown，直接复制HTML文件"
    fi
    
    # 清理临时目录
    rm -rf "$temp_dir"
    
    log_info "成功转换Office文档: $input_file -> $output_path"
}