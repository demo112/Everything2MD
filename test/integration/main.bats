#!/usr/bin/env bats

@test "should show help when -h flag is provided" {
    run /Users/cooperd/UNV/TraeProject/Everything2MD/src/main.sh -h
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Everything2MD" ]]
    [[ "$output" =~ "用法:" ]]
}

@test "should error when input file does not exist" {
    run /Users/cooperd/UNV/TraeProject/Everything2MD/src/main.sh -i "/non/existent/file.docx"
    [ "$status" -eq 1 ]
    [[ "$output" =~ "不支持的文件类型: error" ]]
}

@test "should process a valid file" {
    # 创建一个测试文件
    local test_file="/tmp/test.docx"
    touch "$test_file"
    
    # 运行程序
    run /Users/cooperd/UNV/TraeProject/Everything2MD/src/main.sh -i "$test_file"
    
    # 清理测试文件
    rm -f "$test_file"
    
    # 检查结果
    [ "$status" -eq 0 ]
}