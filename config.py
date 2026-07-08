"""
配置管理模块
支持从环境变量、配置文件加载设置
"""

import os
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """LLM 配置"""
    api_key: str = ""
    api_base: str = "https://api.openai.com/v1"
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class SandboxConfig:
    """沙箱配置"""
    timeout: int = 5
    max_memory_mb: int = 256
    max_cpu_percent: int = 50
    allow_network: bool = False
    allowed_imports: list = field(default_factory=lambda: [
        'math', 'random', 'datetime', 'collections', 'itertools',
        'functools', 're', 'json', 'typing', 'dataclasses'
    ])
    blocked_imports: list = field(default_factory=lambda: [
        'os', 'sys', 'subprocess', 'socket', 'http', 'urllib',
        'pickle', 'marshal', 'ctypes', 'importlib'
    ])


@dataclass
class DebugConfig:
    """调试配置"""
    max_attempts: int = 5
    use_cache: bool = True
    cache_size: int = 1000
    enable_local_fix: bool = True
    enable_context_compression: bool = True
    log_level: str = "INFO"
    log_file: Optional[str] = None


@dataclass
class Config:
    """主配置类"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    debug: DebugConfig = field(default_factory=DebugConfig)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量加载配置"""
        config = cls()
        
        # LLM 配置
        if os.getenv('LLM_API_KEY'):
            config.llm.api_key = os.getenv('LLM_API_KEY')
        if os.getenv('LLM_API_BASE'):
            config.llm.api_base = os.getenv('LLM_API_BASE')
        if os.getenv('LLM_MODEL'):
            config.llm.model = os.getenv('LLM_MODEL')
        if os.getenv('LLM_MAX_TOKENS'):
            try:
                config.llm.max_tokens = int(os.getenv('LLM_MAX_TOKENS'))
            except ValueError:
                pass  # 使用默认值
        if os.getenv('LLM_TEMPERATURE'):
            try:
                config.llm.temperature = float(os.getenv('LLM_TEMPERATURE'))
            except ValueError:
                pass  # 使用默认值
        if os.getenv('LLM_TIMEOUT'):
            try:
                config.llm.timeout = int(os.getenv('LLM_TIMEOUT'))
            except ValueError:
                pass  # 使用默认值
        if os.getenv('LLM_RETRY_ATTEMPTS'):
            try:
                config.llm.retry_attempts = int(os.getenv('LLM_RETRY_ATTEMPTS'))
            except ValueError:
                pass  # 使用默认值
        if os.getenv('LLM_RETRY_DELAY'):
            try:
                config.llm.retry_delay = float(os.getenv('LLM_RETRY_DELAY'))
            except ValueError:
                pass  # 使用默认值
        
        # 沙箱配置
        if os.getenv('SANDBOX_TIMEOUT'):
            try:
                config.sandbox.timeout = int(os.getenv('SANDBOX_TIMEOUT'))
            except ValueError:
                pass  # 使用默认值
        if os.getenv('SANDBOX_MAX_MEMORY_MB'):
            try:
                config.sandbox.max_memory_mb = int(os.getenv('SANDBOX_MAX_MEMORY_MB'))
            except ValueError:
                pass  # 使用默认值
        if os.getenv('SANDBOX_ALLOW_NETWORK'):
            config.sandbox.allow_network = os.getenv('SANDBOX_ALLOW_NETWORK').lower() == 'true'
        
        # 调试配置
        if os.getenv('DEBUG_MAX_ATTEMPTS'):
            try:
                config.debug.max_attempts = int(os.getenv('DEBUG_MAX_ATTEMPTS'))
            except ValueError:
                pass  # 使用默认值
        if os.getenv('DEBUG_USE_CACHE'):
            config.debug.use_cache = os.getenv('DEBUG_USE_CACHE').lower() == 'true'
        if os.getenv('DEBUG_LOG_LEVEL'):
            config.debug.log_level = os.getenv('DEBUG_LOG_LEVEL')
        if os.getenv('DEBUG_LOG_FILE'):
            config.debug.log_file = os.getenv('DEBUG_LOG_FILE')
        
        return config
    
    @classmethod
    def from_json(cls, path: str) -> 'Config':
        """从 JSON 文件加载配置"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """从字典加载配置"""
        config = cls()
        
        if 'llm' in data:
            for key, value in data['llm'].items():
                if hasattr(config.llm, key):
                    setattr(config.llm, key, value)
        
        if 'sandbox' in data:
            for key, value in data['sandbox'].items():
                if hasattr(config.sandbox, key):
                    setattr(config.sandbox, key, value)
        
        if 'debug' in data:
            for key, value in data['debug'].items():
                if hasattr(config.debug, key):
                    setattr(config.debug, key, value)
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'llm': {
                'api_key': self.llm.api_key,
                'api_base': self.llm.api_base,
                'model': self.llm.model,
                'max_tokens': self.llm.max_tokens,
                'temperature': self.llm.temperature,
                'timeout': self.llm.timeout,
                'retry_attempts': self.llm.retry_attempts,
                'retry_delay': self.llm.retry_delay,
            },
            'sandbox': {
                'timeout': self.sandbox.timeout,
                'max_memory_mb': self.sandbox.max_memory_mb,
                'max_cpu_percent': self.sandbox.max_cpu_percent,
                'allow_network': self.sandbox.allow_network,
                'allowed_imports': self.sandbox.allowed_imports,
                'blocked_imports': self.sandbox.blocked_imports,
            },
            'debug': {
                'max_attempts': self.debug.max_attempts,
                'use_cache': self.debug.use_cache,
                'cache_size': self.debug.cache_size,
                'enable_local_fix': self.debug.enable_local_fix,
                'enable_context_compression': self.debug.enable_context_compression,
                'log_level': self.debug.log_level,
                'log_file': self.debug.log_file,
            }
        }
    
    def save_to_json(self, path: str):
        """保存配置到 JSON 文件"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


# 全局默认配置
default_config = Config()


def get_config() -> Config:
    """获取当前配置（优先从环境变量加载）"""
    return Config.from_env()


if __name__ == "__main__":
    # 测试配置功能
    config = get_config()
    print("Current Configuration:")
    print(json.dumps(config.to_dict(), indent=2))
    
    # 保存示例配置
    config.save_to_json("config.example.json")
    print("\nSaved example config to config.example.json")
