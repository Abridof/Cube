"""
测试速率限制模块
================
验证速率限制器的各种功能和边界情况

Author: AI Assistant (QA Engineer)
"""

import pytest
import time
from typing import Dict, Any

from services.rate_limiter import (
    RateLimiter,
    RateLimitConfig,
    RateLimitStrategy,
    TokenBucket,
    SlidingWindowCounter,
    FixedWindowCounter,
    RateLimitStats,
    create_rate_limiter,
    RateLimitMiddleware,
)


class TestRateLimitConfig:
    """测试配置类"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = RateLimitConfig()
        assert config.max_requests == 100
        assert config.window_seconds == 60.0
        assert config.burst_size == 20
        assert config.strategy == RateLimitStrategy.TOKEN_BUCKET
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = RateLimitConfig(
            max_requests=50,
            window_seconds=30.0,
            burst_size=10,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
        )
        assert config.max_requests == 50
        assert config.window_seconds == 30.0
        assert config.burst_size == 10
        assert config.strategy == RateLimitStrategy.SLIDING_WINDOW
    
    def test_auto_refill_rate(self):
        """测试自动计算补充速率"""
        config = RateLimitConfig(max_requests=100, window_seconds=10.0)
        assert config.refill_rate == 10.0  # 100/10 = 10 tokens/秒


class TestTokenBucket:
    """测试令牌桶算法"""
    
    def test_initial_tokens(self):
        """测试初始令牌数"""
        config = RateLimitConfig(burst_size=10)
        bucket = TokenBucket(config)
        assert bucket.get_tokens() == 10.0
    
    def test_consume_tokens(self):
        """测试消耗令牌"""
        config = RateLimitConfig(burst_size=10)
        bucket = TokenBucket(config)
        
        assert bucket.consume(5) is True
        tokens_after_first = bucket.get_tokens()
        assert 4.9 <= tokens_after_first <= 5.1  # 允许微小误差
        
        assert bucket.consume(5) is True
        tokens_after_second = bucket.get_tokens()
        assert -0.1 <= tokens_after_second <= 0.5  # 允许微小误差和补充
        
        assert bucket.consume(1) is False
    
    def test_token_refill(self):
        """测试令牌补充"""
        config = RateLimitConfig(
            max_requests=10,
            window_seconds=1.0,
            burst_size=10,
        )
        bucket = TokenBucket(config)
        
        # 消耗所有令牌
        for _ in range(10):
            bucket.consume(1)
        
        tokens_after_consume = bucket.get_tokens()
        assert -0.1 <= tokens_after_consume <= 0.5  # 允许微小误差和补充
        
        # 等待补充
        time.sleep(0.5)  # 应该补充约 5 个令牌
        
        tokens = bucket.get_tokens()
        assert 4.0 <= tokens <= 6.0  # 允许一定误差
    
    def test_wait_time(self):
        """测试等待时间计算"""
        config = RateLimitConfig(
            max_requests=10,
            window_seconds=1.0,
            burst_size=10,
        )
        bucket = TokenBucket(config)
        
        # 消耗所有令牌
        for _ in range(10):
            bucket.consume(1)
        
        # 需要等待约 0.1 秒才能获得 1 个令牌
        wait = bucket.wait_time(1)
        assert 0.05 <= wait <= 0.15


class TestSlidingWindowCounter:
    """测试滑动窗口计数器"""
    
    def test_allow_within_limit(self):
        """测试限制内允许请求"""
        config = RateLimitConfig(max_requests=5, window_seconds=1.0)
        counter = SlidingWindowCounter(config)
        
        for i in range(5):
            assert counter.allow_request() is True
        
        assert counter.get_count() == 5
    
    def test_reject_over_limit(self):
        """测试超出限制拒绝请求"""
        config = RateLimitConfig(max_requests=3, window_seconds=1.0)
        counter = SlidingWindowCounter(config)
        
        for _ in range(3):
            counter.allow_request()
        
        assert counter.allow_request() is False
    
    def test_window_expiry(self):
        """测试窗口过期"""
        config = RateLimitConfig(max_requests=3, window_seconds=0.5)
        counter = SlidingWindowCounter(config)
        
        # 填满窗口
        for _ in range(3):
            counter.allow_request()
        
        assert counter.allow_request() is False
        
        # 等待窗口过期
        time.sleep(0.6)
        
        # 应该可以再次请求
        assert counter.allow_request() is True
    
    def test_reset(self):
        """测试重置"""
        config = RateLimitConfig(max_requests=5, window_seconds=1.0)
        counter = SlidingWindowCounter(config)
        
        for _ in range(3):
            counter.allow_request()
        
        counter.reset()
        assert counter.get_count() == 0


class TestFixedWindowCounter:
    """测试固定窗口计数器"""
    
    def test_allow_within_limit(self):
        """测试限制内允许请求"""
        config = RateLimitConfig(max_requests=5, window_seconds=1.0)
        counter = FixedWindowCounter(config)
        
        for i in range(5):
            assert counter.allow_request() is True
    
    def test_reject_over_limit(self):
        """测试超出限制拒绝请求"""
        config = RateLimitConfig(max_requests=3, window_seconds=1.0)
        counter = FixedWindowCounter(config)
        
        for _ in range(3):
            counter.allow_request()
        
        assert counter.allow_request() is False


class TestRateLimiter:
    """测试速率限制器主类"""
    
    def test_default_strategy(self):
        """测试默认策略"""
        limiter = RateLimiter()
        allowed, info = limiter.allow_request("test")
        assert allowed is True
        assert "remaining_tokens" in info
    
    def test_user_isolation(self):
        """测试用户隔离"""
        config = RateLimitConfig(max_requests=3, burst_size=3)
        limiter = RateLimiter(default_config=config)
        
        # 用户 1 用尽配额
        for _ in range(3):
            limiter.allow_request("user1")
        
        _, info1 = limiter.allow_request("user1")
        assert info1["allowed"] is False
        
        # 用户 2 仍然可以请求
        _, info2 = limiter.allow_request("user2")
        assert info2["allowed"] is True
    
    def test_custom_config_per_key(self):
        """测试每键自定义配置"""
        limiter = RateLimiter()
        
        # 为特定用户设置更严格的限制
        strict_config = RateLimitConfig(max_requests=2, burst_size=2)
        limiter.set_config("strict_user", strict_config)
        
        for _ in range(2):
            limiter.allow_request("strict_user")
        
        allowed, _ = limiter.allow_request("strict_user")
        assert allowed is False
        
        # 普通用户不受影响
        allowed, _ = limiter.allow_request("normal_user")
        assert allowed is True
    
    def test_stats_tracking(self):
        """测试统计追踪"""
        limiter = RateLimiter()
        
        for _ in range(5):
            limiter.allow_request("test")
        
        stats = limiter.get_stats("test")
        assert stats["total_requests"] == 5
        assert stats["allowed_requests"] == 5
        assert stats["rejected_requests"] == 0
    
    def test_get_all_stats(self):
        """测试获取所有统计"""
        limiter = RateLimiter()
        
        limiter.allow_request("user1")
        limiter.allow_request("user2")
        limiter.allow_request("user1")
        
        all_stats = limiter.get_all_stats()
        assert "user1" in all_stats
        assert "user2" in all_stats
        assert all_stats["user1"]["total_requests"] == 2
        assert all_stats["user2"]["total_requests"] == 1
    
    def test_reset_key(self):
        """测试重置单个键"""
        config = RateLimitConfig(max_requests=2, burst_size=2)
        limiter = RateLimiter(default_config=config)
        
        for _ in range(2):
            limiter.allow_request("test")
        
        limiter.reset("test")
        
        allowed, _ = limiter.allow_request("test")
        assert allowed is True
    
    def test_reset_all(self):
        """测试重置所有"""
        limiter = RateLimiter()
        
        limiter.allow_request("user1")
        limiter.allow_request("user2")
        
        limiter.reset()
        
        all_stats = limiter.get_all_stats()
        assert len(all_stats) == 0


class TestRateLimitStrategies:
    """测试不同限流策略"""
    
    def test_token_bucket_burst(self):
        """测试令牌桶的突发能力"""
        config = RateLimitConfig(
            max_requests=10,
            window_seconds=1.0,
            burst_size=20,
            strategy=RateLimitStrategy.TOKEN_BUCKET,
        )
        limiter = RateLimiter(default_config=config)
        
        # 突发模式下应该允许最多 burst_size 个请求
        allowed_count = sum(
            1 for _ in range(25)
            if limiter.allow_request("test")[0]
        )
        assert allowed_count == 20
    
    def test_sliding_window_smooth(self):
        """测试滑动窗口的平滑限流"""
        config = RateLimitConfig(
            max_requests=10,
            window_seconds=1.0,
            strategy=RateLimitStrategy.SLIDING_WINDOW,
        )
        limiter = RateLimiter(default_config=config)
        
        # 滑动窗口应该严格限制在 max_requests
        allowed_count = sum(
            1 for _ in range(15)
            if limiter.allow_request("test")[0]
        )
        assert allowed_count == 10


class TestRateLimitMiddleware:
    """测试限流中间件"""
    
    def test_basic_middleware(self):
        """测试基本中间件功能"""
        limiter = RateLimiter()
        middleware = RateLimitMiddleware(limiter)
        
        # 模拟请求对象
        request = {"user_id": "test"}
        
        allowed, info = middleware.process_request(request)
        assert allowed is True
    
    def test_middleware_with_key_func(self):
        """测试带键提取函数的中间件"""
        limiter = RateLimiter()
        
        def extract_key(req):
            return req.get("user_id", "anonymous")
        
        middleware = RateLimitMiddleware(limiter, key_func=extract_key)
        
        request1 = {"user_id": "user1"}
        request2 = {"user_id": "user2"}
        
        allowed1, _ = middleware.process_request(request1)
        allowed2, _ = middleware.process_request(request2)
        
        assert allowed1 is True
        assert allowed2 is True


class TestCreateRateLimiter:
    """测试便捷创建函数"""
    
    def test_create_with_defaults(self):
        """测试使用默认值创建"""
        limiter = create_rate_limiter()
        allowed, _ = limiter.allow_request("test")
        assert allowed is True
    
    def test_create_with_custom_values(self):
        """测试使用自定义值创建"""
        limiter = create_rate_limiter(
            max_requests=50,
            window_seconds=30.0,
            burst_size=10,
        )
        
        config = limiter.default_config
        assert config.max_requests == 50
        assert config.window_seconds == 30.0
        assert config.burst_size == 10


class TestEdgeCases:
    """测试边界情况"""
    
    def test_zero_cost_request(self):
        """测试零成本请求"""
        limiter = RateLimiter()
        allowed, info = limiter.allow_request("test", cost=0)
        assert allowed is True
    
    def test_high_cost_request(self):
        """测试高成本请求"""
        config = RateLimitConfig(max_requests=10, burst_size=10)
        limiter = RateLimiter(default_config=config)
        
        # 请求成本超过可用令牌
        allowed, info = limiter.allow_request("test", cost=15)
        assert allowed is False
    
    def test_concurrent_access(self):
        """测试并发访问"""
        import threading
        
        limiter = RateLimiter()
        results = []
        
        def make_request():
            allowed, _ = limiter.allow_request("test")
            results.append(allowed)
        
        threads = [threading.Thread(target=make_request) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 所有请求都应该成功处理（不报错）
        assert len(results) == 20


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 创建限流器
        limiter = create_rate_limiter(
            max_requests=10,
            window_seconds=1.0,
            burst_size=15,
        )
        
        # 模拟正常流量
        for i in range(10):
            allowed, info = limiter.allow_request("user_normal")
            assert allowed is True
        
        # 模拟突发流量
        burst_results = [
            limiter.allow_request("user_burst")[0]
            for _ in range(20)
        ]
        
        # 部分应该被拒绝
        assert any(burst_results)
        assert not all(burst_results)
        
        # 检查统计
        stats = limiter.get_all_stats()
        assert "user_normal" in stats
        assert "user_burst" in stats
        
        # 等待恢复
        time.sleep(1.1)
        
        # 应该可以再次请求
        allowed, _ = limiter.allow_request("user_burst")
        assert allowed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
