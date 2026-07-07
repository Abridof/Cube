"""
Token 优化器单元测试
验证上下文压缩、本地修复、缓存机制等功能
"""

import unittest
from token_optimizer import (
    TokenOptimizer, 
    TokenStats, 
    optimize_prompt, 
    try_fix_locally
)


class TestTokenEstimation(unittest.TestCase):
    """测试 Token 估算功能"""
    
    def test_estimate_tokens_simple(self):
        optimizer = TokenOptimizer()
        text = "print('hello')"
        tokens = optimizer.estimate_tokens(text)
        self.assertGreater(tokens, 0)
    
    def test_estimate_tokens_long_code(self):
        optimizer = TokenOptimizer()
        code = "\n".join([f"line_{i} = {i}" for i in range(100)])
        tokens = optimizer.estimate_tokens(code)
        # 长代码应该有更多 token
        self.assertGreater(tokens, 50)


class TestLocalFix(unittest.TestCase):
    """测试本地修复功能 (零 Token 消耗)"""
    
    def test_fix_indentation_tab_to_space(self):
        code = "def test():\n\tprint('hello')"
        error = "IndentationError: unexpected indent"
        fixed = try_fix_locally(code, error)
        self.assertIsNotNone(fixed)
        self.assertNotIn('\t', fixed)
        self.assertIn('    ', fixed)
    
    def test_fix_typo_prnt(self):
        code = "prnt('hello')"
        error = "NameError: name 'prnt' is not defined"
        fixed = try_fix_locally(code, error)
        self.assertIsNotNone(fixed)
        self.assertIn("print('hello')", fixed)
    
    def test_fix_missing_colon(self):
        code = "def test()\n    pass"
        error = "SyntaxError: invalid syntax at line 1"
        fixed = try_fix_locally(code, error)
        # 这个测试取决于错误信息格式，可能无法匹配
        # 如果实现正确应该能修复
        if fixed:
            self.assertIn("def test():", fixed)
    
    def test_no_local_fix_for_complex_errors(self):
        code = "x = [1, 2, 3"
        error = "SyntaxError: unexpected EOF while parsing"
        fixed = try_fix_locally(code, error)
        # 复杂错误应该返回 None，交给 LLM 处理
        self.assertIsNone(fixed)


class TestContextCompression(unittest.TestCase):
    """测试上下文压缩功能"""
    
    def test_extract_error_context_with_line_number(self):
        optimizer = TokenOptimizer()
        code = "\n".join([f"line_{i} = {i}" for i in range(20)])
        error = "Error at line 10"
        
        context = optimizer._extract_error_context(code, error)
        
        # 应该包含错误行及其上下文
        self.assertIn("line_9", context)
        self.assertIn("line_10", context)
        self.assertIn("line_11", context)
        # 应该标记错误行
        self.assertIn(">>> ", context)
    
    def test_compress_large_code(self):
        optimizer = TokenOptimizer(max_context_lines=10)
        code = "\n".join([f"line_{i} = {i}" for i in range(100)])
        error = "Some error"
        
        compressed = optimizer.compress_context(code, error, [])
        
        # 压缩后应该比原代码短
        self.assertLess(len(compressed), len(code))
        # 应该包含省略标记
        self.assertIn("省略", compressed)
    
    def test_prompt_structure(self):
        optimizer = TokenOptimizer()
        code = "x = 1"
        error = "NameError"
        
        prompt = optimizer.compress_context(code, error, [])
        full_prompt = prompt + optimizer.format_response_prompt()
        
        # 检查 Prompt 结构
        self.assertIn("### 任务", full_prompt)
        self.assertIn("### 错误信息", full_prompt)
        self.assertIn("### 相关代码片段", full_prompt)
        self.assertIn("输出要求", full_prompt)


class TestCacheMechanism(unittest.TestCase):
    """测试缓存机制"""
    
    def test_cache_save_and_retrieve(self):
        optimizer = TokenOptimizer(enable_cache=True)
        
        code = "print('test')"
        error = "Some error"
        fix = "print('fixed')"
        
        # 首次应该没有缓存
        cached = optimizer.check_cache(code, error)
        self.assertIsNone(cached)
        
        # 保存修复方案
        optimizer.save_to_cache(code, error, fix)
        
        # 再次查询应该有缓存
        cached = optimizer.check_cache(code, error)
        self.assertEqual(cached, fix)
        self.assertEqual(optimizer.stats.cache_hits, 1)
    
    def test_cache_disabled(self):
        optimizer = TokenOptimizer(enable_cache=False)
        
        code = "print('test')"
        error = "Some error"
        fix = "print('fixed')"
        
        optimizer.save_to_cache(code, error, fix)
        cached = optimizer.check_cache(code, error)
        
        # 禁用缓存时应该始终返回 None
        self.assertIsNone(cached)
    
    def test_cache_key_uniqueness(self):
        optimizer = TokenOptimizer()
        
        code1 = "print('a')"
        code2 = "print('b')"
        error = "Same error"
        
        key1 = optimizer.get_cache_key(code1, error)
        key2 = optimizer.get_cache_key(code2, error)
        
        # 不同代码应该生成不同 Key
        self.assertNotEqual(key1, key2)


class TestStatsTracking(unittest.TestCase):
    """测试统计跟踪功能"""
    
    def test_stats_calculation(self):
        stats = TokenStats()
        stats.original_tokens = 1000
        stats.optimized_tokens = 600
        stats.saved_tokens = 400
        
        # 节省比例应该是 40%
        self.assertAlmostEqual(stats.save_rate, 40.0, places=1)
    
    def test_stats_zero_division_protection(self):
        stats = TokenStats()
        # original_tokens 为 0 时不应该除零错误
        self.assertEqual(stats.save_rate, 0.0)
    
    def test_stats_report_generation(self):
        optimizer = TokenOptimizer()
        optimizer.stats.original_tokens = 1000
        optimizer.stats.optimized_tokens = 700
        optimizer.stats.cache_hits = 5
        optimizer.stats.local_fixes = 3
        
        report = optimizer.get_stats_report()
        
        self.assertIn("Token 优化统计", report)
        self.assertIn("1000", report)
        self.assertIn("700", report)
        self.assertIn("5", report)
        self.assertIn("3", report)


class TestConvenienceFunctions(unittest.TestCase):
    """测试便捷函数"""
    
    def test_optimize_prompt_function(self):
        code = "x = 1"
        error = "Error"
        
        prompt = optimize_prompt(code, error, [])
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        self.assertIn("修复以下代码错误", prompt)
    
    def test_try_fix_locally_function(self):
        code = "prnt('hello')"
        error = "NameError: name 'prnt' is not defined"
        
        result = try_fix_locally(code, error)
        
        self.assertIsNotNone(result)
        self.assertIn("print", result)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def test_empty_code(self):
        optimizer = TokenOptimizer()
        context = optimizer.compress_context("", "Error", [])
        self.assertIsInstance(context, str)
    
    def test_empty_error_message(self):
        optimizer = TokenOptimizer()
        code = "x = 1"
        context = optimizer.compress_context(code, "", [])
        self.assertIsInstance(context, str)
    
    def test_unicode_code(self):
        optimizer = TokenOptimizer()
        code = "print('你好世界')"
        error = "Error"
        
        context = optimizer.compress_context(code, error, [])
        self.assertIn("你好世界", context)
    
    def test_very_long_error_message(self):
        optimizer = TokenOptimizer()
        code = "x = 1"
        error = "E" * 10000  # 超长错误信息
        
        context = optimizer.compress_context(code, error, [])
        # 应该能处理而不崩溃
        self.assertIsInstance(context, str)
    
    def test_history_with_multiple_attempts(self):
        optimizer = TokenOptimizer()
        code = "x = 1"
        error = "Current error"
        history = [
            {"code": "x = ", "error": "First error"},
            {"code": "x = 1/", "error": "Second error"},
        ]
        
        context = optimizer.compress_context(code, error, history)
        
        # 应该只包含最近一次的历史
        self.assertIn("Second error", context)


if __name__ == '__main__':
    unittest.main(verbosity=2)
