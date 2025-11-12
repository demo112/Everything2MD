#!/bin/bash

# 配置管理系统模块

# 加载依赖模块
source "$(dirname "${BASH_SOURCE[0]}")/logger.sh"

# 默认配置路径
CONFIG_DIR="$HOME/.config/everything2md"
CONFIG_FILE="$CONFIG_DIR/config.json"

# 默认配置值
CONFIG_LOG_LEVEL="INFO"
CONFIG_OUTPUT_FORMAT="markdown"
CONFIG_BATCH_PROCESSING_ENABLED="true"
CONFIG_MAX_PARALLEL_JOBS="2"
CONFIG_FILE_FILTERS="docx,pptx,pdf,txt"
CONFIG_LAST_INPUT_PATH=""
CONFIG_LAST_OUTPUT_PATH=""

# 加载配置文件
load_config() {
    local config_file="${1:-$CONFIG_FILE}"
    
    # 检查配置文件是否存在
    if [[ ! -f "$config_file" ]]; then
        log_warn "配置文件不存在: $config_file"
        # 创建默认配置
        create_default_config "$config_file"
        return 0
    fi
    
    # 检查文件格式（INI或JSON）
    if [[ "$config_file" == *.json ]]; then
        load_json_config "$config_file"
    else
        load_ini_config "$config_file"
    fi
    
    log_info "配置文件加载成功: $config_file"
}

# 加载JSON格式配置
load_json_config() {
    local config_file="$1"
    
    if ! command -v jq &> /dev/null; then
        log_error "jq命令未找到，无法解析JSON配置"
        return 1
    fi
    
    # 检查配置文件是否为空
    if [[ ! -s "$config_file" ]]; then
        log_warn "配置文件为空，创建默认配置"
        create_default_config "$config_file"
        return 0
    fi
    
    # 使用jq解析JSON配置
    CONFIG_LOG_LEVEL=$(jq -r '.conversion_settings.log_level // "INFO"' "$config_file" 2>/dev/null)
    CONFIG_OUTPUT_FORMAT=$(jq -r '.conversion_settings.output_format // "markdown"' "$config_file" 2>/dev/null)
    CONFIG_BATCH_PROCESSING_ENABLED=$(jq -r '.conversion_settings.batch_processing.enabled // "true"' "$config_file" 2>/dev/null)
    CONFIG_MAX_PARALLEL_JOBS=$(jq -r '.conversion_settings.batch_processing.max_parallel_jobs // "2"' "$config_file" 2>/dev/null)
    CONFIG_FILE_FILTERS=$(jq -r '.conversion_settings.batch_processing.file_filters // ["docx","pptx","pdf","txt"] | join(",")' "$config_file" 2>/dev/null)
}

# 加载INI格式配置（向后兼容）
load_ini_config() {
    local config_file="$1"
    
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
            "max_parallel_jobs") CONFIG_MAX_PARALLEL_JOBS="$value" ;;
            "file_filters") CONFIG_FILE_FILTERS="$value" ;;
            *) log_warn "未知配置项: $key" ;;
        esac
    done < "$config_file"
}

# 创建默认配置
create_default_config() {
    local config_file="$1"
    local config_dir=$(dirname "$config_file")
    
    # 创建配置目录
    mkdir -p "$config_dir"
    
    # 创建默认JSON配置
    cat > "$config_file" << EOF
{
  "version": "1.0",
  "gui_settings": {
    "window_width": 800,
    "window_height": 600,
    "window_x": 100,
    "window_y": 100,
    "theme": "default"
  },
  "conversion_settings": {
    "log_level": "INFO",
    "output_format": "markdown",
    "batch_processing": {
      "enabled": true,
      "max_parallel_jobs": 2,
      "file_filters": ["docx", "pptx", "pdf", "txt"]
    }
  },
  "path_settings": {
    "last_input_path": "",
    "last_output_path": ""
  }
}
EOF
    
    log_info "已创建默认配置文件: $config_file"
}

