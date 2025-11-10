#!/bin/bash

# Everything2MD 测试脚本
# 用于测试各种文件格式的转换功能

# 设置脚本基础目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 加载依赖模块
source "$PROJECT_DIR/src/utils/logger.sh"

# 测试函数
test_conversion() {
    local input_file="$1"
    local expected_output="$2"
    
    log_info "测试文件转换: $input_file"
    
    # 执行转换
    "$PROJECT_DIR/everything2md.sh" "$input_file" "$expected_output"
    local result=$?
    
    # 检查转换结果
    if [[ $result -eq 0 && -f "$expected_output" ]]; then
        log_info "转换成功: $expected_output"
        # 清理生成的文件
        rm "$expected_output"
        return 0
    else
        log_error "转换失败: $input_file"
        return 1
    fi
}

# 主函数
main() {
    log_info "开始执行转换测试"
    
    # 测试 Markdown 文件（直接复制）
    test_conversion "$SCRIPT_DIR/fixtures/sample.md" "$SCRIPT_DIR/expected/sample.md"
    
    # 测试文本文件（直接复制）
    test_conversion "$SCRIPT_DIR/fixtures/sample.txt" "$SCRIPT_DIR/expected/sample.txt"
    
    log_info "转换测试完成"
}

# 执行主函数
main "$@"