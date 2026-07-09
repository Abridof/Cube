"""
Pytest 配置文件
提供共享的 fixtures 和测试工具
"""

import pytest
import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def sample_code():
    """示例代码片段"""
    return """
def hello_world():
    print('Hello, World!')

class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
"""


@pytest.fixture
def sample_error():
    """示例错误信息"""
    return "SyntaxError: invalid syntax on line 2"


@pytest.fixture
def mock_llm_response():
    """Mock LLM 响应"""
    class MockResponse:
        text = "```python\nprint('Fixed!')\n```"
        tokens_used = 25
        model = "mock"
        latency_ms = 10
        success = True
        error = None
    return MockResponse()


@pytest.fixture
def temp_config(tmp_path):
    """创建临时配置文件"""
    config_content = """
{
    "llm": {
        "api_key": "test-key",
        "model": "gpt-3.5-turbo",
        "max_tokens": 500
    },
    "sandbox": {
        "timeout": 3,
        "max_memory_mb": 128
    },
    "debug": {
        "max_attempts": 3,
        "use_cache": true
    }
}
"""
    config_file = tmp_path / "test_config.json"
    config_file.write_text(config_content)
    return str(config_file)
