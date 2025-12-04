#!/bin/bash

# 批量处理模块

# 批量处理目录中的文件
process_batch() {
    local input_dir="$1"
    local output_dir="$2"
    
    # 如果没有指定输出目录，使用默认值
    # 但如果是通过 main.sh 自动切换过来的，$output_dir 可能是空的
    # 此时我们希望保持原有结构，或者在同目录下生成
    # 这里修改策略：如果未指定输出目录，则在原文件同级目录生成 .md (in-place)
    # 或者如果用户希望输出到 output 子目录，则保持原逻辑。
    # 根据用户习惯 "同目录下生成同名.md"，我们这里稍微调整：
    if [[ -z "$output_dir" ]]; then
        # 如果未指定输出目录，则遍历时直接在源文件同目录生成
        output_dir="" 
    else
        # 创建输出目录
        mkdir -p "$output_dir"
    fi
    
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
        local output_file=""
        if [[ -z "$output_dir" ]]; then
            output_file="${file%.*}.md"
        else
            local relative_path="${file#$input_dir/}"
            output_file="$output_dir/${relative_path%.*}.md"
            # 创建输出文件的目录
            mkdir -p "$(dirname "$output_file")"
        fi
        
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