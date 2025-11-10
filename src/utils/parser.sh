#!/bin/bash

# 参数解析器
# 用于解析命令行参数

# 解析命令行参数
parse_args() {
    local verbose=false
    local batch_mode=false
    local input=""
    local output=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -b|--batch)
                batch_mode=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -*)
                echo "未知参数: $1"
                show_help
                exit 1
                ;;
            *)
                if [[ -z "$input" ]]; then
                    input="$1"
                elif [[ -z "$output" ]]; then
                    output="$1"
                else
                    echo "参数过多"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 返回解析结果
    echo "$verbose|$batch_mode|$input|$output"
}

# 显示帮助信息
show_help() {
    echo "Usage: $0 [-h] [-b] [-v] input [output]"
    echo ""
    echo "参数:"
    echo "  input          输入文件或目录路径"
    echo "  output         输出文件或目录路径（可选）"
    echo "  -h, --help     显示帮助信息"
    echo "  -b, --batch    批量转换模式"
    echo "  -v, --verbose  详细输出模式"
    echo ""
}