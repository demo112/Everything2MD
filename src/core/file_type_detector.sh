#!/bin/bash

# 文件类型检测器
# 用于检测输入文件的类型并确定相应的处理流程

# 根据文件扩展名判断文件类型
# 参数:
#   $1 - 文件路径
# 返回值:
#   输出文件类型字符串
detect_file_type() {
    local file_path="$1"
    
    # 检查文件是否存在
    if [[ ! -f "$file_path" ]]; then
        echo "error"
        return 1
    fi
    
    # 获取文件扩展名并转换为小写
    local file_ext=$(echo "${file_path##*.}" | tr '[:upper:]' '[:lower:]')
    
    # 根据扩展名判断文件类型
    case "$file_ext" in
        doc|docx|ppt|pptx)
            echo "office"
            ;;
        pdf)
            echo "pdf"
            ;;
        md|markdown)
            echo "markdown"
            ;;
        txt)
            echo "text"
            ;;
        *)
            echo "unsupported"
            ;;
    esac
}