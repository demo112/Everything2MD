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
    
    # 处理文件名中的特殊字符，创建安全的临时文件路径
    local safe_input_file="$temp_dir/$(basename "$input_file")"
    cp "$input_file" "$safe_input_file"
    
    # 使用LibreOffice转换为HTML
    libreoffice --headless --convert-to html --outdir "$temp_dir" "$safe_input_file" >/dev/null 2>&1
    
    # 检查转换是否成功
    if [[ $? -ne 0 ]]; then
        rm -rf "$temp_dir"
        handle_error "LibreOffice转换失败: $input_file"
        return 1
    fi
    
    # 获取转换后的HTML文件路径（使用更精确的匹配方式）
    local html_file=""
    # 查找转换生成的HTML文件
    for file in "$temp_dir"/*.html; do
        if [[ -f "$file" ]]; then
            html_file="$file"
            break
        fi
    done
    
    # 如果没有找到HTML文件，尝试其他可能的文件名模式
    if [[ -z "$html_file" || ! -f "$html_file" ]]; then
        # 获取不带扩展名的文件名
        local base_name=$(basename "${input_file%.*}")
        # 尝试不同的可能文件名
        local possible_names=("$temp_dir/${base_name}.html" "$temp_dir/$(basename "$input_file" .docx).html" "$temp_dir/$(basename "$input_file" .doc).html")
        for name in "${possible_names[@]}"; do
            if [[ -f "$name" ]]; then
                html_file="$name"
                break
            fi
        done
    fi
    
    # 检查HTML文件是否存在
    if [[ -z "$html_file" || ! -f "$html_file" ]]; then
        # 列出临时目录中的所有文件以帮助调试
        local temp_files=$(ls -la "$temp_dir" 2>/dev/null || echo "无法列出目录内容")
        rm -rf "$temp_dir"
        handle_error "LibreOffice转换后的HTML文件不存在。输入文件: $input_file, 临时目录内容: $temp_files"
        return 1
    fi
    
    # 使用Pandoc将HTML转换为Markdown
    if command -v pandoc >/dev/null 2>&1; then
        pandoc -f html -t markdown "$html_file" -o "$output_path"
    else
        # 如果没有Pandoc，直接复制HTML文件
        cp "$html_file" "$output_path"
    fi
    
    # 清理临时目录
    rm -rf "$temp_dir"
    
    log_info "成功转换Office文档: $input_file -> $output_path"
}