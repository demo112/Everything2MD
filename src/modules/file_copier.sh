#!/bin/bash

# 直接复制模块

# 复制文本文件
copy_text_file() {
    local input_file="$1"
    local output_path="$2"
    
    # 检查输入文件是否存在
    if [[ ! -f "$input_file" ]]; then
        handle_error "输入文件不存在: $input_file"
        return 1
    fi
    
    # 创建输出目录（如果不存在）
    mkdir -p "$(dirname "$output_path")"
    
    # 直接复制文件
    cp "$input_file" "$output_path"
    
    # 检查复制是否成功
    if [[ $? -ne 0 ]]; then
        handle_error "文件复制失败: $input_file -> $output_path"
        return 1
    fi
    
    log_info "成功复制文件: $input_file -> $output_path"
}