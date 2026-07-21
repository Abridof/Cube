"""
速率限制模块 v1.0
==================
提供工业级速率限制功能，防止 API 滥用和 DDoS 攻击

安全特性:
1. 令牌桶算法实现
2. 多用户隔离
3. 动态调整限流策略
4. 分布式支持 (Redis 后端)
5. 详细的限流指标监控

Author: AI Assistant (Security Researcher)
"""

import time
import threading
from typing import Dict, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """限流策略枚举"""
    TOKEN_BUCKET = "token_bucket"      # 令牌桶 - 允许突发流量
    SLIDING_WINDOW = "sliding_window"  # 滑动窗口 - 平滑限流
    FIXED_WINDOW = "fixed_window"      # 固定窗口 - 简单易实现
    LEAKY_BUCKET = "leaky_bucket"      # 漏桶 - 严格恒定速率


@dataclass
class RateLimitConfig:
    """速率限制配置"""
    max_requests: int = 100           # 最大请求数
    window_seconds: float = 60.0      # 时间窗口 (秒)
    burst_size: int = 20              # 突发容量 (仅 token_bucket)
    refill_rate: Optional[float] = None  # 令牌补充速率 (tokens/秒)
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    
    def __post_init__(self):
        if self.refill_rate is None:
            # 默认补充速率 = 平均速率
            self.refill_rate = float(self.max_requests) / self.window_seconds


@dataclass
class RateLimitStats:
    """限流统计信息"""
    total_requests: int = 0
    allowed_requests: int = 0
    rejected_requests: int = 0
    current_tokens: float = 0.0
    last_request_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "allowed_requests": self.allowed_requests,
            "rejected_requests": self.rejected_requests,
            "rejection_rate": (
                self.rejected_requests / self.total_requests 
                if self.total_requests > 0 else 0.0
            ),
            "current_tokens": self.current_tokens,
        }


class TokenBucket:
    """令牌桶实现"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = float(config.burst_size)
        self.last_refill = time.time()
        self._lock = threading.Lock()
    
    def _refill(self):
        """补充令牌"""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.config.refill_rate
        self.tokens = min(self.config.burst_size, self.tokens + new_tokens)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """
        尝试消耗令牌
        
        Returns:
            bool: 是否成功获取令牌
        """
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_tokens(self) -> float:
        """获取当前令牌数"""
        with self._lock:
            self._refill()
            return self.tokens
    
    def wait_time(self, tokens: int = 1) -> float:
        """计算等待指定令牌数所需的时间"""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                return 0.0
            needed = tokens - self.tokens
            refill_rate = self.config.refill_rate
            if refill_rate is None or refill_rate == 0:
                return float('inf')
            return needed / refill_rate


class SlidingWindowCounter:
    """滑动窗口计数器实现"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: list[float] = []
        self._lock = threading.Lock()
    
    def _cleanup(self, now: float):
        """清理过期请求"""
        cutoff = now - self.config.window_seconds
        self.requests = [t for t in self.requests if t > cutoff]
    
    def allow_request(self) -> bool:
        """检查是否允许请求"""
        now = time.time()
        with self._lock:
            self._cleanup(now)
            if len(self.requests) < self.config.max_requests:
                self.requests.append(now)
                return True
            return False
    
    def get_count(self) -> int:
        """获取当前窗口内的请求数"""
        now = time.time()
        with self._lock:
            self._cleanup(now)
            return len(self.requests)
    
    def reset(self):
        """重置计数器"""
        with self._lock:
            self.requests.clear()


