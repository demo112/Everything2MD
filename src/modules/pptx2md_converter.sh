#!/bin/bash

# pptx2md转换器模块

# 检查pptx2md是否已安装
check_pptx2md_installed() {
    if ! command -v pptx2md >/dev/null 2>&1; then
        handle_error "pptx2md未安装，请先安装pptx2md"
        return 1
    fi
    return 0
}

# 使用pptx2md将PPTX文件转换为Markdown
convert_pptx_to_md() {
    local input_file="$1"
    local output_path="$2"
    
    # 检查pptx2md是否已安装
    if ! check_pptx2md_installed; then
        return 1
    fi
    
    # 创建输出目录（如果不存在）
    mkdir -p "$(dirname "$output_path")"
    
    # 使用pptx2md转换
    # 注意：pptx2md通常会在指定目录下创建一个与PPTX文件同名的目录，并在其中生成Markdown文件
    local output_dir=$(dirname "$output_path")
    local base_name=$(basename "${input_file%.*}")
    local image_dir="$output_dir/img"
    
    # 创建图片目录
    mkdir -p "$image_dir"
    
    # 直接指定输出文件路径，而不是目录
    pptx2md "$input_file" -o "$output_path" -i "$image_dir"
    
    # 检查转换是否成功
    if [[ $? -ne 0 ]]; then
        handle_error "pptx2md转换失败: $input_file"
        return 1
    fi
    
    # 检查输出文件是否存在
    if [[ ! -f "$output_path" ]]; then
        handle_error "pptx2md转换后未找到生成的Markdown文件: $output_path"
        return 1
    fi
    
    log_info "成功转换PPTX文件: $input_file -> $output_path"
}