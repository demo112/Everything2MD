#!/bin/bash

# LibreOffice 接口模块
# 用于调用 LibreOffice 将 doc/docx/ppt 文件转换为 pdf

# 检查 LibreOffice 是否可用
check_libreoffice() {
    if command -v libreoffice &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 使用 LibreOffice 将文件转换为 PDF
# 参数:
#   $1 - 输入文件路径
#   $2 - 输出目录路径
convert_to_pdf() {
    local input_file="$1"
    local output_dir="$2"
    
    # 检查输入文件是否存在
    if [[ ! -f "$input_file" ]]; then
        echo "错误: 输入文件不存在: $input_file"
        return 1
    fi
    
    # 检查 LibreOffice 是否可用
    if ! check_libreoffice; then
        echo "错误: LibreOffice 未安装或不可用"
        return 1
    fi
    
    # 创建输出目录（如果不存在）
    mkdir -p "$output_dir"
    
    # 执行转换
    echo "正在使用 LibreOffice 将 $input_file 转换为 PDF..."
    libreoffice --headless --convert-to pdf --outdir "$output_dir" "$input_file"
    
    # 检查转换是否成功
    local file_name=$(basename "$input_file")
    local name="${file_name%.*}"
    local output_file="$output_dir/$name.pdf"
    
    if [[ -f "$output_file" ]]; then
        echo "转换成功: $output_file"
        echo "$output_file"
        return 0
    else
        echo "转换失败: 无法生成输出文件 $output_file"
        return 1
    fi
}