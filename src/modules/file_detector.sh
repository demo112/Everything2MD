#!/bin/bash

# 文件类型检测模块

# 检测文件类型
detect_file_type() {
    local file_path="$1"
    
    # 检查文件是否存在
    if [[ ! -f "$file_path" ]]; then
        echo "error"
        return
    fi
    
    # 获取文件扩展名
    local extension="${file_path##*.}"
    extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')
    
    # 根据扩展名判断文件类型
    case "$extension" in
        # Office文档
        doc|docx|xls|xlsx|ppt)
            echo "office"
            ;;
        # PowerPoint文档
        pptx)
            echo "pptx"
            ;;
        # 文本文件
        txt|md|markdown)
            echo "text"
            ;;
        # 其他文件类型
        *)
            # 尝试使用file命令检测
            if command -v file >/dev/null 2>&1; then
                local mime_type=$(file --mime-type -b "$file_path")
                case "$mime_type" in
                    text/*)
                        echo "text"
                        ;;
                    application/msword|application/vnd.ms-word*|application/vnd.openxmlformats-officedocument*)
                        echo "office"
                        ;;
                    application/vnd.ms-powerpoint*|application/vnd.openxmlformats-officedocument.presentationml*)
                        echo "pptx"
                        ;;
                    *)
                        echo "unknown"
                        ;;
                esac
            else
                echo "unknown"
            fi
            ;;
    esac
}