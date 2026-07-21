"""
Token 优化模块
专为降低 LLM 调用成本设计，提供上下文压缩、增量提示、本地预检等策略
"""

import re
import hashlib
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class TokenStats:
    """Token 使用统计"""

    original_tokens: int = 0
    optimized_tokens: int = 0
    saved_tokens: int = 0
    cache_hits: int = 0
    local_fixes: int = 0

    @property
    def save_rate(self) -> float:
        if self.original_tokens == 0:
            return 0.0
        return (self.original_tokens - self.optimized_tokens) / self.original_tokens * 100


class TokenOptimizer:
    """
    Token 优化器
    策略：
    1. 上下文压缩：只保留关键错误信息
    2. 增量更新：只发送变更部分
    3. 本地预检：尝试零成本修复简单错误
    4. 响应格式约束：要求 LLM 输出紧凑格式
    """

    def __init__(self, max_context_lines: int = 50, enable_cache: bool = True):
        self.max_context_lines = max_context_lines
        self.enable_cache = enable_cache
        self.cache: Dict[str, str] = {}  # error_hash -> fix_suggestion
        self.stats = TokenStats()

        # 常见简单错误的本地修复规则 (零 Token 消耗)
        self.local_fix_rules = [
            # 规则：(错误模式正则, 修复函数)
            (r"IndentationError", self._fix_indentation),
            (r"NameError: name '(\w+)' is not defined", self._check_typo),
            (r"SyntaxError: invalid syntax", self._check_syntax_common),
        ]

    def estimate_tokens(self, text: str) -> int:
        """粗略估算 Token 数 (英文: 1 token ≈ 4 chars, 中文: 1 token ≈ 1.5 chars)"""
        # 简化估算：按字符数除以 4 (对于混合文本通常偏保守)
        return len(text) // 4 + 10

    def try_local_fix(self, code: str, error_message: str) -> Optional[str]:
        """
        尝试本地修复简单错误 (零 Token 消耗)
        返回修复后的代码，如果无法本地修复则返回 None
        """
        for pattern, fix_func in self.local_fix_rules:
            if re.search(pattern, error_message, re.IGNORECASE):
                fixed_code = fix_func(code, error_message)
                if fixed_code:
                    self.stats.local_fixes += 1
                    return fixed_code
        return None

    def _fix_indentation(self, code: str, error: str) -> Optional[str]:
        """简单缩进修复：统一转为 4 空格"""
        # 这里只做最基础的检测，复杂缩进需 LLM
        lines = code.split("\n")
        fixed_lines = []
        for line in lines:
            # 将 tab 转为 4 空格
            if "\t" in line:
                fixed_lines.append(line.replace("\t", "    "))
            else:
                fixed_lines.append(line)

        fixed_code = "\n".join(fixed_lines)
        if fixed_code != code:
            return fixed_code
        return None

    def _check_typo(self, code: str, error: str) -> Optional[str]:
        """检查常见拼写错误 (如 print 写成 prnt)"""
        match = re.search(r"name '(\w+)' is not defined", error)
        if match:
            undefined_var = match.group(1)
            # 常见拼写映射
            typos = {"prnt": "print", "retrun": "return", "funtion": "function", "impor": "import"}
            if undefined_var in typos:
                correct_name = typos[undefined_var]
                return code.replace(undefined_var, correct_name)
        return None

    def _check_syntax_common(self, code: str, error: str) -> Optional[str]:
        """检查常见语法错误 (如缺少冒号)"""
        # 简单规则：如果报错行末尾缺少冒号且上一行是 def/if/for/while
        lines = code.split("\n")
        # 解析错误行号 (假设错误信息包含 "line X")
        line_match = re.search(r"line (\d+)", error)
        if line_match:
            line_num = int(line_match.group(1)) - 1
            if 0 <= line_num < len(lines):
                line = lines[line_num].strip()
                # 检查是否缺少冒号
                if line and not line.endswith(":") and not line.endswith("#"):
                    # 检查是否是定义语句
                    if re.match(
                        r"^(def|class|if|elif|else|for|while|try|except|finally|with)\b", line
                    ):
                        lines[line_num] = lines[line_num].rstrip() + ":"
                        self.stats.local_fixes += 1
                        return "\n".join(lines)
        return None

    def compress_context(self, code: str, error_message: str, history: List[Dict]) -> str:
        """
        压缩上下文：
        1. 只保留错误相关代码片段 (前后各 5 行)
        2. 截断过长的历史对话
        3. 移除冗余的系统提示
        """
        # 1. 提取错误相关代码片段
        error_context = self._extract_error_context(code, error_message)

        # 2. 构建精简 Prompt
        prompt_parts = []
        prompt_parts.append("### 任务\n修复以下代码错误。只输出修复后的完整代码，不要解释。")

        prompt_parts.append(f"\n### 错误信息\n{error_message}")

        prompt_parts.append(f"\n### 相关代码片段\n{error_context}")

        # 3. 如果有历史尝试，只保留最近一次的失败代码和错误 (增量式)
        if history:
            last_attempt = history[-1]
            prompt_parts.append(f"\n### 上一次尝试的错误\n{last_attempt.get('error', 'Unknown')}")
            # 不重复发送完整代码，因为上面已经发了当前代码

        compressed_prompt = "\n".join(prompt_parts)

        # 统计
        original_len = len(code) + sum(len(str(h)) for h in history) + len(error_message)
        self.stats.original_tokens += self.estimate_tokens(str(original_len))
        self.stats.optimized_tokens += self.estimate_tokens(compressed_prompt)
        self.stats.saved_tokens += self.stats.original_tokens - self.stats.optimized_tokens

        return compressed_prompt

    def _extract_error_context(self, code: str, error_message: str) -> str:
        """提取错误发生位置及其上下文的代码片段"""
        lines = code.split("\n")
        total_lines = len(lines)

        # 尝试从错误信息中提取行号
        line_match = re.search(r"line (\d+)", error_message)
        if line_match:
            error_line = int(line_match.group(1)) - 1  # 0-indexed
            start = max(0, error_line - 5)
            end = min(total_lines, error_line + 6)

            context_lines = lines[start:end]
            # 添加行号标记
            marked_lines = []
            for i, line in enumerate(context_lines):
                actual_line_num = start + i + 1
                marker = ">>> " if actual_line_num == error_line + 1 else "    "
                marked_lines.append(f"{marker}{actual_line_num}: {line}")

            return "\n".join(marked_lines)

        # 如果无法提取行号，返回代码开头和结尾 (最多 max_context_lines 行)
        if total_lines > self.max_context_lines:
            head = lines[: self.max_context_lines // 2]
            tail = lines[-self.max_context_lines // 2 :]
            return "\n".join(head + ["... (省略中间部分) ..."] + tail)

        return code

    def get_cache_key(self, code: str, error_message: str) -> str:
        """生成缓存 Key"""
        content = f"{code}|||{error_message}"
        return hashlib.sha256(content.encode()).hexdigest()

    def check_cache(self, code: str, error_message: str) -> Optional[str]:
        """检查缓存中是否有修复方案"""
        if not self.enable_cache:
            return None

        key = self.get_cache_key(code, error_message)
        if key in self.cache:
            self.stats.cache_hits += 1
            return self.cache[key]
        return None

    def save_to_cache(self, code: str, error_message: str, fix: str):
        """保存修复方案到缓存"""
        if not self.enable_cache:
            return
        key = self.get_cache_key(code, error_message)
        self.cache[key] = fix

    def format_response_prompt(self) -> str:
        """生成要求 LLM 紧凑输出的指令"""
        return (
            "\n\n### 输出要求\n"
            "1. 只输出修复后的完整 Python 代码。\n"
            "2. 不要包含 markdown 代码块标记 (```python)。\n"
            "3. 不要输出任何解释、注释或额外文本。\n"
            "4. 确保代码可以直接运行。"
        )

    def get_stats_report(self) -> str:
        """生成 Token 节省报告"""
        return (
            f"=== Token 优化统计 ===\n"
            f"原始预估 Token: {self.stats.original_tokens}\n"
            f"优化后 Token:   {self.stats.optimized_tokens}\n"
            f"节省 Token:     {self.stats.saved_tokens}\n"
            f"节省比例:       {self.stats.save_rate:.2f}%\n"
            f"缓存命中次数:   {self.stats.cache_hits}\n"
            f"本地修复次数:   {self.stats.local_fixes}\n"
        )


# 便捷函数
def optimize_prompt(code: str, error: str, history: Optional[List[Dict]] = None) -> str:
    """快速生成优化后的 Prompt"""
    optimizer = TokenOptimizer()
    return (
        optimizer.compress_context(code, error, history or []) + optimizer.format_response_prompt()
    )


def try_fix_locally(code: str, error: str) -> Optional[str]:
    """快速尝试本地修复"""
    optimizer = TokenOptimizer()
    return optimizer.try_local_fix(code, error)