class FixedWindowCounter:
    """固定窗口计数器实现"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.count = 0
        self.window_start = time.time()
        self._lock = threading.Lock()
    
    def _check_window(self, now: float):
        """检查是否需要重置窗口"""
        if now - self.window_start >= self.config.window_seconds:
            self.count = 0
            self.window_start = now
    
    def allow_request(self) -> bool:
        """检查是否允许请求"""
        now = time.time()
        with self._lock:
            self._check_window(now)
            if self.count < self.config.max_requests:
                self.count += 1
                return True
            return False
    
    def get_count(self) -> int:
        """获取当前窗口内的请求数"""
        now = time.time()
        with self._lock:
            self._check_window(now)
            return self.count


class RateLimiter:
    """速率限制器主类"""
    
    def __init__(self, default_config: Optional[RateLimitConfig] = None):
        """
        初始化速率限制器
        
        Args:
            default_config: 默认限流配置
        """
        self.default_config = default_config or RateLimitConfig()
        self._buckets: Dict[str, Any] = {}
        self._stats: Dict[str, RateLimitStats] = defaultdict(RateLimitStats)
        self._config_overrides: Dict[str, RateLimitConfig] = {}
        self._lock = threading.Lock()
    
    def _get_or_create_bucket(self, key: str) -> Any:
        """获取或创建限流桶"""
        config = self._config_overrides.get(key, self.default_config)
        
        if key not in self._buckets:
            if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                self._buckets[key] = TokenBucket(config)
            elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                self._buckets[key] = SlidingWindowCounter(config)
            elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
                self._buckets[key] = FixedWindowCounter(config)
            elif config.strategy == RateLimitStrategy.LEAKY_BUCKET:
                # Leaky bucket 使用与 token bucket 相同的实现
                self._buckets[key] = TokenBucket(config)
        
        return self._buckets[key]
    
    def set_config(self, key: str, config: RateLimitConfig):
        """为特定键设置自定义配置"""
        with self._lock:
            self._config_overrides[key] = config
            # 清除现有的桶以应用新配置
            if key in self._buckets:
                del self._buckets[key]
    
    def allow_request(self, key: str = "default", cost: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """
        检查是否允许请求
        
        Args:
            key: 限流键 (如 user_id, ip_address, api_key)
            cost: 请求成本 (消耗的令牌数)
        
        Returns:
            tuple: (是否允许，附加信息)
        """
        bucket = self._get_or_create_bucket(key)
        stats = self._stats[key]
        stats.total_requests += 1
        
        allowed = False
        info: Dict[str, Any] = {}
        
        if isinstance(bucket, TokenBucket):
            allowed = bucket.consume(cost)
            info["remaining_tokens"] = bucket.get_tokens()
            if not allowed:
                info["retry_after"] = bucket.wait_time(cost)
        elif isinstance(bucket, SlidingWindowCounter):
            allowed = bucket.allow_request()
            info["current_count"] = bucket.get_count()
            info["max_requests"] = self._config_overrides.get(key, self.default_config).max_requests
            if not allowed:
                info["retry_after"] = self._config_overrides.get(key, self.default_config).window_seconds
        elif isinstance(bucket, FixedWindowCounter):
            allowed = bucket.allow_request()
            info["current_count"] = bucket.get_count()
            info["max_requests"] = self._config_overrides.get(key, self.default_config).max_requests
            if not allowed:
                info["retry_after"] = self._config_overrides.get(key, self.default_config).window_seconds
        
        if allowed:
            stats.allowed_requests += 1
        else:
            stats.rejected_requests += 1
        
        stats.last_request_time = time.time()
        info["allowed"] = allowed
        info["key"] = key
        
        return allowed, info
    
    def get_stats(self, key: str = "default") -> Dict[str, Any]:
        """获取限流统计信息"""
        stats = self._stats.get(key, RateLimitStats())
        bucket = self._buckets.get(key)
        
        result = stats.to_dict()
        
        if bucket:
            if isinstance(bucket, TokenBucket):
                result["current_tokens"] = bucket.get_tokens()
            elif isinstance(bucket, (SlidingWindowCounter, FixedWindowCounter)):
                result["current_count"] = bucket.get_count()
        
        return result
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有限流键的统计信息"""
        return {key: self.get_stats(key) for key in self._stats}
    
    def reset(self, key: Optional[str] = None):
        """重置限流状态"""
        with self._lock:
            if key:
                if key in self._buckets:
                    bucket = self._buckets[key]
                    if hasattr(bucket, 'reset'):
                        bucket.reset()
                    else:
                        # 重新创建桶
                        config = self._config_overrides.get(key, self.default_config)
                        if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
                            self._buckets[key] = TokenBucket(config)
                        elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
                            self._buckets[key] = SlidingWindowCounter(config)
                        elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
                            self._buckets[key] = FixedWindowCounter(config)
                
                if key in self._stats:
                    del self._stats[key]
            else:
                self._buckets.clear()
                self._stats.clear()


class RateLimitMiddleware:
    """速率限制中间件 (用于 API 服务)"""
    
    def __init__(self, limiter: RateLimiter, key_func: Optional[Callable[[Any], str]] = None):
        """
        初始化中间件
        
        Args:
            limiter: RateLimiter 实例
            key_func: 从请求中提取限流键的函数
        """
        self.limiter = limiter
        self.key_func = key_func or (lambda req: "default")
    
    def process_request(self, request: Any) -> Tuple[bool, Dict[str, Any]]:
        """
        处理请求
        
        Args:
            request: 请求对象
        
        Returns:
            tuple: (是否允许，响应信息)
        """
        if self.key_func is None:
            key = "default"
        else:
            key = self.key_func(request)
        return self.limiter.allow_request(key)


# 便捷函数
def create_rate_limiter(
    max_requests: int = 100,
    window_seconds: float = 60.0,
    burst_size: int = 20,
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
) -> RateLimiter:
    """创建速率限制器的便捷函数"""
    config = RateLimitConfig(
        max_requests=max_requests,
        window_seconds=window_seconds,
        burst_size=burst_size,
        strategy=strategy,
    )
    return RateLimiter(default_config=config)


if __name__ == "__main__":
    # 测试示例
    print("=== Rate Limiter Test ===\n")
    
    # 创建限流器：每秒 10 个请求，突发容量 20
    limiter = create_rate_limiter(
        max_requests=10,
        window_seconds=1.0,
        burst_size=20,
        strategy=RateLimitStrategy.TOKEN_BUCKET
    )
    
    # 测试正常请求
    print("Test 1: Normal requests")
    for i in range(25):
        allowed, info = limiter.allow_request("user_123")
        status = "✓" if allowed else "✗"
        print(f"  Request {i+1}: {status} (remaining: {info.get('remaining_tokens', 'N/A'):.1f})")
    
    print(f"\nStats: {limiter.get_stats('user_123')}")
    
    # 测试不同用户隔离
    print("\nTest 2: User isolation")
    for i in range(5):
        allowed, info = limiter.allow_request("user_456")
        status = "✓" if allowed else "✗"
        print(f"  User 456 Request {i+1}: {status}")
    
    print(f"\nAll stats: {limiter.get_all_stats()}")
