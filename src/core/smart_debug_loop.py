"""
AI 编程能力提升系统 v2.0 - 智能高效调试循环
核心特性：
1. 本地修复 (Local Fixing): 零 Token 消耗修复常见语法错误
2. 上下文压缩 (Context Compression): 仅发送错误相关代码片段
3. 智能缓存 (Smart Caching): 相同错误直接复用修复方案
4. 实时监控 (Real-time Monitoring): 统计 Token 节省率
"""

import hashlib
import re
import time
import sys
import os

# 添加 ai-dev-system 到路径以导入依赖模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-dev-system'))

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from secure_sandbox import run_secure_code
# 修复导入：使用实际的函数名
try:
    from llm_client import call_llm_real as call_llm
except ImportError:
    # Mock for testing without API key
    def call_llm(prompt: str) -> str:
        return "```python\nprint('Mock response')\n```"

@dataclass
class TokenStats:
    """Token 消耗统计"""
    total_requests: int = 0
    total_tokens_used: int = 0
    local_fixes: int = 0
    cache_hits: int = 0
    compressed_contexts: int = 0
    
    def savings_rate(self) -> float:
        """估算节省率 (假设平均每次请求 500 tokens)"""
        estimated_total = (self.total_requests + self.local_fixes + self.cache_hits) * 500
        if estimated_total == 0:
            return 0.0
        return (1 - (self.total_tokens_used / estimated_total)) * 100

@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: Optional[str]
    code: str
    attempts: int
    token_stats: TokenStats

class LocalFixer:
    """本地语法修复器 (零 Token 消耗)"""
    
    # 预编译正则表达式以提高性能
    FIX_PATTERNS = [
        # 拼写错误 (仅在 SyntaxError 时应用)
        (re.compile(r'\bprnt\s*\(', re.IGNORECASE), 'print('),
        (re.compile(r'\bprin\s*\(', re.IGNORECASE), 'print('),
        (re.compile(r'\bretun\s+', re.IGNORECASE), 'return '),
        (re.compile(r'\bdefen\s+', re.IGNORECASE), 'def '),
        (re.compile(r'\bimport\s+mathh\b', re.IGNORECASE), 'import math'),
    ]
    
    # 需要添加冒号的关键字
    COLON_KEYWORDS = {'if', 'else', 'for', 'while', 'def', 'class', 'elif', 'try', 'except', 'finally', 'with'}
    
    # 预编译关键字匹配正则
    KEYWORD_PATTERN = re.compile(r'^(if|else|for|while|def|class|elif|try|except|finally|with)\s+')
    
    @classmethod
    def try_fix(cls, code: str, error_msg: str) -> Optional[str]:
        """尝试本地修复，成功返回新代码，失败返回 None"""
        original_code = code
        fixed = False
        
        # 判断是否为语法相关错误
        is_syntax_error = any(kw in error_msg for kw in ["SyntaxError", "TabError", "IndentationError"])
        
        if is_syntax_error:
            # 1. 处理缺失冒号
            if "invalid syntax" in error_msg or "expected ':'" in error_msg:
                code, fixed = cls._fix_missing_colons(code)
            
            # 2. 处理 TabError
            if "TabError" in error_msg or "inconsistent use of tabs" in error_msg:
                new_code = code.replace('    \t', '        ')
                if new_code != code:
                    code = new_code
                    fixed = True
            
            # 3. 应用通用拼写错误修复
            code, pattern_fixed = cls._apply_pattern_fixes(code)
            fixed = fixed or pattern_fixed
        else:
            # 非语法错误也尝试拼写错误修复
            code, fixed = cls._apply_pattern_fixes(code)
        
        return code if fixed and code != original_code else None
    
    @classmethod
    def _fix_missing_colons(cls, code: str) -> Tuple[str, bool]:
        """修复缺失的冒号"""
        lines = code.split('\n')
        fixed = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            # 检查是否是关键字开头且缺少冒号
            if cls.KEYWORD_PATTERN.match(stripped) and not stripped.endswith(':'):
                lines[i] = line.rstrip() + ':'
                fixed = True
        
        return '\n'.join(lines), fixed
    
    @classmethod
    def _apply_pattern_fixes(cls, code: str) -> Tuple[str, bool]:
        """应用预定义的正则修复模式"""
        fixed = False
        for pattern, replacement in cls.FIX_PATTERNS:
            new_code = pattern.sub(replacement, code)
            if new_code != code:
                code = new_code
                fixed = True
        return code, fixed

class ContextCompressor:
    """上下文压缩器 (减少 Token 输入)"""
    
    # 预编译正则表达式
    LINE_NUMBER_PATTERN = re.compile(r'line (\d+)', re.IGNORECASE)
    COMMENT_PATTERN = re.compile(r'^\s*#')
    
    @staticmethod
    def compress(code: str, error_msg: str, max_lines: int = 20) -> str:
        """
        压缩代码上下文：
        1. 提取错误行及其周围代码
        2. 移除注释和空行
        3. 限制最大行数
        """
        lines = code.split('\n')
        
        # 尝试从错误消息中提取行号
        line_match = ContextCompressor.LINE_NUMBER_PATTERN.search(error_msg)
        if line_match:
            error_line = int(line_match.group(1)) - 1  # 0-based
            start = max(0, error_line - 3)
            end = min(len(lines), error_line + 4)
            relevant_lines = lines[start:end]
        else:
            # 如果无法提取，取前 N 行
            relevant_lines = lines[:max_lines]
        
        # 移除纯空行和纯注释行 (保留缩进)
        compressed = [
            line for line in relevant_lines 
            if line.strip() and not ContextCompressor.COMMENT_PATTERN.match(line)
        ]
        
        result = '\n'.join(compressed)
        return result if len(compressed) < len(lines) else code

