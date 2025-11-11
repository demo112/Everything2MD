#!/usr/bin/env bats

# 加载被测试的脚本
load '../../src/modules/argument_parser.sh'

setup() {
    # 重置全局变量
    INPUT_PATH=""
    OUTPUT_PATH=""
    BATCH_MODE="false"
    CONFIG_FILE=""
    LOG_LEVEL="INFO"
}

@test "parse input path argument" {
    parse_arguments -i "/path/to/input.docx"
    [ "$INPUT_PATH" = "/path/to/input.docx" ]
}

@test "parse output path argument" {
    parse_arguments -i "/path/to/input.docx" -o "/path/to/output.md"
    [ "$OUTPUT_PATH" = "/path/to/output.md" ]
}

@test "parse batch mode argument" {
    parse_arguments -i "/path/to/input" -b
    [ "$BATCH_MODE" = "true" ]
}

@test "parse config file argument" {
    parse_arguments -i "/path/to/input.docx" -c "/path/to/config.ini"
    [ "$CONFIG_FILE" = "/path/to/config.ini" ]
}

@test "parse log level argument" {
    parse_arguments -i "/path/to/input.docx" -l "DEBUG"
    [ "$LOG_LEVEL" = "DEBUG" ]
}

@test "should error when input path is missing" {
    run parse_arguments -o "/path/to/output.md"
    [ "$status" -eq 1 ]
    [[ "$output" =~ "错误: 必须指定输入路径" ]]
}

@test "should use default output path for single file mode" {
    parse_arguments -i "/path/to/input.docx"
    [ "$OUTPUT_PATH" = "/path/to/input.md" ]
}

@test "should use default output path for batch mode" {
    parse_arguments -i "/path/to/input" -b
    [ "$OUTPUT_PATH" = "/path/to/output" ]
}

@test "should error when unknown argument is provided" {
    run parse_arguments -i "/path/to/input.docx" --unknown
    [ "$status" -eq 1 ]
    [[ "$output" =~ "未知参数: --unknown" ]]
}

@test "show help message" {
    run show_help
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Everything2MD - 将各种文档格式转换为Markdown" ]]
    [[ "$output" =~ "用法:" ]]
    [[ "$output" =~ "选项:" ]]
}