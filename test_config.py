"""
配置模块单元测试
"""

import unittest
import os
import json
import tempfile
from config import (
    Config, LLMConfig, SandboxConfig, DebugConfig,
    get_config
)


class TestLLMConfig(unittest.TestCase):
    """测试 LLM 配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = LLMConfig()
        self.assertEqual(config.api_key, "")
        self.assertEqual(config.api_base, "https://api.openai.com/v1")
        self.assertEqual(config.model, "gpt-3.5-turbo")
        self.assertEqual(config.max_tokens, 1000)
        self.assertEqual(config.temperature, 0.7)
    
    def test_custom_values(self):
        """测试自定义值"""
        config = LLMConfig(
            api_key="test-key",
            model="gpt-4",
            max_tokens=2000
        )
        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.model, "gpt-4")
        self.assertEqual(config.max_tokens, 2000)


class TestSandboxConfig(unittest.TestCase):
    """测试沙箱配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = SandboxConfig()
        self.assertEqual(config.timeout, 5)
        self.assertFalse(config.allow_network)
        self.assertIn('math', config.allowed_imports)
        self.assertIn('os', config.blocked_imports)


class TestDebugConfig(unittest.TestCase):
    """测试调试配置"""
    
    def test_default_values(self):
        """测试默认值"""
        config = DebugConfig()
        self.assertEqual(config.max_attempts, 5)
        self.assertTrue(config.use_cache)
        self.assertEqual(config.log_level, "INFO")


class TestConfigFromEnv(unittest.TestCase):
    """测试从环境变量加载配置"""
    
    def setUp(self):
        # 保存原始环境变量
        self.original_env = {
            'LLM_API_KEY': os.getenv('LLM_API_KEY'),
            'LLM_MODEL': os.getenv('LLM_MODEL'),
            'DEBUG_MAX_ATTEMPTS': os.getenv('DEBUG_MAX_ATTEMPTS'),
        }
    
    def tearDown(self):
        # 恢复原始环境变量
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    
    def test_load_from_env(self):
        """测试从环境变量加载"""
        os.environ['LLM_API_KEY'] = 'env-test-key'
        os.environ['LLM_MODEL'] = 'gpt-4-turbo'
        os.environ['DEBUG_MAX_ATTEMPTS'] = '10'
        
        config = Config.from_env()
        
        self.assertEqual(config.llm.api_key, 'env-test-key')
        self.assertEqual(config.llm.model, 'gpt-4-turbo')
        self.assertEqual(config.debug.max_attempts, 10)


class TestConfigFromJson(unittest.TestCase):
    """测试从 JSON 文件加载配置"""
    
    def test_save_and_load_json(self):
        """测试保存和加载 JSON"""
        config = Config()
        config.llm.api_key = "json-test-key"
        config.llm.model = "claude-3"
        config.debug.max_attempts = 8
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config.save_to_json(f.name)
            temp_path = f.name
        
        try:
            loaded = Config.from_json(temp_path)
            self.assertEqual(loaded.llm.api_key, "json-test-key")
            self.assertEqual(loaded.llm.model, "claude-3")
            self.assertEqual(loaded.debug.max_attempts, 8)
        finally:
            os.unlink(temp_path)
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = Config()
        data = config.to_dict()
        
        self.assertIn('llm', data)
        self.assertIn('sandbox', data)
        self.assertIn('debug', data)
        self.assertEqual(data['llm']['model'], "gpt-3.5-turbo")


class TestGetConfig(unittest.TestCase):
    """测试 get_config 函数"""
    
    def test_get_config_returns_instance(self):
        """测试 get_config 返回 Config 实例"""
        config = get_config()
        self.assertIsInstance(config, Config)


class TestConfigEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def test_empty_dict(self):
        """测试空字典"""
        config = Config.from_dict({})
        self.assertIsInstance(config, Config)
    
    def test_partial_dict(self):
        """测试部分字典"""
        config = Config.from_dict({'llm': {'model': 'test-model'}})
        self.assertEqual(config.llm.model, 'test-model')
        # 其他值应该是默认值
        self.assertEqual(config.llm.api_key, "")
    
    def test_invalid_env_values(self):
        """测试无效的环境变量值"""
        os.environ['LLM_MAX_TOKENS'] = 'invalid'
        # 不应该抛出异常，应该使用默认值
        config = Config.from_env()
        self.assertEqual(config.llm.max_tokens, 1000)
        del os.environ['LLM_MAX_TOKENS']


if __name__ == '__main__':
    unittest.main(verbosity=2)
