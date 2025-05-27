import unittest
import os
import json
import yaml
from ConfigManager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.config_path_json = 'test_config.json'
        self.config_path_yaml = 'test_config.yaml'
        self.config_data = {
            'module1': {'param1': 'value1', 'param2': 123},
            'module2': {'param3': True, 'param4': [1, 2, 3]}
        }

        # JSON dosyası oluştur
        with open(self.config_path_json, 'w') as f:
            json.dump(self.config_data, f, indent=4)

        # YAML dosyası oluştur
        with open(self.config_path_yaml, 'w') as f:
            yaml.dump(self.config_data, f, indent=4)

        self.config_manager_json = ConfigManager(self.config_path_json)
        self.config_manager_yaml = ConfigManager(self.config_path_yaml)

    def tearDown(self):
        os.remove(self.config_path_json)
        os.remove(self.config_path_yaml)

    def test_load_config(self):
        self.assertEqual(self.config_manager_json.config, self.config_data)
        self.assertEqual(self.config_manager_yaml.config, self.config_data)

    def test_get(self):
        self.assertEqual(self.config_manager_json.get('module1'), self.config_data['module1'])
        self.assertEqual(self.config_manager_yaml.get('module2'), self.config_data['module2'])
        self.assertEqual(self.config_manager_json.get('nonexistent_key'), None)
        self.assertEqual(self.config_manager_yaml.get('nonexistent_key', 'default_value'), 'default_value')

    def test_set(self):
        self.config_manager_json.set('new_key', 'new_value')
        self.assertEqual(self.config_manager_json.get('new_key'), 'new_value')
        self.config_manager_yaml.set('new_key', 'new_value')
        self.assertEqual(self.config_manager_yaml.get('new_key'), 'new_value')

    def test_save_config(self):
        self.config_manager_json.set('another_key', 'another_value')
        self.config_manager_json.save_config()
        with open(self.config_path_json, 'r') as f:
            updated_config = json.load(f)
        self.assertEqual(updated_config['another_key'], 'another_value')

        self.config_manager_yaml.set('another_key', 'another_value')
        self.config_manager_yaml.save_config()
        with open(self.config_path_yaml, 'r') as f:
            updated_config = yaml.safe_load(f)
        self.assertEqual(updated_config['another_key'], 'another_value')

    def test_register_and_get_module_config(self):
        module_name = 'module3'
        config_section = {'param5': 'value5', 'param6': 456}
        self.config_manager_json.register(module_name, config_section)
        self.assertEqual(self.config_manager_json.get_module_config(module_name), config_section)
        self.config_manager_yaml.register(module_name, config_section)
        self.assertEqual(self.config_manager_yaml.get_module_config(module_name), config_section)

if __name__ == '__main__':
    unittest.main()