# 获取配置值
get_config() {
    local key="$1"
    
    case "$key" in
        "log_level") echo "$CONFIG_LOG_LEVEL" ;;
        "output_format") echo "$CONFIG_OUTPUT_FORMAT" ;;
        "batch_processing_enabled") echo "$CONFIG_BATCH_PROCESSING_ENABLED" ;;
        "max_parallel_jobs") echo "$CONFIG_MAX_PARALLEL_JOBS" ;;
        "file_filters") echo "$CONFIG_FILE_FILTERS" ;;
        "last_input_path") echo "$CONFIG_LAST_INPUT_PATH" ;;
        "last_output_path") echo "$CONFIG_LAST_OUTPUT_PATH" ;;
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
    
    # 验证配置值
    if ! validate_config "$key" "$value"; then
        log_error "配置值验证失败: $key=$value"
        return 1
    fi
    
    case "$key" in
        "log_level") CONFIG_LOG_LEVEL="$value" ;;
        "output_format") CONFIG_OUTPUT_FORMAT="$value" ;;
        "batch_processing_enabled") CONFIG_BATCH_PROCESSING_ENABLED="$value" ;;
        "max_parallel_jobs") CONFIG_MAX_PARALLEL_JOBS="$value" ;;
        "file_filters") CONFIG_FILE_FILTERS="$value" ;;
        "last_input_path") CONFIG_LAST_INPUT_PATH="$value" ;;
        "last_output_path") CONFIG_LAST_OUTPUT_PATH="$value" ;;
        *) 
            log_warn "未知配置项: $key"
            return 1
            ;;
    esac
    
    log_debug "配置项已更新: $key=$value"
}

# 验证配置值
validate_config() {
    local key="$1"
    local value="$2"
    
    case "$key" in
        "log_level")
            # 验证日志级别（支持WARN和WARNING两种格式）
            if [[ ! "$value" =~ ^(DEBUG|INFO|WARN|WARNING|ERROR)$ ]]; then
                log_error "无效的日志级别: $value，有效值为: DEBUG, INFO, WARN, WARNING, ERROR"
                return 1
            fi
            ;;
        "output_format")
            # 验证输出格式
            if [[ ! "$value" =~ ^(markdown|html|txt)$ ]]; then
                log_error "无效的输出格式: $value，有效值为: markdown, html, txt"
                return 1
            fi
            ;;
        "batch_processing_enabled")
            # 验证布尔值
            if [[ ! "$value" =~ ^(true|false)$ ]]; then
                log_error "无效的布尔值: $value，有效值为: true, false"
                return 1
            fi
            ;;
        "max_parallel_jobs")
            # 验证并行任务数
            if [[ ! "$value" =~ ^[0-9]+$ ]] || [[ "$value" -lt 1 ]] || [[ "$value" -gt 16 ]]; then
                log_error "无效的并行任务数: $value，有效值为: 1-16"
                return 1
            fi
            ;;
        "file_filters")
            # 验证文件过滤器
            if [[ -z "$value" ]]; then
                log_error "文件过滤器不能为空"
                return 1
            fi
            # 验证文件扩展名格式
            if [[ "$value" =~ [^a-zA-Z0-9,.] ]]; then
                log_error "文件过滤器包含无效字符: $value"
                return 1
            fi
            ;;
        "last_input_path")
            # 验证输入路径（允许空值）
            CONFIG_LAST_INPUT_PATH="$value"
            ;;
        "last_output_path")
            # 验证输出路径（允许空值）
            CONFIG_LAST_OUTPUT_PATH="$value"
            ;;
    esac
    
    return 0
}

# 备份配置文件
backup_config() {
    local config_file="${1:-$CONFIG_FILE}"
    local backup_dir="$CONFIG_DIR/backup"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/config_$timestamp.json"
    
    # 创建备份目录
    mkdir -p "$backup_dir"
    
    # 备份配置文件
    if [[ -f "$config_file" ]]; then
        cp "$config_file" "$backup_file"
        if [[ $? -eq 0 ]]; then
            log_info "配置文件已备份: $backup_file"
            return 0
        else
            log_error "配置文件备份失败"
            return 1
        fi
    else
        log_warn "配置文件不存在，无需备份"
        return 0
    fi
}

# 恢复配置文件
restore_config() {
    local backup_file="$1"
    local config_file="${2:-$CONFIG_FILE}"
    
    if [[ ! -f "$backup_file" ]]; then
        log_error "备份文件不存在: $backup_file"
        return 1
    fi
    
    # 验证备份文件格式
    if ! jq . "$backup_file" >/dev/null 2>&1; then
        log_error "备份文件格式无效: $backup_file"
        return 1
    fi
    
    # 恢复配置文件
    cp "$backup_file" "$config_file"
    if [[ $? -eq 0 ]]; then
        log_info "配置文件已恢复: $config_file"
        return 0
    else
        log_error "配置文件恢复失败"
        return 1
    fi
}

# 列出备份文件
list_backups() {
    local backup_dir="$CONFIG_DIR/backup"
    
    if [[ ! -d "$backup_dir" ]]; then
        echo "暂无备份文件"
        return 0
    fi
    
    echo "可用的备份文件:"
    find "$backup_dir" -name "config_*.json" -type f | sort -r | head -10
}

