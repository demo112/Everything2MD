#!/bin/bash

# Logger module

# Log level (default is INFO)
LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Get log level value
get_log_level_value() {
    case "$1" in
        DEBUG) echo 0 ;;
        INFO) echo 1 ;;
        WARN) echo 2 ;;
        ERROR) echo 3 ;;
        *) echo 1 ;;  # Default to INFO level
    esac
}

# Log debug message
log_debug() {
    local msg="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    if [[ $(get_log_level_value "$LOG_LEVEL") -le 0 ]]; then
        echo "[$timestamp] [DEBUG] $msg" >&2
    fi
}

# Log info message
log_info() {
    local msg="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    if [[ $(get_log_level_value "$LOG_LEVEL") -le 1 ]]; then
        echo "[$timestamp] [INFO] $msg" >&2
    fi
}

# Log warning message
log_warn() {
    local msg="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    if [[ $(get_log_level_value "$LOG_LEVEL") -le 2 ]]; then
        echo "[$timestamp] [WARN] $msg" >&2
    fi
}

# Log error message
log_error() {
    local msg="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    if [[ $(get_log_level_value "$LOG_LEVEL") -le 3 ]]; then
        echo "[$timestamp] [ERROR] $msg" >&2
    fi
}