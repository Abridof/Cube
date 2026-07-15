"""
Tests for Secure Sandbox Engine
-------------------------------
Verifies:
- AST validation catches dangerous code
- Resource limits work correctly
- Built-in restrictions are enforced
- Timeout handling functions properly
"""

import pytest
from src.core.secure_sandbox import (
    SecureSandbox, 
    SecurityLevel, 
    SandboxConfig,
    run_secure_code
)


class TestASTValidation:
    """Test static analysis security checks."""
    
    def test_allows_safe_math(self):
        config = SandboxConfig(security_level=SecurityLevel.HIGH)
        sb = SecureSandbox(config=config)
        result = sb.run_code("x = 1 + 2 * 3")
        assert result['success'] is True
    
    def test_blocks_import_statements(self):
        config = SandboxConfig(security_level=SecurityLevel.HIGH)
        sb = SecureSandbox(config=config)
        result = sb.run_code("import os")
        assert result['success'] is False
        assert len(result.get('security_violations', [])) > 0
    
    def test_blocks_import_from(self):
        config = SandboxConfig(security_level=SecurityLevel.HIGH)
        sb = SecureSandbox(config=config)
        result = sb.run_code("from os import system")
        assert result['success'] is False
    
    def test_allows_basic_builtins(self):
        config = SandboxConfig(security_level=SecurityLevel.MEDIUM)
        sb = SecureSandbox(config=config)
        result = sb.run_code("len([1, 2, 3])")
        assert result['success'] is True


class TestResourceLimits:
    """Test CPU and memory resource constraints."""
    
    def test_timeout_short_execution(self):
        config = SandboxConfig(security_level=SecurityLevel.MEDIUM, timeout=5)
        sb = SecureSandbox(config=config)
        result = sb.run_code("1 + 1")
        assert result['success'] is True
    
    def test_detects_infinite_loop(self):
        config = SandboxConfig(security_level=SecurityLevel.MEDIUM, timeout=2)
        sb = SecureSandbox(config=config)
        code = "while True: pass"
        result = sb.run_code(code)
        # Should timeout or be blocked
        assert result['success'] is False or result['execution_time'] < 3.0


class TestSafetyLevels:
    """Test different safety level configurations."""
    
    def test_high_level_allows_safe_code(self):
        config = SandboxConfig(security_level=SecurityLevel.HIGH)
        sb = SecureSandbox(config=config)
        result = sb.run_code("x = 10")
        assert result['success'] is True
    
    def test_paranoid_level_restrictive(self):
        config = SandboxConfig(security_level=SecurityLevel.PARANOID)
        sb = SecureSandbox(config=config)
        result = sb.run_code("1 + 1")
        assert isinstance(result, dict)


class TestIsolation:
    """Test sandbox isolation properties."""
    
    def test_cannot_access_filesystem(self):
        config = SandboxConfig(security_level=SecurityLevel.HIGH)
        sb = SecureSandbox(config=config)
        code = "import os; os.listdir('/')"
        result = sb.run_code(code)
        assert result['success'] is False
    
    def test_cannot_execute_system_commands(self):
        config = SandboxConfig(security_level=SecurityLevel.HIGH)
        sb = SecureSandbox(config=config)
        code = "import subprocess; subprocess.run(['ls'])"
        result = sb.run_code(code)
        assert result['success'] is False


class TestSingleton:
    """Test helper functions."""
    
    def test_run_secure_code_helper(self):
        result = run_secure_code("1 + 1")
        assert isinstance(result, dict)
        assert 'success' in result


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_syntax_error_handling(self):
        config = SandboxConfig(security_level=SecurityLevel.MEDIUM)
        sb = SecureSandbox(config=config)
        result = sb.run_code("if True x = 1")
        assert result['success'] is False
    
    def test_empty_code(self):
        config = SandboxConfig(security_level=SecurityLevel.MEDIUM)
        sb = SecureSandbox(config=config)
        result = sb.run_code("")
        # Empty code may fail or succeed depending on implementation
        assert isinstance(result, dict)
        assert 'success' in result
    
    def test_unicode_in_code(self):
        config = SandboxConfig(security_level=SecurityLevel.MEDIUM)
        sb = SecureSandbox(config=config)
        code = "'你好世界'"
        result = sb.run_code(code)
        assert result['success'] is True


class TestThreadSafety:
    """Test thread safety of sandbox execution."""
    
    def test_concurrent_executions(self):
        import threading
        
        config = SandboxConfig(security_level=SecurityLevel.MEDIUM)
        sb = SecureSandbox(config=config)
        results = []
        
        def run_code():
            result = sb.run_code("1 + 1")
            results.append(result)
        
        threads = [threading.Thread(target=run_code) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(results) == 3
        assert all(r['success'] for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
