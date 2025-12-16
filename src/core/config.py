import json
import os
import shutil
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path=None):
        if config_path:
            self.config_file = Path(config_path)
            self.config_dir = self.config_file.parent
        else:
            self.config_dir = Path.home() / ".config" / "everything2md"
            self.config_file = self.config_dir / "config.json"
        
        self.config_data = {}
        self.load_config()

    def get_default_config(self):
        return {
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
                "max_output_file_size_mb": 50,
                "batch_processing": {
                    "enabled": True,
                    "max_parallel_jobs": 2,
                    "file_filters": ["docx", "pptx", "pdf", "txt"]
                }
            },
            "path_settings": {
                "last_input_path": "",
                "last_output_path": "",
                "soffice_path": "",
                "pandoc_path": ""
            },
            "ragflow_settings": {
                "api_base_url": "http://192.168.150.76:8081",
                "api_key": "ragflow-8DLY1LXzljiZ_WxirLd3q4NBgGrkR8Mt1ZgbfkN3zRw"
            }
        }

    def load_config(self):
        if not self.config_file.exists():
            self.config_data = self.get_default_config()
            self.save_config()
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
        except Exception:
            # If load fails, backup and reset
            if self.config_file.exists():
                shutil.copy(self.config_file, str(self.config_file) + ".bak")
            self.config_data = self.get_default_config()
            self.save_config()

    def save_config(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        # Flattened key access for compatibility
        if key == "log_level":
            return self.config_data.get("conversion_settings", {}).get("log_level", default)
        elif key == "output_format":
            return self.config_data.get("conversion_settings", {}).get("output_format", default)
        elif key == "max_output_file_size_mb":
            return self.config_data.get("conversion_settings", {}).get("max_output_file_size_mb", default)
        elif key == "batch_processing_enabled":
            val = self.config_data.get("conversion_settings", {}).get("batch_processing", {}).get("enabled", default)
            return str(val).lower()  # Keep consistent with shell script string return
        elif key == "max_parallel_jobs":
            return str(self.config_data.get("conversion_settings", {}).get("batch_processing", {}).get("max_parallel_jobs", default))
        elif key == "file_filters":
            filters = self.config_data.get("conversion_settings", {}).get("batch_processing", {}).get("file_filters", default)
            if isinstance(filters, list):
                return ",".join(filters)
            return filters
        elif key == "last_input_path":
            return self.config_data.get("path_settings", {}).get("last_input_path", default)
        elif key == "last_output_path":
            return self.config_data.get("path_settings", {}).get("last_output_path", default)
        elif key == "soffice_path":
            return self.config_data.get("path_settings", {}).get("soffice_path", default)
        elif key == "pandoc_path":
            return self.config_data.get("path_settings", {}).get("pandoc_path", default)
        elif key == "rag_api_base":
            return self.config_data.get("ragflow_settings", {}).get("api_base_url", default)
        elif key == "rag_api_key":
            return self.config_data.get("ragflow_settings", {}).get("api_key", default)
        return default

    def set(self, key, value):
        # Flattened key setter
        if "conversion_settings" not in self.config_data:
            self.config_data["conversion_settings"] = {}
        if "path_settings" not in self.config_data:
            self.config_data["path_settings"] = {}
        if "ragflow_settings" not in self.config_data:
            self.config_data["ragflow_settings"] = {}
        
        cs = self.config_data["conversion_settings"]
        
        if key == "log_level":
            cs["log_level"] = value
        elif key == "output_format":
            cs["output_format"] = value
        elif key == "batch_processing_enabled":
            if "batch_processing" not in cs: cs["batch_processing"] = {}
            # Handle boolean/string conversion if needed, but keeping it simple
            cs["batch_processing"]["enabled"] = value
        elif key == "max_parallel_jobs":
            if "batch_processing" not in cs: cs["batch_processing"] = {}
            cs["batch_processing"]["max_parallel_jobs"] = int(value) if str(value).isdigit() else 2
        elif key == "file_filters":
            if "batch_processing" not in cs: cs["batch_processing"] = {}
            # value should be list or comma separated string
            if isinstance(value, str):
                cs["batch_processing"]["file_filters"] = [x.strip() for x in value.split(",")]
            else:
                cs["batch_processing"]["file_filters"] = value
        elif key == "last_input_path":
            self.config_data["path_settings"]["last_input_path"] = value
        elif key == "last_output_path":
            self.config_data["path_settings"]["last_output_path"] = value
        elif key == "soffice_path":
            self.config_data["path_settings"]["soffice_path"] = value
        elif key == "pandoc_path":
            self.config_data["path_settings"]["pandoc_path"] = value
        elif key == "rag_api_base":
            self.config_data["ragflow_settings"]["api_base_url"] = value
        elif key == "rag_api_key":
            self.config_data["ragflow_settings"]["api_key"] = value
        
        self.save_config()
