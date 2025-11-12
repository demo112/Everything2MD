#!/usr/bin/env python3
"""
配置迁移工具 - 将INI格式配置迁移到JSON格式
"""

import os
import json
import configparser
from pathlib import Path

def get_default_config_path():
    """获取平台默认配置路径"""
    home = Path.home()
    
    if os.name == 'posix':  # macOS/Linux
        if 'Darwin' in os.uname().sysname:  # macOS
            config_dir = home / "Library" / "Application Support" / "Everything2MD"
        else:  # Linux
            config_dir = home / ".config" / "everything2md"
    else:  # Windows
        config_dir = Path(os.environ.get('APPDATA', '')) / "Everything2MD"
    
    return config_dir

def migrate_ini_to_json(ini_path, json_path):
    """将INI配置文件迁移到JSON格式"""
    
    # 创建配置目录
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 默认配置结构
    default_config = {
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
                "enabled": True,
                "max_parallel_jobs": 2,
                "file_filters": ["docx", "pptx", "pdf", "txt"]
            }
        },
        "path_settings": {
            "last_input_path": "",
            "last_output_path": ""
        }
    }
    
    # 如果INI文件存在，则迁移配置
    if ini_path.exists():
        print(f"发现INI配置文件: {ini_path}")
        
        config_parser = configparser.ConfigParser()
        config_parser.read(ini_path)
        
        # 迁移基本配置
        if config_parser.has_section('general'):
            if config_parser.has_option('general', 'log_level'):
                default_config['conversion_settings']['log_level'] = config_parser.get('general', 'log_level')
            
            if config_parser.has_option('general', 'output_format'):
                default_config['conversion_settings']['output_format'] = config_parser.get('general', 'output_format')
        
        # 迁移批量处理配置
        if config_parser.has_section('batch'):
            if config_parser.has_option('batch', 'enabled'):
                default_config['conversion_settings']['batch_processing']['enabled'] = config_parser.getboolean('batch', 'enabled')
        
        print(f"成功迁移配置从: {ini_path}")
        
        # 备份原文件
        backup_path = ini_path.with_suffix('.ini.backup')
        import shutil
        shutil.copy2(ini_path, backup_path)
        print(f"原配置文件已备份到: {backup_path}")
    else:
        print("未发现现有INI配置文件，创建新的JSON配置")
    
    # 写入JSON配置文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    print(f"JSON配置文件已创建: {json_path}")
    return True

def main():
    """主函数"""
    config_dir = get_default_config_path()
    ini_path = config_dir / "config.ini"
    json_path = config_dir / "config.json"
    
    print("开始配置格式迁移...")
    print(f"配置目录: {config_dir}")
    print(f"INI文件: {ini_path}")
    print(f"JSON文件: {json_path}")
    
    try:
        success = migrate_ini_to_json(ini_path, json_path)
        if success:
            print("配置迁移完成!")
            return 0
        else:
            print("配置迁移失败!")
            return 1
    except Exception as e:
        print(f"迁移过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    exit(main())