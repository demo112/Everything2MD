#!/bin/bash

# Pandoc转换器模块

# 检查Pandoc是否已安装
check_pandoc_installed() {
    if ! command -v pandoc >/dev/null 2>&1; then
        handle_error "Pandoc未安装，请先安装Pandoc"
        return 1
    fi
    return 0
}

# 使用Pandoc将文档转换为Markdown
convert_with_pandoc() {
    local input_file="$1"
    local output_path="$2"
    local from_format="$3"
    
    # 检查Pandoc是否已安装
    if ! check_pandoc_installed; then
        return 1
    fi
    
    # 构建Pandoc命令
    local pandoc_cmd="pandoc"
    
    # 添加源格式参数（如果指定）
    if [[ -n "$from_format" ]]; then
        pandoc_cmd+=" -f $from_format"
    fi
    
    # 添加目标格式参数
    pandoc_cmd+=" -t markdown"
    
    # 添加输入和输出文件参数
    pandoc_cmd+=" \"$input_file\" -o \"$output_path\""
    
    # 执行转换
    eval $pandoc_cmd
    
    # 检查转换是否成功
    if [[ $? -ne 0 ]]; then
        handle_error "Pandoc转换失败: $input_file"
        return 1
    fi
    
    log_info "成功使用Pandoc转换文档: $input_file -> $output_path"
}

# 转换HTML到Markdown
convert_html_to_md() {
    local input_file="$1"
    local output_path="$2"
    
    convert_with_pandoc "$input_file" "$output_path" "html"
}