#!/bin/bash

# 配置管理系统模块

# 默认配置
CONFIG_LOG_LEVEL="INFO"
CONFIG_OUTPUT_FORMAT="markdown"
CONFIG_BATCH_PROCESSING_ENABLED="true"

# 加载配置文件
load_config() {
    local config_file="$1"
    
    # 检查配置文件是否存在
    if [[ ! -f "$config_file" ]]; then
        log_warn "配置文件不存在: $config_file"
        return 1
    fi
    
    # 读取配置文件
    while IFS='=' read -r key value; do
        # 跳过注释和空行
        [[ "$key" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$key" ]] && continue
        
        # 去除值的首尾空格
        value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # 根据键设置配置变量
        case "$key" in
            "log_level") CONFIG_LOG_LEVEL="$value" ;;
            "output_format") CONFIG_OUTPUT_FORMAT="$value" ;;
            "batch_processing_enabled") CONFIG_BATCH_PROCESSING_ENABLED="$value" ;;
            *) log_warn "未知配置项: $key" ;;
        esac
    done < "$config_file"
    
    log_info "配置文件加载成功: $config_file"
}

# 获取配置值
get_config() {
    local key="$1"
    
    case "$key" in
        "log_level") echo "$CONFIG_LOG_LEVEL" ;;
        "output_format") echo "$CONFIG_OUTPUT_FORMAT" ;;
        "batch_processing_enabled") echo "$CONFIG_BATCH_PROCESSING_ENABLED" ;;
        *) 
            log_warn "未知配置项: $key"
            return 1
            ;;
    esac
}

# 设置配置值
set_config() {
    local key="$1"
    local value="$2"
    
    case "$key" in
        "log_level") CONFIG_LOG_LEVEL="$value" ;;
        "output_format") CONFIG_OUTPUT_FORMAT="$value" ;;
        "batch_processing_enabled") CONFIG_BATCH_PROCESSING_ENABLED="$value" ;;
        *) 
            log_warn "未知配置项: $key"
            return 1
            ;;
    esac
    
    log_debug "配置项已更新: $key=$value"
}