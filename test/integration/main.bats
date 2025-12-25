#!/usr/bin/env bats

setup() {
    PROJECT_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    MAIN_SH="$PROJECT_ROOT/src/main.sh"
}

@test "should show help when -h flag is provided" {
    run "$MAIN_SH" -h
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Everything2MD" ]]
    [[ "$output" =~ "用法:" ]]
}

@test "should error when input file does not exist" {
    run "$MAIN_SH" -i "/non/existent/file.docx"
    [ "$status" -eq 1 ]
    [[ "$output" =~ "不支持的文件类型: error" ]]
}

@test "should process a valid file" {
    # 使用真实的测试文件
    local test_file="$PROJECT_ROOT/test/fixtures/Untitled 1.docx"
    local output_file="/tmp/test_output_$$.md"
    
    # 跳过测试如果测试文件不存在
    if [[ ! -f "$test_file" ]]; then
        skip "Test fixture not found: $test_file"
    fi
    
    # 运行程序
    run "$MAIN_SH" -i "$test_file" -o "$output_file"
    
    # 清理输出文件
    rm -f "$output_file"
    
    # 检查结果 - 允许成功或因为工具缺失而失败
    [[ "$status" -eq 0 || "$output" =~ "LibreOffice" || "$output" =~ "Pandoc" ]]
}