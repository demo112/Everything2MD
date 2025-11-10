#!/bin/bash

# 依赖检查系统模块

# 检查所有依赖是否已安装
check_dependencies() {
    local missing_deps=()
    
    # 检查LibreOffice
    if ! command -v libreoffice >/dev/null 2>&1; then
        missing_deps+=("LibreOffice")
    fi
    
    # 检查Pandoc
    if ! command -v pandoc >/dev/null 2>&1; then
        missing_deps+=("Pandoc")
    fi
    
    # 检查pptx2md
    if ! command -v pptx2md >/dev/null 2>&1; then
        missing_deps+=("pptx2md")
    fi
    
    # 如果有缺失的依赖，报错并退出
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        handle_error "以下依赖未安装: ${missing_deps[*]}"
        log_error "请安装缺失的依赖后再运行程序"
        exit 1
    fi
    
    log_info "所有依赖检查通过"
}