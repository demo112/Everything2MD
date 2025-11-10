#!/bin/bash

# 日志记录模块

# 日志级别（默认为INFO）
LOG_LEVEL="${LOG_LEVEL:-INFO}"

# 获取日志级别的数值
get_log_level_value() {
    case "$1" in
        DEBUG) echo 0 ;;
        INFO) echo 1 ;;
        WARN) echo 2 ;;
        ERROR) echo 3 ;;
        *) echo 1 ;;  # 默认为INFO级别
    esac
}

# 记录调试信息
log_debug() {
    local message="$1"
    log_message "DEBUG" "$message"
}

# 记录普通信息
log_info() {
    local message="$1"
    log_message "INFO" "$message"
}

# 记录警告信息
log_warn() {
    local message="$1"
    log_message "WARN" "$message"
}

# 记录错误信息
log_error() {
    local message="$1"
    log_message "ERROR" "$message"
}

# 记录日志消息
log_message() {
    local level="$1"
    local message="$2"
    
    # 检查日志级别是否应该输出
    local level_value=$(get_log_level_value "$level")
    local current_level_value=$(get_log_level_value "$LOG_LEVEL")
    
    if [[ $level_value -lt $current_level_value ]]; then
        return
    fi
    
    # 获取当前时间戳
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 输出日志消息
    echo "[$timestamp] [$level] $message"
}

# 设置日志级别
set_log_level() {
    local level="$1"
    
    # 检查日志级别是否有效
    local level_value=$(get_log_level_value "$level")
    if [[ $level_value -eq 1 && "$level" != "INFO" ]]; then
        echo "无效的日志级别: $level" >&2
        return 1
    fi
    
    LOG_LEVEL="$level"
}