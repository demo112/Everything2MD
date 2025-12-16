#!/bin/bash

# Configuration management module

# Load dependency modules
source "$(dirname "${BASH_SOURCE[0]}")/fixed_logger.sh"

# Default configuration paths
CONFIG_DIR="$HOME/.config/everything2md"
CONFIG_FILE="$CONFIG_DIR/config.json"

# Default configuration values
CONFIG_LOG_LEVEL="INFO"
CONFIG_OUTPUT_FORMAT="markdown"
CONFIG_BATCH_PROCESSING_ENABLED="true"
CONFIG_MAX_PARALLEL_JOBS="2"
CONFIG_FILE_FILTERS="docx,pptx,pdf,txt"
CONFIG_LAST_INPUT_PATH=""
CONFIG_LAST_OUTPUT_PATH=""

# Load configuration from file
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        # Read configuration values from file
        CONFIG_LOG_LEVEL=$(jq -r '.log_level // "INFO"' "$CONFIG_FILE")
        CONFIG_OUTPUT_FORMAT=$(jq -r '.output_format // "markdown"' "$CONFIG_FILE")
        CONFIG_BATCH_PROCESSING_ENABLED=$(jq -r '.conversion_settings.batch_processing.enabled // "true"' "$CONFIG_FILE")
        CONFIG_MAX_PARALLEL_JOBS=$(jq -r '.conversion_settings.batch_processing.max_parallel_jobs // "2"' "$CONFIG_FILE")
        CONFIG_FILE_FILTERS=$(jq -r '.conversion_settings.batch_processing.file_filters | join(",") // "docx,pptx,pdf,txt"' "$CONFIG_FILE")
        CONFIG_LAST_INPUT_PATH=$(jq -r '.last_input_path // ""' "$CONFIG_FILE")
        CONFIG_LAST_OUTPUT_PATH=$(jq -r '.last_output_path // ""' "$CONFIG_FILE")
        
        log_info "Configuration file loaded successfully: $CONFIG_FILE"
    else
        log_warn "Configuration file not found, using default values"
    fi
}

# Save configuration to file
save_config() {
    # Create config directory if it doesn't exist
    mkdir -p "$CONFIG_DIR"
    
    # Create backup of existing config file
    if [[ -f "$CONFIG_FILE" ]]; then
        backup_config
    fi
    
    # Create JSON configuration
    local config_json=$(jq -n \
        --arg log_level "$CONFIG_LOG_LEVEL" \
        --arg output_format "$CONFIG_OUTPUT_FORMAT" \
        --arg batch_enabled "$CONFIG_BATCH_PROCESSING_ENABLED" \
        --arg max_jobs "$CONFIG_MAX_PARALLEL_JOBS" \
        --arg file_filters "$CONFIG_FILE_FILTERS" \
        --arg input_path "$CONFIG_LAST_INPUT_PATH" \
        --arg output_path "$CONFIG_LAST_OUTPUT_PATH" \
        '{
            log_level: $log_level,
            output_format: $output_format,
            conversion_settings: {
                batch_processing: {
                    enabled: $batch_enabled | test("true"),
                    max_parallel_jobs: ($max_jobs | tonumber),
                    file_filters: ($file_filters | split(",") | map(select(length > 0)))
                }
            },
            last_input_path: $input_path,
            last_output_path: $output_path
        }')
    
    # Save configuration to file
    echo "$config_json" > "$CONFIG_FILE"
    
    if [[ $? -eq 0 ]]; then
        log_info "Configuration saved successfully: $CONFIG_FILE"
        return 0
    else
        log_error "Failed to save configuration: $CONFIG_FILE"
        return 1
    fi
}

# Get configuration value
get_config() {
    local key="$1"
    
    case "$key" in
        "log_level")
            echo "$CONFIG_LOG_LEVEL"
            ;;
        "output_format")
            echo "$CONFIG_OUTPUT_FORMAT"
            ;;
        "batch_processing_enabled")
            echo "$CONFIG_BATCH_PROCESSING_ENABLED"
            ;;
        "max_parallel_jobs")
            echo "$CONFIG_MAX_PARALLEL_JOBS"
            ;;
        "file_filters")
            echo "$CONFIG_FILE_FILTERS"
            ;;
        "last_input_path")
            echo "$CONFIG_LAST_INPUT_PATH"
            ;;
        "last_output_path")
            echo "$CONFIG_LAST_OUTPUT_PATH"
            ;;
        *)
            log_error "Unknown configuration key: $key"
            return 1
            ;;
    esac
}

# Set configuration value
set_config() {
    local key="$1"
    local value="$2"
    
    # Validate configuration value
    if ! validate_config "$key" "$value"; then
        return 1
    fi
    
    case "$key" in
        "log_level")
            CONFIG_LOG_LEVEL="$value"
            ;;
        "output_format")
            CONFIG_OUTPUT_FORMAT="$value"
            ;;
        "batch_processing_enabled")
            CONFIG_BATCH_PROCESSING_ENABLED="$value"
            ;;
        "max_parallel_jobs")
            CONFIG_MAX_PARALLEL_JOBS="$value"
            ;;
        "file_filters")
            CONFIG_FILE_FILTERS="$value"
            ;;
        "last_input_path")
            CONFIG_LAST_INPUT_PATH="$value"
            ;;
        "last_output_path")
            CONFIG_LAST_OUTPUT_PATH="$value"
            ;;
        *)
            log_error "Unknown configuration key: $key"
            return 1
            ;;
    esac
    
    log_info "Configuration value set: $key = $value"
    return 0
}

