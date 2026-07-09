"""
LLM 客户端单元测试
测试 LLMClient 类的各项功能
"""

import unittest
from unittest.mock import patch, MagicMock
from src.core.llm_client import (
    LLMClient, 
    LLMResponse,
    call_llm, 
    call_llm_mock, 
    call_llm_real,
    get_client
)


class TestLLMResponse(unittest.TestCase):
    """测试 LLMResponse 数据类"""
    
    def test_create_response(self):
        """创建响应对象"""
        response = LLMResponse(
            text="Hello",
            tokens_used=10,
            model="gpt-3.5-turbo",
            latency_ms=100.5,
            success=True
        )
        self.assertEqual(response.text, "Hello")
        self.assertEqual(response.tokens_used, 10)
        self.assertTrue(response.success)
    
    def test_response_with_error(self):
        """带错误的响应"""
        response = LLMResponse(
            text="",
            tokens_used=0,
            model="gpt-3.5-turbo",
            latency_ms=0,
            success=False,
            error="Connection timeout"
        )
        self.assertFalse(response.success)
        self.assertEqual(response.error, "Connection timeout")


class TestLLMClientInit(unittest.TestCase):
    """测试 LLMClient 初始化"""
    
    def test_default_init(self):
        """默认初始化"""
        client = LLMClient()
        self.assertEqual(client.model, "gpt-3.5-turbo")
        self.assertEqual(client.max_tokens, 1000)
        self.assertEqual(client.temperature, 0.7)
        self.assertEqual(client.timeout, 30)
        self.assertEqual(client.retry_attempts, 3)
    
    def test_custom_init(self):
        """自定义初始化"""
        client = LLMClient(
            api_key="test-key",
            model="gpt-4",
            max_tokens=2000,
            temperature=0.5,
            timeout=60
        )
        self.assertEqual(client.api_key, "test-key")
        self.assertEqual(client.model, "gpt-4")
        self.assertEqual(client.max_tokens, 2000)
        self.assertEqual(client.temperature, 0.5)
        self.assertEqual(client.timeout, 60)


class TestMockResponse(unittest.TestCase):
    """测试 Mock 响应"""
    
    def setUp(self):
        self.client = LLMClient()
    
    def test_mock_print_hello(self):
        """测试打印 Hello 的 mock 响应"""
        response = self.client._mock_response("Print Hello World")
        self.assertTrue(response.success)
        self.assertIn("print", response.text)
    
    def test_mock_syntax_error_fix(self):
        """测试语法错误修复的 mock 响应"""
        prompt = "Fix this: def test()\n    pass\nSyntaxError: invalid syntax"
        response = self.client._mock_response(prompt)
        self.assertTrue(response.success)
    
    def test_mock_fix_error(self):
        """测试 Fix the error 的 mock 响应"""
        response = self.client._mock_response("Fix the error in this code")
        self.assertTrue(response.success)
        self.assertIn("Fixed", response.text)
    
    def test_mock_default(self):
        """测试默认 mock 响应"""
        response = self.client._mock_response("Random prompt")
        self.assertTrue(response.success)
        self.assertIn("Hello from LLM", response.text)


class TestLLMClientCall(unittest.TestCase):
    """测试 LLMClient.call() 方法"""
    
    def test_call_without_api_key_uses_mock(self):
        """无 API key 时使用 mock"""
        client = LLMClient(api_key="")
        response = client.call("Test prompt")
        self.assertTrue(response.success)
        self.assertEqual(response.model, "mock")
    
    def test_call_returns_LLMResponse(self):
        """调用返回 LLMResponse 对象"""
        client = LLMClient(api_key="")
        response = client.call("Test")
        self.assertIsInstance(response, LLMResponse)
        self.assertTrue(hasattr(response, 'text'))
        self.assertTrue(hasattr(response, 'tokens_used'))
        self.assertTrue(hasattr(response, 'latency_ms'))


class TestConvenienceFunctions(unittest.TestCase):
    """测试便捷函数"""
    
    def test_call_llm(self):
        """测试 call_llm 函数"""
        result = call_llm("Test prompt")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_call_llm_mock(self):
        """测试 call_llm_mock 函数"""
        result = call_llm_mock("Test")
        self.assertIsInstance(result, str)
    
    def test_get_client(self):
        """测试 get_client 函数"""
        client = get_client()
        self.assertIsInstance(client, LLMClient)
        
        # 第二次调用应该返回同一个实例
        client2 = get_client()
        self.assertIs(client, client2)


class TestLLMClientEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def test_empty_prompt(self):
        """空提示词"""
        client = LLMClient(api_key="")
        response = client.call("")
        self.assertTrue(response.success)
    
    def test_very_long_prompt(self):
        """超长提示词"""
        client = LLMClient(api_key="")
        long_prompt = "Test " * 1000
        response = client.call(long_prompt)
        self.assertTrue(response.success)
    
    def test_special_characters(self):
        """特殊字符"""
        client = LLMClient(api_key="")
        prompt = "Test with special chars: !@#$%^&*()_+{}|:<>?"
        response = client.call(prompt)
        self.assertTrue(response.success)
    
    def test_unicode_prompt(self):
        """Unicode 字符"""
        client = LLMClient(api_key="")
        prompt = "测试中文和 emoji 🚀✨"
        response = client.call(prompt)
        self.assertTrue(response.success)


class TestRetryMechanism(unittest.TestCase):
    """测试重试机制"""
    
    def test_retry_config(self):
        """测试重试配置"""
        client = LLMClient(
            retry_attempts=5,
            retry_delay=0.5
        )
        self.assertEqual(client.retry_attempts, 5)
        self.assertEqual(client.retry_delay, 0.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
