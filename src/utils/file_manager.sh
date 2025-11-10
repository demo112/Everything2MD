#!/bin/bash

# 文件管理器
# 用于处理临时文件的创建、使用和清理

# 创建临时目录
create_temp_dir() {
    local prefix="${1:-everything2md}"
    local temp_dir=$(mktemp -d "/tmp/${prefix}.XXXXXX")
    echo "$temp_dir"
}

# 检查文件是否存在
file_exists() {
    local file_path="$1"
    if [[ -f "$file_path" ]]; then
        return 0
    else
        return 1
    fi
}

# 检查目录是否存在
dir_exists() {
    local dir_path="$1"
    if [[ -d "$dir_path" ]]; then
        return 0
    else
        return 1
    fi
}

# 获取文件扩展名
get_file_extension() {
    local file_path="$1"
    local extension="${file_path##*.}"
    echo "$extension"
}

# 获取文件名（不包含路径和扩展名）
get_file_name() {
    local file_path="$1"
    local file_name=$(basename "$file_path")
    local name="${file_name%.*}"
    echo "$name"
}

# 创建目录（如果不存在）
mkdir_p() {
    local dir_path="$1"
    if ! dir_exists "$dir_path"; then
        mkdir -p "$dir_path"
    fi
}