# 验证当前配置
validate_current_config() {
    local errors=0
    
    # 验证所有配置项
    validate_config "log_level" "$CONFIG_LOG_LEVEL" || errors=$((errors + 1))
    validate_config "output_format" "$CONFIG_OUTPUT_FORMAT" || errors=$((errors + 1))
    validate_config "batch_processing_enabled" "$CONFIG_BATCH_PROCESSING_ENABLED" || errors=$((errors + 1))
    validate_config "max_parallel_jobs" "$CONFIG_MAX_PARALLEL_JOBS" || errors=$((errors + 1))
    validate_config "file_filters" "$CONFIG_FILE_FILTERS" || errors=$((errors + 1))
    # 路径配置项不需要验证，因为它们可以为空
    # validate_config "last_input_path" "$CONFIG_LAST_INPUT_PATH" || errors=$((errors + 1))
    # validate_config "last_output_path" "$CONFIG_LAST_OUTPUT_PATH" || errors=$((errors + 1))
    
    if [[ $errors -eq 0 ]]; then
        log_info "配置验证通过"
        return 0
    else
        log_error "配置验证失败，发现 $errors 个错误"
        return 1
    fi
}

# 保存配置到文件
save_config() {
    local config_file="${1:-$CONFIG_FILE}"
    
    if ! command -v jq &> /dev/null; then
        log_error "jq命令未找到，无法保存JSON配置"
        return 1
    fi
    
    # 验证当前配置
    if ! validate_current_config; then
        log_error "配置验证失败，无法保存"
        return 1
    fi
    
    # 备份当前配置
    if ! backup_config "$config_file"; then
        log_warn "配置备份失败，继续保存操作"
    fi
    
    # 创建配置目录
    mkdir -p "$(dirname "$config_file")"
    
    # 使用jq直接构建JSON配置
    jq -n --arg log_level "$CONFIG_LOG_LEVEL" \
           --arg output_format "$CONFIG_OUTPUT_FORMAT" \
           --arg batch_enabled "$CONFIG_BATCH_PROCESSING_ENABLED" \
           --arg max_jobs "$CONFIG_MAX_PARALLEL_JOBS" \
           --arg file_filters "$CONFIG_FILE_FILTERS" \
           --arg last_input_path "$CONFIG_LAST_INPUT_PATH" \
           --arg last_output_path "$CONFIG_LAST_OUTPUT_PATH" \
           '{
             "version": "1.0",
             "gui_settings": {
               "window_width": 800,
               "window_height": 600,
               "window_x": 100,
               "window_y": 100,
               "theme": "default"
             },
             "conversion_settings": {
               "log_level": $log_level,
               "output_format": $output_format,
               "batch_processing": {
                 "enabled": ($batch_enabled == "true"),
                 "max_parallel_jobs": ($max_jobs | tonumber),
                 "file_filters": ($file_filters | split(",") | map(select(. != "")))
               }
             },
             "path_settings": {
               "last_input_path": $last_input_path,
               "last_output_path": $last_output_path
             }
           }' > "$config_file"
    
    if [[ $? -eq 0 ]]; then
        log_info "配置已保存到: $config_file"
        return 0
    else
        log_error "配置保存失败"
        return 1
    fi
}

# 主函数 - 处理命令行参数
main() {
    local action="$1"
    local key="$2"
    local value="$3"
    
    # 加载配置
    load_config
    
    case "$action" in
        "get_config")
            if [[ -z "$key" ]]; then
                echo "用法: $0 get_config <key>"
                echo "可用配置项: log_level, output_format, batch_processing_enabled, max_parallel_jobs, file_filters, last_input_path, last_output_path"
                return 1
            fi
            get_config "$key"
            ;;
        "set_config")
            if [[ -z "$key" ]] || [[ -z "$value" ]]; then
                echo "用法: $0 set_config <key> <value>"
                echo "可用配置项: log_level, output_format, batch_processing_enabled, max_parallel_jobs, file_filters, last_input_path, last_output_path"
                return 1
            fi
            set_config "$key" "$value"
            save_config
            ;;
        "backup_config")
            backup_config
            ;;
        "list_backups")
            list_backups
            ;;
        "restore_config")
            if [[ -z "$key" ]]; then
                echo "用法: $0 restore_config <backup_file>"
                return 1
            fi
            restore_config "$key"
            ;;
        "validate_config")
            validate_current_config
            ;;
        "save_config")
            save_config
            ;;
        *)
            echo "用法: $0 <action> [args...]"
            echo "可用操作:"
            echo "  get_config <key> - 获取配置值"
            echo "  set_config <key> <value> - 设置配置值并保存"
            echo "  backup_config - 备份当前配置"
            echo "  list_backups - 列出备份文件"
            echo "  restore_config <backup_file> - 恢复配置"
            echo "  validate_config - 验证当前配置"
            echo "  save_config - 保存当前配置到文件"
            return 1
            ;;
    esac
}

# 如果脚本被直接执行，则调用主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi