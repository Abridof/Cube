"""
单元测试：智能调试循环 (Token 优化版)
测试覆盖：
1. 本地修复功能 (LocalFixer)
2. 上下文压缩功能 (ContextCompressor)
3. 缓存机制 (SmartDebugLoop Cache)
4. Token 统计准确性
5. 集成测试
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加 ai-dev-system 到路径以导入依赖模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-dev-system'))

from smart_debug_loop import (
    LocalFixer, 
    ContextCompressor, 
    SmartDebugLoop, 
    TokenStats,
    run_smart_debug
)

class TestLocalFixer(unittest.TestCase):
    """测试本地修复器"""
    
    def test_fix_missing_colon_def(self):
        """修复 def 缺失冒号"""
        code = "def hello()\n    print('Hi')"
        error = "SyntaxError: invalid syntax"
        fixed = LocalFixer.try_fix(code, error)
        self.assertIsNotNone(fixed)
        self.assertIn("def hello():", fixed)
    
    def test_fix_missing_colon_if(self):
        """修复 if 缺失冒号"""
        code = "if True\n    print('Yes')"
        error = "SyntaxError: invalid syntax"
        fixed = LocalFixer.try_fix(code, error)
        self.assertIsNotNone(fixed)
        self.assertIn("if True:", fixed)
    
    def test_fix_typo_prnt(self):
        """修复 prnt 拼写错误"""
        code = "prnt('Hello')"
        error = "NameError: name 'prnt' is not defined"
        fixed = LocalFixer.try_fix(code, error)
        # 注意：当前实现主要针对 SyntaxError，这个可能不触发
        # 但模式匹配应该能工作
        self.assertEqual(fixed, "print('Hello')")
    
    def test_no_fix_needed(self):
        """无需修复时返回 None"""
        code = "print('Hello')"
        error = "RuntimeError: Something wrong"
        fixed = LocalFixer.try_fix(code, error)
        self.assertIsNone(fixed)
    
    def test_fix_indentation_mixed(self):
        """修复混合缩进"""
        code = "def test():\n    \tpass"
        error = "TabError: inconsistent use of tabs"
        fixed = LocalFixer.try_fix(code, error)
        self.assertIsNotNone(fixed)
        self.assertNotIn("    \t", fixed)

class TestContextCompressor(unittest.TestCase):
    """测试上下文压缩器"""
    
    def test_extract_error_lines(self):
        """提取错误行周围代码"""
        code = "\n".join([f"line_{i}" for i in range(1, 21)])
        error = "SyntaxError on line 10"
        compressed = ContextCompressor.compress(code, error)
        lines = compressed.split('\n')
        self.assertLessEqual(len(lines), 7)  # 最多 7 行 (error_line ± 3)
        self.assertTrue(any("line_10" in l for l in lines))
    
    def test_remove_comments_and_empty(self):
        """移除注释和空行"""
        code = """# Comment
line1

line2
# Another comment
line3"""
        error = "Some error"
        compressed = ContextCompressor.compress(code, error)
        self.assertNotIn("#", compressed)
        self.assertNotIn("", compressed.split('\n'))
    
    def test_no_compression_if_small(self):
        """小代码不压缩"""
        code = "print('Hi')"
        error = "Error"
        compressed = ContextCompressor.compress(code, error)
        self.assertEqual(compressed, code)

class TestTokenStats(unittest.TestCase):
    """测试 Token 统计"""
    
    def test_savings_rate_calculation(self):
        """计算节省率"""
        stats = TokenStats(
            total_requests=2,
            total_tokens_used=500,
            local_fixes=3,
            cache_hits=2
        )
        # 估算总消耗 = (2+3+2) * 500 = 3500
        # 实际消耗 = 500
        # 节省率 = (1 - 500/3500) * 100 ≈ 85.7%
        rate = stats.savings_rate()
        self.assertAlmostEqual(rate, 85.7, delta=0.5)
    
    def test_zero_division_handling(self):
        """零请求时避免除零错误"""
        stats = TokenStats()
        rate = stats.savings_rate()
        self.assertEqual(rate, 0.0)

class TestSmartDebugLoop(unittest.TestCase):
    """测试智能调试主循环"""
    
    @patch('smart_debug_loop.run_secure_code')
    @patch('smart_debug_loop.call_llm')
    def test_local_fix_prevents_llm_call(self, mock_llm, mock_exec):
        """本地修复成功时不调用 LLM"""
        # 第一次执行失败 (SyntaxError)
        mock_exec.side_effect = [
            {'success': False, 'error': 'SyntaxError: invalid syntax', 'output': ''},
            {'success': True, 'error': None, 'output': 'Hi'}
        ]
        
        loop = SmartDebugLoop()
        bad_code = "def hello()\n    print('Hi')"
        result = loop.run("Say hi", bad_code)
        
        # 验证 LLM 未被调用 (因为本地修复成功了)
        mock_llm.assert_not_called()
        self.assertEqual(result.token_stats.local_fixes, 1)
        self.assertTrue(result.success)
    
    @patch('smart_debug_loop.run_secure_code')
    @patch('smart_debug_loop.call_llm')
    def test_cache_hit_prevents_llm_call(self, mock_llm, mock_exec):
        """缓存命中时不调用 LLM"""
        # 第一次：失败 -> LLM 修复 -> 成功
        # 第二次：失败 -> 缓存命中 -> 成功
        
        mock_exec.side_effect = [
            {'success': False, 'error': 'RuntimeError', 'output': ''},  # 第一次失败
            {'success': True, 'error': None, 'output': 'Result'},       # 第一次重试成功
            {'success': False, 'error': 'RuntimeError', 'output': ''},  # 第二次失败
            {'success': True, 'error': None, 'output': 'Result'}        # 第二次重试成功
        ]
        
        mock_llm.return_value = "```python\nfixed_code = 'result'\n```"
        
        loop = SmartDebugLoop(use_cache=True)
        
        # 第一次运行 (会调用 LLM)
        result1 = loop.run("Test", "bad_code")
        llm_calls_first = mock_llm.call_count
        
        # 第二次运行相同错误 (应该命中缓存)
        result2 = loop.run("Test", "bad_code")
        llm_calls_second = mock_llm.call_count
        
        # 验证第二次没有新增 LLM 调用
        self.assertEqual(llm_calls_first, llm_calls_second)
        self.assertGreater(result2.token_stats.cache_hits, 0)
    
    @patch('smart_debug_loop.run_secure_code')
    @patch('smart_debug_loop.call_llm')
    def test_context_compression_reduces_tokens(self, mock_llm, mock_exec):
        """验证上下文压缩减少 Token"""
        long_code = "\n".join([f"# comment {i}\nline_{i}" for i in range(50)])
        
        mock_exec.return_value = {'success': False, 'error': 'Error on line 25', 'output': ''}
        mock_llm.return_value = "```python\nfixed\n```"
        
        loop = SmartDebugLoop(max_attempts=1)
        loop.run("Test", long_code)
        
        # 验证至少有一次压缩
        self.assertGreater(loop.stats.compressed_contexts, 0)
        
        # 验证 LLM 收到的 prompt 长度小于原代码
        call_args = mock_llm.call_args[0][0]
        self.assertLess(len(call_args), len(long_code))

class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    @patch('smart_debug_loop.run_secure_code')
    @patch('smart_debug_loop.call_llm')
    def test_full_workflow_with_savings(self, mock_llm, mock_exec):
        """完整工作流程并验证 Token 节省"""
        # 场景：代码有语法错误 -> 本地修复成功
        mock_exec.side_effect = [
            {'success': False, 'error': 'SyntaxError: invalid syntax', 'output': ''},
            {'success': True, 'error': None, 'output': 'Hello'}
        ]
        
        result = run_smart_debug("Print Hello", "def main()\n    print('Hello')")
        
        self.assertTrue(result.success)
        self.assertEqual(result.token_stats.local_fixes, 1)
        self.assertEqual(result.token_stats.total_requests, 0)  # 未调用 LLM
        self.assertGreater(result.token_stats.savings_rate(), 50)  # 节省率 > 50%
    
    @patch('smart_debug_loop.run_secure_code')
    @patch('smart_debug_loop.call_llm')
    def test_max_attempts_reached(self, mock_llm, mock_exec):
        """达到最大尝试次数"""
        mock_exec.return_value = {'success': False, 'error': 'Persistent Error', 'output': ''}
        mock_llm.return_value = "```python\nstill_broken\n```"
        
        loop = SmartDebugLoop(max_attempts=3)
        result = loop.run("Test", "broken_code")
        
        self.assertFalse(result.success)
        self.assertEqual(result.attempts, 3)
        self.assertIn("Persistent Error", result.error)

if __name__ == '__main__':
    unittest.main(verbosity=2)
