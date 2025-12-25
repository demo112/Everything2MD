#!/usr/bin/env bats

# 配置管理模块测试

# 设置测试环境
setup() {
    # 获取项目根目录
    PROJECT_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    
    # 创建临时测试目录
    TEST_TMP_DIR=$(mktemp -d)
    TEST_CONFIG_FILE="$TEST_TMP_DIR/config.json"
    
    # 保存原始配置路径
    ORIGINAL_CONFIG_DIR="$CONFIG_DIR"
    ORIGINAL_CONFIG_FILE="$CONFIG_FILE"
    
    # 设置测试配置路径
    export CONFIG_DIR="$TEST_TMP_DIR"
    export CONFIG_FILE="$TEST_CONFIG_FILE"
    
    # 加载被测试的脚本
    source "$PROJECT_ROOT/src/modules/logger.sh"
    source "$PROJECT_ROOT/src/modules/config_manager.sh"
}

# 清理测试环境
teardown() {
    # 恢复原始配置路径
    CONFIG_DIR="$ORIGINAL_CONFIG_DIR"
    CONFIG_FILE="$ORIGINAL_CONFIG_FILE"
    
    # 清理临时目录
    rm -rf "$TEST_TMP_DIR"
}

@test "create_default_config creates valid JSON config file" {
    create_default_config "$TEST_CONFIG_FILE"
    
    [ -f "$TEST_CONFIG_FILE" ]
    
    # 验证JSON格式有效
    if command -v jq &> /dev/null; then
        run jq . "$TEST_CONFIG_FILE"
        [ "$status" -eq 0 ]
    fi
}

@test "load_config creates default config when file does not exist" {
    # 确保配置文件不存在
    rm -f "$TEST_CONFIG_FILE"
    
    load_config "$TEST_CONFIG_FILE"
    
    # 验证配置文件已创建
    [ -f "$TEST_CONFIG_FILE" ]
}

@test "get_config returns correct default values" {
    create_default_config "$TEST_CONFIG_FILE"
    load_config "$TEST_CONFIG_FILE"
    
    run get_config "log_level"
    [ "$output" = "INFO" ]
    
    run get_config "output_format"
    [ "$output" = "markdown" ]
}

@test "set_config updates config value" {
    create_default_config "$TEST_CONFIG_FILE"
    load_config "$TEST_CONFIG_FILE"
    
    set_config "log_level" "DEBUG"
    
    run get_config "log_level"
    [ "$output" = "DEBUG" ]
}

@test "validate_config rejects invalid log level" {
    run validate_config "log_level" "INVALID"
    [ "$status" -eq 1 ]
}

@test "validate_config accepts valid log levels" {
    run validate_config "log_level" "DEBUG"
    [ "$status" -eq 0 ]
    
    run validate_config "log_level" "INFO"
    [ "$status" -eq 0 ]
    
    run validate_config "log_level" "WARN"
    [ "$status" -eq 0 ]
    
    run validate_config "log_level" "ERROR"
    [ "$status" -eq 0 ]
}

@test "validate_config rejects invalid output format" {
    run validate_config "output_format" "invalid_format"
    [ "$status" -eq 1 ]
}

@test "validate_config accepts valid output formats" {
    run validate_config "output_format" "markdown"
    [ "$status" -eq 0 ]
    
    run validate_config "output_format" "html"
    [ "$status" -eq 0 ]
    
    run validate_config "output_format" "txt"
    [ "$status" -eq 0 ]
}

@test "validate_config rejects invalid max_parallel_jobs" {
    run validate_config "max_parallel_jobs" "0"
    [ "$status" -eq 1 ]
    
    run validate_config "max_parallel_jobs" "17"
    [ "$status" -eq 1 ]
    
    run validate_config "max_parallel_jobs" "abc"
    [ "$status" -eq 1 ]
}

@test "validate_config accepts valid max_parallel_jobs" {
    run validate_config "max_parallel_jobs" "1"
    [ "$status" -eq 0 ]
    
    run validate_config "max_parallel_jobs" "8"
    [ "$status" -eq 0 ]
    
    run validate_config "max_parallel_jobs" "16"
    [ "$status" -eq 0 ]
}

@test "get_config returns error for unknown key" {
    create_default_config "$TEST_CONFIG_FILE"
    load_config "$TEST_CONFIG_FILE"
    
    run get_config "unknown_key"
    [ "$status" -eq 1 ]
}
