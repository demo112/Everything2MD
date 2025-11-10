#!/bin/bash

# pptx2md 接口模块
# 用于调用 pptx2md 将 PowerPoint 文件转换为 Markdown

# 检查 pptx2md 是否可用
check_pptx2md() {
    if command -v pptx2md &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 使用 pptx2md 将 PPTX 文件转换为 Markdown
# 参数:
#   $1 - 输入 PPTX 文件路径
#   $2 - 输出文件路径
convert_pptx_to_markdown() {
    local input_file="$1"
    local output_file="$2"
    
    # 检查输入文件是否存在
    if [[ ! -f "$input_file" ]]; then
        echo "错误: 输入文件不存在: $input_file"
        return 1
    fi
    
    # 检查是否为 PPTX 文件
    local file_ext=$(echo "${input_file##*.}" | tr '[:upper:]' '[:lower:]')
    if [[ "$file_ext" != "pptx" ]]; then
        echo "错误: 输入文件不是 PPTX 格式: $input_file"
        return 1
    fi
    
    # 检查 pptx2md 是否可用
    if ! check_pptx2md; then
        echo "错误: pptx2md 未安装或不可用"
        return 1
    fi
    
    # 创建输出文件的目录（如果不存在）
    local output_dir=$(dirname "$output_file")
    mkdir -p "$output_dir"
    
    # 执行转换
    echo "正在使用 pptx2md 将 $input_file 转换为 Markdown..."
    pptx2md "$input_file" -o "$output_file"
    
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