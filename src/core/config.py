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
                "theme": "default",
            },
            "conversion_settings": {
                "log_level": "INFO",
                "output_format": "markdown",
                "max_output_file_size_mb": 20,
                "batch_processing": {
                    "enabled": True,
                    "max_parallel_jobs": 2,
                    "file_filters": ["docx", "pptx", "pdf", "txt"],
                },
            },
            "path_settings": {
                "last_input_path": "",
                "last_output_path": "",
                "soffice_path": "",
                "pandoc_path": "",
            },
            "ragflow_settings": {
                "api_base_url": "http://192.168.150.76:8081",
                "api_key": "ragflow-8DLY1LXzljiZ_WxirLd3q4NBgGrkR8Mt1ZgbfkN3zRw",
            },
            "image_recognition": {
                "enabled": False,
                "api_base": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-4-vision-preview",
                "max_concurrency": 2,
                "context_length": 500,
            },
            "structure_cleaning": {
                "enabled": False,
                "api_base": "https://api.openai.com/v1",
                "api_key": "",
                "model": "gpt-4",
            },
        }

    def load_config(self):
        if not self.config_file.exists():
            self.config_data = self.get_default_config()
            self.save_config()
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config_data = json.load(f)
        except Exception:
            # If load fails, backup and reset
            if self.config_file.exists():
                shutil.copy(self.config_file, str(self.config_file) + ".bak")
            self.config_data = self.get_default_config()
            self.save_config()

    def save_config(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=2, ensure_ascii=False)

    def _get_config_mapping(self):
        """
        Define the mapping between flat keys and nested config dictionary paths.
        Format: "flat_key": (("path", "to", "section"), "key_name")
        """
        return {
            # Conversion Settings
            "log_level": (("conversion_settings",), "log_level"),
            "output_format": (("conversion_settings",), "output_format"),
            "max_output_file_size_mb": (("conversion_settings",), "max_output_file_size_mb"),
            
            # Batch Processing
            "batch_processing_enabled": (("conversion_settings", "batch_processing"), "enabled"),
            "max_parallel_jobs": (("conversion_settings", "batch_processing"), "max_parallel_jobs"),
            "file_filters": (("conversion_settings", "batch_processing"), "file_filters"),
            
            # Path Settings
            "last_input_path": (("path_settings",), "last_input_path"),
            "last_output_path": (("path_settings",), "last_output_path"),
            "soffice_path": (("path_settings",), "soffice_path"),
            "pandoc_path": (("path_settings",), "pandoc_path"),
            
            # RAGFlow Settings
            "rag_api_base": (("ragflow_settings",), "api_base_url"),
            "rag_api_key": (("ragflow_settings",), "api_key"),
            
            # Image Recognition Settings
            "img_rec_enabled": (("image_recognition",), "enabled"),
            "img_rec_api_base": (("image_recognition",), "api_base"),
            "img_rec_api_key": (("image_recognition",), "api_key"),
            "img_rec_model": (("image_recognition",), "model"),
            "img_rec_concurrency": (("image_recognition",), "max_concurrency"),
            "img_rec_context_length": (("image_recognition",), "context_length"),
            
            # Structure Cleaning Settings
            "struct_clean_enabled": (("structure_cleaning",), "enabled"),
            "struct_clean_api_base": (("structure_cleaning",), "api_base"),
            "struct_clean_api_key": (("structure_cleaning",), "api_key"),
            "struct_clean_model": (("structure_cleaning",), "model"),
        }

    def get(self, key, default=None):
        mapping = self._get_config_mapping()
        if key not in mapping:
            return default
            
        path_tuple, field_name = mapping[key]
        
        # Navigate to the section
        current_data = self.config_data
        for section in path_tuple:
            current_data = current_data.get(section, {})
            
        value = current_data.get(field_name, default)
        
        # Type conversions for specific keys to maintain backward compatibility
        if key == "batch_processing_enabled":
            return str(value).lower()
        elif key == "max_parallel_jobs":
            return str(value)
        elif key == "file_filters":
            if isinstance(value, list):
                return ",".join(value)
            return value
            
        return value

    def set(self, key, value):
        mapping = self._get_config_mapping()
        if key not in mapping:
            # Optionally log warning or ignore
            return
            
        path_tuple, field_name = mapping[key]
        
        # Navigate and create sections if needed
        current_data = self.config_data
        for section in path_tuple:
            if section not in current_data:
                current_data[section] = {}
            current_data = current_data[section]
            
        # Type conversions before saving
        if key == "batch_processing_enabled":
            # Handle boolean/string conversion
            if isinstance(value, str):
                value = value.lower() == "true"
        elif key == "max_parallel_jobs":
            value = int(value) if str(value).isdigit() else 2
        elif key == "img_rec_concurrency":
             value = int(value) if str(value).isdigit() else 2
        elif key == "img_rec_context_length":
             value = int(value) if str(value).isdigit() else 500
        elif key == "file_filters":
            if isinstance(value, str):
                value = [x.strip() for x in value.split(",")]
                
        current_data[field_name] = value
        self.save_config()