class SmartDebugLoop:
    """智能调试主循环 (v2.0)"""
    
    # 预编译正则表达式用于代码提取
    CODE_BLOCK_PATTERN = re.compile(r'```python\s*(.*?)\s*```', re.DOTALL)
    
    def __init__(self, max_attempts: int = 5, use_cache: bool = True):
        self.max_attempts = max_attempts
        self.use_cache = use_cache
        self.cache: Dict[str, str] = {}  # error_hash -> fixed_code
        self.stats = TokenStats()
        self.local_fixer = LocalFixer()
        self.compressor = ContextCompressor()
    
    def _get_error_hash(self, error: str, code_snippet: str) -> str:
        """生成错误的唯一哈希用于缓存"""
        content = f"{error}|||{code_snippet}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _estimate_tokens(self, text: str) -> int:
        """粗略估算 Token 数 (1 token ≈ 4 chars)"""
        return len(text) >> 2  # 位运算优化除法
    
    def run(self, requirement: str, initial_code: Optional[str] = None) -> ExecutionResult:
        """执行智能调试循环"""
        start_time = time.time()
        code = initial_code or ""
        attempt = 0
        last_error = ""
        
        # 如果没有初始代码，先请求 LLM 生成
        if not code:
            self.stats.total_requests += 1
            prompt = f"Write Python code to: {requirement}"
            response = call_llm(prompt)
            code = self._extract_code(response)
            self.stats.total_tokens_used += self._estimate_tokens(prompt + response)
        
        while attempt < self.max_attempts:
            attempt += 1
            
            # 1. 执行代码
            exec_result = run_secure_code(code, timeout=5)
            
            if exec_result['success']:
                return ExecutionResult(
                    success=True,
                    output=exec_result['output'],
                    error=None,
                    code=code,
                    attempts=attempt,
                    token_stats=self.stats
                )
            
            last_error = exec_result['error']
            
            # 2. 尝试本地修复 (零 Token)
            fixed_code = self.local_fixer.try_fix(code, last_error)
            if fixed_code:
                self.stats.local_fixes += 1
                code = fixed_code
                continue  # 跳过 LLM，直接重试
            
            # 3. 检查缓存 (零 Token)
            if self.use_cache:
                snippet = self.compressor.compress(code, last_error)
                cache_key = self._get_error_hash(last_error, snippet)
                if cache_key in self.cache:
                    self.stats.cache_hits += 1
                    code = self.cache[cache_key]
                    continue
            
            # 4. 准备 LLM 请求 (使用压缩上下文)
            compressed_code = self.compressor.compress(code, last_error)
            compression_ratio = 1 - (len(compressed_code) / len(code)) if code else 0
            
            if compression_ratio > 0.1:  # 压缩超过 10% 才记录
                self.stats.compressed_contexts += 1
            
            self.stats.total_requests += 1
            prompt = (
                f"Fix the error in this code.\n"
                f"Requirement: {requirement}\n"
                f"Code:\n{compressed_code}\n"
                f"Error: {last_error}\n"
                f"Return ONLY the fixed code."
            )
            
            response = call_llm(prompt)
            new_code = self._extract_code(response)
            
            # 更新统计
            self.stats.total_tokens_used += self._estimate_tokens(prompt + response)
            
            # 更新缓存 - 使用原始错误和代码生成 key，这样下次相同错误能命中
            if self.use_cache and new_code != code:
                cache_key = self._get_error_hash(last_error, compressed_code)
                self.cache[cache_key] = new_code
            
            code = new_code
        
        # 达到最大尝试次数
        return ExecutionResult(
            success=False,
            output="",
            error=last_error,
            code=code,
            attempts=attempt,
            token_stats=self.stats
        )
    
    def _extract_code(self, text: str) -> str:
        """从 LLM 响应中提取代码块"""
        match = self.CODE_BLOCK_PATTERN.search(text)
        return match.group(1).strip() if match else text.strip()
    
    def get_stats_report(self) -> str:
        """生成 Token 节省报告"""
        s = self.stats
        return f"""
=== Token 优化报告 ===
总 LLM 请求数: {s.total_requests}
总 Token 消耗: {s.total_tokens_used}
本地修复次数: {s.local_fixes} (节省 ~{s.local_fixes * 500} tokens)
缓存命中次数: {s.cache_hits} (节省 ~{s.cache_hits * 500} tokens)
上下文压缩次数: {s.compressed_contexts}
估算节省率: {s.savings_rate():.1f}%
=====================
"""

# 便捷函数
def run_smart_debug(requirement: str, initial_code: Optional[str] = None) -> ExecutionResult:
    loop = SmartDebugLoop()
    return loop.run(requirement, initial_code)

if __name__ == "__main__":
    # 演示用例
    print("🚀 启动 AI 编程系统 v2.0 (Token 优化版)")
    
    # 测试 1: 本地修复 (SyntaxError)
    print("\n[Test 1] 测试本地修复 (缺失冒号)...")
    bad_code = "def hello()\n    print('Hi')"
    result = run_smart_debug("Say hi", bad_code)
    print(f"结果: {'✅ 成功' if result.success else '❌ 失败'}")
    print(f"尝试次数: {result.attempts}")
    print(f"本地修复: {result.token_stats.local_fixes} 次")
    loop = SmartDebugLoop(); print(loop.get_stats_report())
    
    # 测试 2: 缓存命中
    print("\n[Test 2] 测试缓存命中...")
    # 再次运行相同的错误代码
    result2 = run_smart_debug("Say hi", bad_code)
    print(f"结果: {'✅ 成功' if result2.success else '❌ 失败'}")
    print(f"缓存命中: {result2.token_stats.cache_hits} 次")
    loop2 = SmartDebugLoop(); print(loop2.get_stats_report())
