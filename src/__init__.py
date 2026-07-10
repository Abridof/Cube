"""
AI Cognition Engine - 统一认知表示与自主智慧系统
===================================================

版本：v9.0
愿景："识别万物，研究万物"

核心架构:
- 统一认知表示层 (UCR): 符号 - 向量混合表示
- 知识图谱与元学习：关系网络与策略优化
- 多模态感知层：跨模态融合与对齐
- 世界模型：状态空间建模与因果推理
- 通用认知引擎：感知 - 推理 - 行动 - 学习循环
- 具身环境：仿真环境与多智能体社会
- 自反思模块：代码自我分析与改进
- 长期演化引擎：7x24 小时自主学习
"""

__version__ = "9.0.0"
__author__ = "AI Cognition Engine Team"
__license__ = "MIT"

from .core.config import Config, LLMConfig, SandboxConfig, DebugConfig, get_config
from .core.llm_client import LLMClient, LLMResponse
from .core.secure_sandbox import SecureSandbox
from .core.token_optimizer import TokenOptimizer
from .core.smart_debug_loop import SmartDebugLoop, LocalFixer, ContextCompressor

__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__license__",
    # 核心配置
    "Config",
    "LLMConfig",
    "SandboxConfig",
    "DebugConfig",
    "get_config",
    # LLM 客户端
    "LLMClient",
    "LLMResponse",
    # 安全沙箱
    "SecureSandbox",
    # Token 优化
    "TokenOptimizer",
    # 智能调试
    "SmartDebugLoop",
    "LocalFixer",
    "ContextCompressor",
]
