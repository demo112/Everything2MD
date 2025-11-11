#!/usr/bin/env bats

# 加载被测试的脚本
load '../../src/modules/logger.sh'

setup() {
    # 保存原始的日志级别
    ORIGINAL_LOG_LEVEL="$LOG_LEVEL"
    # 重置日志级别为INFO
    LOG_LEVEL="INFO"
}

teardown() {
    # 恢复原始的日志级别
    LOG_LEVEL="$ORIGINAL_LOG_LEVEL"
}

@test "get log level value" {
    run get_log_level_value "DEBUG"
    [ "$output" = "0" ]
    
    run get_log_level_value "INFO"
    [ "$output" = "1" ]
    
    run get_log_level_value "WARN"
    [ "$output" = "2" ]
    
    run get_log_level_value "ERROR"
    [ "$output" = "3" ]
    
    run get_log_level_value "UNKNOWN"
    [ "$output" = "1" ]
}

@test "log debug message" {
    LOG_LEVEL="DEBUG"
    run log_debug "Debug message"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "DEBUG" ]]
    [[ "$output" =~ "Debug message" ]]
}

@test "log info message" {
    run log_info "Info message"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "INFO" ]]
    [[ "$output" =~ "Info message" ]]
}

@test "log warning message" {
    run log_warn "Warning message"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "WARN" ]]
    [[ "$output" =~ "Warning message" ]]
}

@test "log error message" {
    run log_error "Error message"
    [ "$status" -eq 0 ]
    [[ "$output" =~ "ERROR" ]]
    [[ "$output" =~ "Error message" ]]
}

@test "log level filtering - DEBUG level should output all logs" {
    LOG_LEVEL="DEBUG"
    run log_debug "Debug message"
    [ "$status" -eq 0 ]
    [ -n "$output" ]
}

@test "log level filtering - INFO level should filter DEBUG logs" {
    LOG_LEVEL="INFO"
    run log_message "DEBUG" "Debug message"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "log level filtering - WARN level should filter DEBUG and INFO logs" {
    LOG_LEVEL="WARN"
    run log_message "INFO" "Info message"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "set log level" {
    # 直接调用函数而不是使用run命令，因为run会创建子shell，不会影响父进程的变量
    set_log_level "DEBUG"
    [ "$LOG_LEVEL" = "DEBUG" ]
    
    set_log_level "ERROR"
    [ "$LOG_LEVEL" = "ERROR" ]
}

@test "set invalid log level" {
    run set_log_level "INVALID"
    [ "$status" -eq 1 ]  # 无效级别应该返回错误
    [[ "$output" =~ "无效的日志级别" ]]
}