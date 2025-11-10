#!/bin/bash

# 日志记录器
# 用于记录程序运行过程中的信息

# 日志级别
LOG_LEVEL_INFO="INFO"
LOG_LEVEL_WARN="WARN"
LOG_LEVEL_ERROR="ERROR"

# 是否启用详细输出
VERBOSE=false

# 设置详细输出模式
set_verbose() {
    VERBOSE=$1
}

# 记录信息日志
log_info() {
    local message="$1"
    if [[ "$VERBOSE" == true ]]; then
        echo "[$LOG_LEVEL_INFO] $(date '+%Y-%m-%d %H:%M:%S') - $message"
    fi
}

# 记录警告日志
log_warn() {
    local message="$1"
    if [[ "$VERBOSE" == true ]]; then
        echo "[$LOG_LEVEL_WARN] $(date '+%Y-%m-%d %H:%M:%S') - $message"
    fi
}

# 记录错误日志
log_error() {
    local message="$1"
    echo "[$LOG_LEVEL_ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $message" >&2
}