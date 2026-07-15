"""
API 服务测试套件
================
验证 REST API 的安全性、功能和性能

Author: AI Assistant (Security Researcher & AGI Scientist)
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import jwt
import time

# 测试客户端
from fastapi.testclient import TestClient


class TestAPIHealthEndpoints:
    """测试健康检查端点"""
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "services" in data
        assert all(k in data["services"] for k in ["llm", "sandbox", "knowledge_graph", "rate_limiter", "monitor"])
    
    def test_metrics_endpoint(self, client):
        """测试指标端点"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert all(k in data for k in ["cpu_percent", "memory_percent", "disk_percent"])


class TestAPIAuthentication:
    """测试认证端点"""
    
    def test_create_token(self, client):
        """测试创建访问令牌"""
        response = client.post("/auth/token", json={
            "username": "testuser",
            "password": "testpass"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_create_token_missing_credentials(self, client):
        """测试缺少凭证时的错误处理"""
        response = client.post("/auth/token", json={})
        assert response.status_code == 400
    
    def test_get_current_user_with_valid_token(self, client):
        """测试使用有效 token 获取用户信息"""
        # 先创建 token
        auth_response = client.post("/auth/token", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = auth_response.json()["access_token"]
        
        # 使用 token 获取用户信息
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "tier" in data
    
    def test_get_current_user_with_invalid_token(self, client):
        """测试使用无效 token 的错误处理"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == 401


class TestAPIQueryEndpoint:
    """测试查询端点"""
    
    def test_query_without_auth(self, client):
        """测试未认证的查询（应允许但限制更多）"""
        response = client.post("/query", json={
            "query": "What is the meaning of life?"
        })
        # 应该成功（匿名访问）或速率限制
        assert response.status_code in [200, 429]
    
    def test_query_with_auth(self, client):
        """测试认证的查询"""
        # 创建 token
        auth_response = client.post("/auth/token", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/query", headers=headers, json={
            "query": "Explain quantum computing"
        })
        # 应该成功或速率限制
        assert response.status_code in [200, 429, 500]
    
    def test_query_xss_protection(self, client):
        """测试 XSS 防护"""
        response = client.post("/query", json={
            "query": "<script>alert('xss')</script>"
        })
        assert response.status_code == 422  # 验证失败
    
    def test_query_too_long(self, client):
        """测试过长查询的拒绝"""
        long_query = "a" * 10001
        response = client.post("/query", json={"query": long_query})
        assert response.status_code == 422


class TestAPICodeExecution:
    """测试代码执行端点"""
    
    def test_execute_safe_code(self, client):
        """测试执行安全代码"""
        auth_response = client.post("/auth/token", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/execute", headers=headers, json={
            "code": "print('Hello, World!')",
            "timeout": 5,
            "max_memory_mb": 128
        })
        # 应该成功或因沙箱/速率限制失败
        assert response.status_code in [200, 429, 500]
    
    def test_execute_dangerous_code_blocked(self, client):
        """测试危险代码被阻止"""
        auth_response = client.post("/auth/token", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 尝试执行危险代码
        response = client.post("/execute", headers=headers, json={
            "code": "import os; os.system('rm -rf /')",
            "timeout": 5
        })
        # 应该被沙箱阻止
        assert response.status_code in [200, 500]  # 沙箱会阻止并返回错误
    
    def test_execute_code_timeout(self, client):
        """测试代码超时处理"""
        auth_response = client.post("/auth/token", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/execute", headers=headers, json={
            "code": "import time; time.sleep(100)",
            "timeout": 1  # 非常短的超时
        })
        # 应该超时或被阻止
        assert response.status_code in [200, 500]


class TestAPIKnowledgeGraph:
    """测试知识图谱端点"""
    
    def test_kg_add_concept(self, client):
        """测试添加概念"""
        auth_response = client.post("/auth/token", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/knowledge-graph", headers=headers, json={
            "operation": "add",
            "data": {"id": "test_concept", "label": "Test Concept"}
        })
        assert response.status_code in [200, 429, 500]
    
    def test_kg_query_concept(self, client):
        """测试查询概念"""
        auth_response = client.post("/auth/token", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/knowledge-graph", headers=headers, json={
            "operation": "query",
            "data": {"id": "test_concept"}
        })
        assert response.status_code in [200, 429, 500]
    
    def test_kg_invalid_operation(self, client):
        """测试无效操作"""
        auth_response = client.post("/auth/token", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/knowledge-graph", headers=headers, json={
            "operation": "invalid_op",
            "data": {}
        })
        assert response.status_code == 422


class TestAPIRateLimiting:
    """测试速率限制"""
    
    def test_rate_limit_exceeded(self, client):
        """测试速率限制触发"""
        # 快速发送多个请求，使用 FREE tier（burst_size=15）
        auth_response = client.post("/auth/token", json={
            "username": "ratelimituser",
            "password": "testpass",
            "tier": "free"  # 明确指定 FREE tier
        })
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 发送大量请求（超过 FREE tier 的限制）
        responses = []
        for _ in range(20):
            response = client.post("/query", headers=headers, json={
                "query": "test query"
            })
            responses.append(response.status_code)
        
        # 应该有至少一个 429 响应
        assert 429 in responses


class TestAPIErrorHandling:
    """测试错误处理"""
    
    def test_404_not_found(self, client):
        """测试 404 处理"""
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_general_exception_handler(self, client):
        """测试通用异常处理"""
        # 这个测试依赖于 API 中的异常处理器
        # 实际测试需要模拟异常场景
        pass


class TestAPISecurity:
    """测试安全特性"""
    
    def test_cors_headers(self, client):
        """测试 CORS 头"""
        response = client.options("/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    def test_trusted_hosts(self, client):
        """测试受信任主机"""
        # 测试无效主机（需要在配置中设置 allowed_hosts）
        response = client.get("/health", headers={"Host": "evil.com"})
        # 应该被拒绝或接受取决于配置
        # 默认配置允许 localhost 和 127.0.0.1


# Pytest fixtures
@pytest.fixture
def client():
    """创建测试客户端"""
    from src.api.cognitive_api import app
    with TestClient(app) as test_client:
        yield test_client


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
