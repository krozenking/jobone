import json
import yaml
import os

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        _, ext = os.path.splitext(self.config_path)
        try:
            with open(self.config_path, 'r') as f:
                if ext in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                elif ext == '.json':
                    return json.load(f)
                else:
                    raise ValueError("Unsupported config format")
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value

    def save_config(self):
        _, ext = os.path.splitext(self.config_path)
        try:
            with open(self.config_path, 'w') as f:
                if ext in ['.yaml', '.yml']:
                    yaml.dump(self.config, f, indent=4)
                elif ext == '.json':
                    json.dump(self.config, f, indent=4)
                else:
                    raise ValueError("Unsupported config format")
        except Exception as e:
            print(f"Error saving config: {e}")

    def register(self, module_name, config_section):
        if module_name not in self.config:
            self.config[module_name] = config_section

    def get_module_config(self, module_name):
        return self.config.get(module_name, {})