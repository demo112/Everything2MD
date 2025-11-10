#!/bin/bash

# 批量处理模块

# 批量处理目录中的文件
process_batch() {
    local input_dir="$1"
    local output_dir="$2"
    
    # 如果没有指定输出目录，使用默认值
    if [[ -z "$output_dir" ]]; then
        output_dir="$input_dir/output"
    fi
    
    # 创建输出目录
    mkdir -p "$output_dir"
    
    # 检查输入目录是否存在
    if [[ ! -d "$input_dir" ]]; then
        handle_error "输入目录不存在: $input_dir"
        return 1
    fi
    
    # 记录处理开始
    log_info "开始批量处理目录: $input_dir"
    
    # 遍历目录中的所有文件
    local file_count=0
    local success_count=0
    local error_count=0
    
    while IFS= read -r -d '' file; do
        # 跳过目录
        [[ -d "$file" ]] && continue
        
        # 增加文件计数
        ((file_count++))
        
        # 生成输出文件路径
        local relative_path="${file#$input_dir/}"
        local output_file="$output_dir/${relative_path%.*}.md"
        
        # 创建输出文件的目录
        mkdir -p "$(dirname "$output_file")"
        
        # 处理单个文件
        if process_single_file "$file" "$output_file"; then
            ((success_count++))
            log_info "成功处理文件 ($success_count/$file_count): $file"
        else
            ((error_count++))
            log_error "处理文件失败 ($error_count/$file_count): $file"
        fi
    done < <(find "$input_dir" -type f -print0)
    
    # 记录处理结束
    log_info "批量处理完成: 总计$file_count个文件，成功$success_count个，失败$error_count个"
}