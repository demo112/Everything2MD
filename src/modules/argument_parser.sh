#!/bin/bash

# 参数解析器模块

# 默认配置
INPUT_PATH=""
OUTPUT_PATH=""
BATCH_MODE="false"
CONFIG_FILE=""
LOG_LEVEL="INFO"

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--input)
                INPUT_PATH="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_PATH="$2"
                shift 2
                ;;
            -b|--batch)
                BATCH_MODE="true"
                shift
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            -l|--log-level)
                LOG_LEVEL="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 验证必要参数
    if [[ -z "$INPUT_PATH" ]]; then
        echo "错误: 必须指定输入路径"
        show_help
        exit 1
    fi
    
    # 如果没有指定输出路径，使用默认值
    if [[ -z "$OUTPUT_PATH" ]]; then
        if [[ "$BATCH_MODE" == "true" ]]; then
            OUTPUT_PATH="$(dirname "$INPUT_PATH")/output"
        else
            OUTPUT_PATH="$(dirname "$INPUT_PATH")/$(basename "$INPUT_PATH" | cut -d. -f1).md"
        fi
    fi
    
    # 如果指定了配置文件，加载配置
    if [[ -n "$CONFIG_FILE" ]]; then
        load_config "$CONFIG_FILE"
    fi
}

# 显示帮助信息
show_help() {
    echo "Everything2MD - 将各种文档格式转换为Markdown"
    echo
    echo "用法:"
    echo "  ./main.sh [选项]"
    echo
    echo "选项:"
    echo "  -i, --input PATH     输入文件或目录路径"
    echo "  -o, --output PATH    输出文件或目录路径"
    echo "  -b, --batch          批量处理模式"
    echo "  -c, --config FILE    配置文件路径"
    echo "  -l, --log-level LEVEL 日志级别 (DEBUG, INFO, WARN, ERROR)"
    echo "  -h, --help           显示此帮助信息"
    echo
}

# 加载配置文件
load_config() {
    local config_file="$1"
    
    if [[ ! -f "$config_file" ]]; then
        echo "警告: 配置文件不存在: $config_file"
        return
    fi
    
    # 读取配置文件
    while IFS='=' read -r key value; do
        # 跳过注释和空行
        [[ "$key" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$key" ]] && continue
        
        # 去除值的首尾空格
        value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # 根据键设置变量
        case "$key" in
            "log_level") LOG_LEVEL="$value" ;;
            *) echo "警告: 未知配置项: $key" ;;
        esac
    done < "$config_file"
}