#!/bin/bash

# 错误处理模块

# 处理错误信息
handle_error() {
    local error_message="$1"
    local exit_code="${2:-1}"
    
    # 记录错误日志
    log_error "$error_message"
    
    # 如果不是在静默模式下，输出错误信息到标准错误
    if [[ "$SILENT_MODE" != "true" ]]; then
        echo "错误: $error_message" >&2
    fi
    
    # 如果退出码不为0，则退出程序
    if [[ $exit_code -ne 0 ]]; then
        exit $exit_code
    fi
}

# 设置静默模式
set_silent_mode() {
    local silent="$1"
    SILENT_MODE="$silent"
}