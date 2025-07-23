import unittest
import os
import tempfile
from utils.config import Config
from utils.logger import Logger

class TestConfig(unittest.TestCase):
    """配置工具类单元测试"""
    temp_config_path = None

    @classmethod
    def setUpClass(cls):
        """测试前准备，创建临时配置文件"""
        # 创建临时配置文件
        cls.temp_config_path = os.path.join(tempfile.gettempdir(), '.env.toml')
        with open(cls.temp_config_path, 'w', encoding='utf-8') as f:
            f.write('''[api]
stock_data_url = "https://test-api.example.com"
api_key = "test_key"

[model]
epochs = 10
batch_size = 16
''')

        # 重置配置状态
        Config._loaded = False
        Config._config = {}

    @classmethod
    def tearDownClass(cls):
        """测试后清理，删除临时配置文件"""
        if os.path.exists(cls.temp_config_path):
            os.remove(cls.temp_config_path)

    def test_load_config(self):
        """测试加载配置文件"""
        # 使用临时配置文件
        Config.load_config(self.temp_config_path)
        self.assertTrue(Config._loaded)
        self.assertEqual(Config.get('api.stock_data_url'), 'https://test-api.example.com')

    def test_get_config_value(self):
        """测试获取配置值"""
        Config.load_config(self.temp_config_path)
        # 测试存在的配置
        self.assertEqual(Config.get('model.epochs'), 10)
        self.assertEqual(Config.get('model.batch_size'), 16)
        # 测试不存在的配置
        self.assertEqual(Config.get('non.existent.key'), None)
        self.assertEqual(Config.get('non.existent.key', 'default'), 'default')

    def test_get_section(self):
        """测试获取配置节"""
        Config.load_config(self.temp_config_path)
        api_section = Config.get_section('api')
        self.assertEqual(len(api_section), 2)
        self.assertEqual(api_section['api_key'], 'test_key')

    def test_config_not_found(self):
        """测试配置文件不存在的情况"""
        # 重置配置
        Config._loaded = False
        Config._config = {}
        # 使用不存在的文件路径
        Config.load_config('non_existent_config.toml')
        # 应该返回默认值
        self.assertEqual(Config.get('api.stock_data_url'), None)

if __name__ == '__main__':
    unittest.main()