# Validate configuration value
validate_config() {
    local key="$1"
    local value="$2"
    
    case "$key" in
        "log_level")
            # Validate log level (support both WARN and WARNING formats)
            if [[ ! "$value" =~ ^(DEBUG|INFO|WARN|WARNING|ERROR)$ ]]; then
                log_error "Invalid log level: $value, valid values are: DEBUG, INFO, WARN, WARNING, ERROR"
                return 1
            fi
            ;;
        "output_format")
            # Validate output format
            if [[ ! "$value" =~ ^(markdown|html|txt)$ ]]; then
                log_error "Invalid output format: $value, valid values are: markdown, html, txt"
                return 1
            fi
            ;;
        "batch_processing_enabled")
            # Validate boolean value
            if [[ ! "$value" =~ ^(true|false)$ ]]; then
                log_error "Invalid boolean value: $value, valid values are: true, false"
                return 1
            fi
            ;;
        "max_parallel_jobs")
            # Validate parallel job count
            if [[ ! "$value" =~ ^[0-9]+$ ]] || [[ "$value" -lt 1 ]] || [[ "$value" -gt 16 ]]; then
                log_error "Invalid parallel job count: $value, valid values are: 1-16"
                return 1
            fi
            ;;
        "file_filters")
            # Validate file filters
            if [[ -z "$value" ]]; then
                log_error "File filters cannot be empty"
                return 1
            fi
            # Validate file extension format
            if [[ "$value" =~ [^a-zA-Z0-9,.] ]]; then
                log_error "File filters contain invalid characters: $value"
                return 1
            fi
            ;;
        "last_input_path")
            # Validate input path (allow empty values)
            CONFIG_LAST_INPUT_PATH="$value"
            ;;
        "last_output_path")
            # Validate output path (allow empty values)
            CONFIG_LAST_OUTPUT_PATH="$value"
            ;;
    esac
    
    return 0
}

# Backup configuration file
backup_config() {
    local config_file="${1:-$CONFIG_FILE}"
    local backup_dir="$CONFIG_DIR/backup"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/config_$timestamp.json"
    
    # Create backup directory
    mkdir -p "$backup_dir"
    
    # Backup configuration file
    if [[ -f "$config_file" ]]; then
        cp "$config_file" "$backup_file"
        if [[ $? -eq 0 ]]; then
            log_info "Configuration file backed up: $backup_file"
        else
            log_error "Failed to backup configuration file: $backup_file"
            return 1
        fi
    fi
    
    return 0
}

# List backup files
list_backups() {
    local backup_dir="$CONFIG_DIR/backup"
    
    if [[ -d "$backup_dir" ]]; then
        ls -1 "$backup_dir" | grep "^config_.*\.json$"
    else
        log_warn "Backup directory does not exist: $backup_dir"
    fi
}

# Restore configuration
restore_config() {
    local backup_file="$1"
    local backup_dir="$CONFIG_DIR/backup"
    local full_backup_path="$backup_dir/$backup_file"
    
    if [[ ! -f "$full_backup_path" ]]; then
        log_error "Backup file does not exist: $full_backup_path"
        return 1
    fi
    
    # Backup current configuration before restoring
    backup_config "$CONFIG_FILE"
    
    # Restore configuration
    cp "$full_backup_path" "$CONFIG_FILE"
    if [[ $? -eq 0 ]]; then
        log_info "Configuration restored from: $full_backup_path"
        # Reload configuration
        load_config
        return 0
    else
        log_error "Failed to restore configuration from: $full_backup_path"
        return 1
    fi
}

# Validate current configuration
validate_current_config() {
    local errors=0
    
    validate_config "log_level" "$CONFIG_LOG_LEVEL" || errors=$((errors + 1))
    validate_config "output_format" "$CONFIG_OUTPUT_FORMAT" || errors=$((errors + 1))
    validate_config "batch_processing_enabled" "$CONFIG_BATCH_PROCESSING_ENABLED" || errors=$((errors + 1))
    validate_config "max_parallel_jobs" "$CONFIG_MAX_PARALLEL_JOBS" || errors=$((errors + 1))
    validate_config "file_filters" "$CONFIG_FILE_FILTERS" || errors=$((errors + 1))
    # Path configuration items don't need validation as they can be empty
    # validate_config "last_input_path" "$CONFIG_LAST_INPUT_PATH" || errors=$((errors + 1))
    # validate_config "last_output_path" "$CONFIG_LAST_OUTPUT_PATH" || errors=$((errors + 1))
    
    if [[ $errors -eq 0 ]]; then
        log_info "Configuration validation passed"
        return 0
    else
        log_error "Configuration validation failed, found $errors errors"
        return 1
    fi
}

# Main function
main() {
    # Load configuration
    load_config
    
    # Parse command line arguments
    local action="$1"
    local key="$2"
    local value="$3"
    
    case "$action" in
        "get_config")
            if [[ -z "$key" ]]; then
                echo "Usage: $0 get_config <key>"
                return 1
            fi
            get_config "$key"
            ;;
        "set_config")
            if [[ -z "$key" ]] || [[ -z "$value" ]]; then
                echo "Usage: $0 set_config <key> <value>"
                return 1
            fi
            set_config "$key" "$value"
            ;;
        "backup_config")
            backup_config
            ;;
        "list_backups")
            list_backups
            ;;
        "restore_config")
            if [[ -z "$key" ]]; then
                echo "Usage: $0 restore_config <backup_file>"
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
            echo "Usage: $0 <action> [args...]"
            echo "Available actions:"
            echo "  get_config <key> - Get configuration value"
            echo "  set_config <key> <value> - Set configuration value and save"
            echo "  backup_config - Backup current configuration"
            echo "  list_backups - List backup files"
            echo "  restore_config <backup_file> - Restore configuration"
            echo "  validate_config - Validate current configuration"
            echo "  save_config - Save current configuration to file"
            return 1
            ;;
    esac
}

# If script is executed directly, call main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi