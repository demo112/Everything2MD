#!/bin/bash

# 依赖检查系统模块

# 检查所有依赖是否已安装
check_dependencies() {
    # 检查LibreOffice（必需）
    if ! command -v libreoffice >/dev/null 2>&1; then
        handle_error "LibreOffice未安装，这是必需的依赖"
        log_error "请安装LibreOffice后再运行程序"
        exit 1
    fi
    
    # 检查可选依赖并记录日志
    if ! command -v pandoc >/dev/null 2>&1; then
        log_warn "Pandoc未安装，将使用替代方案进行转换"
    else
        log_info "Pandoc已安装"
    fi
    
    if ! command -v pptx2md >/dev/null 2>&1; then
        log_warn "pptx2md未安装，PPTX文件转换可能受限"
    else
        log_info "pptx2md已安装"
    fi
    
    if ! command -v pdftotext >/dev/null 2>&1; then
        log_warn "pdftotext未安装，将使用替代方案进行PDF文本提取"
    else
        log_info "pdftotext已安装"
    fi
    
    log_info "依赖检查完成"
}