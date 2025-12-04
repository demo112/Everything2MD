#!/bin/bash

# 依赖检查系统模块

# 检查所有依赖是否已安装
check_dependencies() {
    # 检查LibreOffice/soffice
    HAS_LIBREOFFICE=false
    if command -v libreoffice >/dev/null 2>&1; then
        HAS_LIBREOFFICE=true
        log_info "检测到 libreoffice"
    elif command -v soffice >/dev/null 2>&1; then
        HAS_LIBREOFFICE=true
        log_info "检测到 soffice"
    else
        log_warn "LibreOffice未安装，部分功能(PDF/PPT转换)将受限，DOCX将尝试使用Pandoc转换"
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
    
    has_pdftotext=false
    has_pandoc=false
    if command -v pdftotext >/dev/null 2>&1; then
        has_pdftotext=true
        log_info "pdftotext已安装"
    else
        log_warn "pdftotext未安装，将尝试使用Pandoc进行PDF文本提取"
    fi
    if command -v pandoc >/dev/null 2>&1; then
        has_pandoc=true
    fi
    if [[ "$has_pdftotext" == "false" && "$has_pandoc" == "false" ]]; then
        handle_error "缺少PDF文本提取工具(pdftotext或pandoc)，请至少安装一个"
        exit 1
    fi
    
    log_info "依赖检查完成"
}

# 检查LibreOffice是否已安装 (供其他模块调用)
check_libreoffice_installed() {
    if [[ "$HAS_LIBREOFFICE" == "true" ]]; then
        return 0
    fi
    # 尝试再次检查
    if command -v libreoffice >/dev/null 2>&1 || command -v soffice >/dev/null 2>&1; then
        HAS_LIBREOFFICE=true
        return 0
    fi
    # 不再直接报错退出，而是返回状态码，由调用者决定是否报错或使用降级方案
    return 1
}
