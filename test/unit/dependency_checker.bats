#!/usr/bin/env bats

# 依赖检查模块测试

# 设置测试环境
setup() {
    # 获取项目根目录
    PROJECT_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
    
    # 加载日志模块（依赖检查模块需要）
    source "$PROJECT_ROOT/src/modules/logger.sh"
    
    # 定义空的 handle_error 函数（避免测试时退出）
    handle_error() {
        echo "ERROR: $1"
    }
    
    # 加载被测试的脚本
    source "$PROJECT_ROOT/src/modules/dependency_checker.sh"
}

@test "check_libreoffice_installed returns status code" {
    # 这个测试检查函数是否正确返回状态码
    # 不管LibreOffice是否安装，函数都应该返回0或1
    run check_libreoffice_installed
    [[ "$status" -eq 0 || "$status" -eq 1 ]]
}

@test "check_dependencies runs without fatal error" {
    # 这个测试验证依赖检查不会导致脚本崩溃
    # 即使某些依赖缺失，也应该能够继续运行
    run check_dependencies
    # 状态码可能是0（所有依赖都存在）或1（某些依赖缺失）
    [[ "$status" -eq 0 || "$status" -eq 1 ]]
}

@test "HAS_LIBREOFFICE variable is set after check_dependencies" {
    check_dependencies 2>/dev/null || true
    
    # 验证变量已被设置（true或false）
    [[ "$HAS_LIBREOFFICE" == "true" || "$HAS_LIBREOFFICE" == "false" ]]
}
