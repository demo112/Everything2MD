#!/usr/bin/env bats

# 文件类型检测模块测试

# 设置测试环境
setup() {
    # 获取项目根目录
    PROJECT_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    
    # 创建临时测试目录
    TEST_TMP_DIR=$(mktemp -d)
    
    # 加载被测试的脚本
    source "$PROJECT_ROOT/src/modules/file_detector.sh"
}

# 清理测试环境
teardown() {
    # 清理临时目录
    rm -rf "$TEST_TMP_DIR"
}

@test "detect_file_type returns 'office' for .doc files" {
    local test_file="$TEST_TMP_DIR/test.doc"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "office" ]
}

@test "detect_file_type returns 'office' for .docx files" {
    local test_file="$TEST_TMP_DIR/test.docx"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "office" ]
}

@test "detect_file_type returns 'office' for .xls files" {
    local test_file="$TEST_TMP_DIR/test.xls"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "office" ]
}

@test "detect_file_type returns 'office' for .xlsx files" {
    local test_file="$TEST_TMP_DIR/test.xlsx"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "office" ]
}

@test "detect_file_type returns 'ppt' for .ppt files" {
    local test_file="$TEST_TMP_DIR/test.ppt"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "ppt" ]
}

@test "detect_file_type returns 'pptx' for .pptx files" {
    local test_file="$TEST_TMP_DIR/test.pptx"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "pptx" ]
}

@test "detect_file_type returns 'text' for .txt files" {
    local test_file="$TEST_TMP_DIR/test.txt"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "text" ]
}

@test "detect_file_type returns 'text' for .md files" {
    local test_file="$TEST_TMP_DIR/test.md"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "text" ]
}

@test "detect_file_type returns 'text' for .markdown files" {
    local test_file="$TEST_TMP_DIR/test.markdown"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "text" ]
}

@test "detect_file_type returns 'error' for non-existent files" {
    run detect_file_type "/non/existent/file.docx"
    [ "$output" = "error" ]
}

@test "detect_file_type handles uppercase extensions" {
    local test_file="$TEST_TMP_DIR/test.DOCX"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "office" ]
}

@test "detect_file_type handles mixed case extensions" {
    local test_file="$TEST_TMP_DIR/test.DocX"
    touch "$test_file"
    
    run detect_file_type "$test_file"
    [ "$output" = "office" ]
}
