"""
配置管理模块
支持从环境变量、配置文件加载设置
优化：使用 functools.lru_cache 缓存配置，避免重复解析
"""

import os
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from functools import lru_cache


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
        
        # LLM 配置 - 批量读取环境变量
        env_mappings = {
            'LLM_API_KEY': ('llm', 'api_key'),
            'LLM_API_BASE': ('llm', 'api_base'),
            'LLM_MODEL': ('llm', 'model'),
            'LLM_MAX_TOKENS': ('llm', 'max_tokens', int),
            'LLM_TEMPERATURE': ('llm', 'temperature', float),
            'LLM_TIMEOUT': ('llm', 'timeout', int),
            'LLM_RETRY_ATTEMPTS': ('llm', 'retry_attempts', int),
            'LLM_RETRY_DELAY': ('llm', 'retry_delay', float),
            'SANDBOX_TIMEOUT': ('sandbox', 'timeout', int),
            'SANDBOX_MAX_MEMORY_MB': ('sandbox', 'max_memory_mb', int),
            'SANDBOX_ALLOW_NETWORK': ('sandbox', 'allow_network', lambda x: x.lower() == 'true'),
            'DEBUG_MAX_ATTEMPTS': ('debug', 'max_attempts', int),
            'DEBUG_USE_CACHE': ('debug', 'use_cache', lambda x: x.lower() == 'true'),
            'DEBUG_LOG_LEVEL': ('debug', 'log_level'),
            'DEBUG_LOG_FILE': ('debug', 'log_file'),
        }
        
        for env_var, mapping in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                section, attr = mapping[0], mapping[1]
                converter = mapping[2] if len(mapping) > 2 else lambda x: x
                
                try:
                    converted_value = converter(value)
                    setattr(getattr(config, section), attr, converted_value)
                except (ValueError, AttributeError):
                    pass  # 使用默认值
        
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
        
        section_map = {
            'llm': config.llm,
            'sandbox': config.sandbox,
            'debug': config.debug
        }
        
        for section_name, section_obj in section_map.items():
            if section_name in data:
                for key, value in data[section_name].items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
        
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


# 全局配置缓存
_config_cache: Optional[Config] = None


def get_config(cached: bool = True) -> Config:
    """
    获取当前配置（优先从环境变量加载）
    
    Args:
        cached: 是否使用缓存（默认 True）
    
    Returns:
        Config: 配置对象
    """
    global _config_cache
    
    if cached and _config_cache is not None:
        return _config_cache
    
    config = Config.from_env()
    
    if cached:
        _config_cache = config
    
    return config


def clear_config_cache():
    """清除配置缓存"""
    global _config_cache
    _config_cache = None


if __name__ == "__main__":
    # 测试配置功能
    config = get_config()
    print("Current Configuration:")
    print(json.dumps(config.to_dict(), indent=2))
    
    # 保存示例配置
    config.save_to_json("config.example.json")
    print("\nSaved example config to config.example.json")
