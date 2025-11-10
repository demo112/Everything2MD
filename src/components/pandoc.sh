#!/bin/bash

# Pandoc 接口模块
# 用于调用 Pandoc 将各种格式文件转换为 Markdown

# 检查 Pandoc 是否可用
check_pandoc() {
    if command -v pandoc &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 使用 Pandoc 将文件转换为 Markdown
# 参数:
#   $1 - 输入文件路径
#   $2 - 输出文件路径
convert_to_markdown() {
    local input_file="$1"
    local output_file="$2"
    
    # 检查输入文件是否存在
    if [[ ! -f "$input_file" ]]; then
        echo "错误: 输入文件不存在: $input_file"
        return 1
    fi
    
    # 检查 Pandoc 是否可用
    if ! check_pandoc; then
        echo "错误: Pandoc 未安装或不可用"
        return 1
    fi
    
    # 创建输出文件的目录（如果不存在）
    local output_dir=$(dirname "$output_file")
    mkdir -p "$output_dir"
    
    # 执行转换
    echo "正在使用 Pandoc 将 $input_file 转换为 Markdown..."
    pandoc "$input_file" -f markdown -t markdown -o "$output_file" --wrap=none
    
    # 检查转换是否成功
    if [[ -f "$output_file" ]]; then
        echo "转换成功: $output_file"
        echo "$output_file"
        return 0
    else
        echo "转换失败: 无法生成输出文件 $output_file"
        return 1
    fi
}

# 使用 Pandoc 将 PDF 文件转换为 Markdown（需要先转换为 HTML）
# 参数:
#   $1 - 输入 PDF 文件路径
#   $2 - 输出文件路径
convert_pdf_to_markdown() {
    local input_file="$1"
    local output_file="$2"
    
    # 检查输入文件是否存在
    if [[ ! -f "$input_file" ]]; then
        echo "错误: 输入文件不存在: $input_file"
        return 1
    fi
    
    # 检查是否为 PDF 文件
    local file_ext=$(echo "${input_file##*.}" | tr '[:upper:]' '[:lower:]')
    if [[ "$file_ext" != "pdf" ]]; then
        echo "错误: 输入文件不是 PDF 格式: $input_file"
        return 1
    fi
    
    # 检查 Pandoc 是否可用
    if ! check_pandoc; then
        echo "错误: Pandoc 未安装或不可用"
        return 1
    fi
    
    # 创建输出文件的目录（如果不存在）
    local output_dir=$(dirname "$output_file")
    mkdir -p "$output_dir"
    
    # 执行转换
    echo "正在使用 Pandoc 将 $input_file 转换为 Markdown..."
    pandoc "$input_file" -f html -t markdown -o "$output_file" --wrap=none
    
    # 检查转换是否成功
    if [[ -f "$output_file" ]]; then
        echo "转换成功: $output_file"
        echo "$output_file"
        return 0
    else
        echo "转换失败: 无法生成输出文件 $output_file"
        return 1
    fi
}