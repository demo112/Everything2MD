#!/bin/bash

# 测试助手函数

# 创建测试文件
create_test_file() {
    local file_path="$1"
    local content="$2"
    
    mkdir -p "$(dirname "$file_path")"
    echo "$content" > "$file_path"
}

# 等待文件出现
wait_for_file() {
    local file_path="$1"
    local timeout="${2:-10}"
    local count=0
    
    while [[ ! -f "$file_path" ]] && [[ $count -lt $timeout ]]; do
        sleep 1
        ((count++))
    done
    
    [[ -f "$file_path" ]]
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}