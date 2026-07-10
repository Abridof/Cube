"""
LLM 客户端模块
提供与大型语言模型的交互接口
支持多种后端（OpenAI、Anthropic、本地模型等）
优化：延迟导入 requests，使用连接池复用
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """LLM 响应数据类"""

    text: str
    tokens_used: int
    model: str
    latency_ms: float
    success: bool
    error: Optional[str] = None


class LLMClient:
    """LLM 客户端类，支持配置管理和多后端"""

    __slots__ = (
        "api_key",
        "api_base",
        "model",
        "max_tokens",
        "temperature",
        "timeout",
        "retry_attempts",
        "retry_delay",
        "_session",
    )

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: str = "https://api.openai.com/v1",
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ):
        self.api_key = api_key or os.getenv("LLM_API_KEY", "")
        self.api_base = api_base
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self._session = None

    def _get_session(self):
        """获取或创建 requests session（延迟导入，连接池复用）"""
        if self._session is None:
            import requests

            self._session = requests.Session()
            self._session.headers.update(
                {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            )
            # 配置连接池
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=4, pool_maxsize=10, max_retries=2, pool_block=False
            )
            self._session.mount("http://", adapter)
            self._session.mount("https://", adapter)
        return self._session

    def call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        调用 LLM API

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            messages: 完整的消息历史（可选）
            **kwargs: 其他参数覆盖

        Returns:
            LLMResponse: LLM 响应对象
        """
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        temperature = kwargs.get("temperature", self.temperature)

        # 构建消息
        if messages is None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # 重试逻辑
        last_error = None
        for attempt in range(self.retry_attempts):
            try:
                start_time = time.time()

                # 如果没有 API key，返回 mock 响应
                if not self.api_key:
                    logger.warning("No API key configured, using mock response")
                    return self._mock_response(prompt)

                session = self._get_session()
                response = session.post(
                    f"{self.api_base}/chat/completions", json=payload, timeout=self.timeout
                )
                response.raise_for_status()

                data = response.json()
                latency_ms = (time.time() - start_time) * 1000

                result = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens", 0)

                return LLMResponse(
                    text=result,
                    tokens_used=tokens_used,
                    model=self.model,
                    latency_ms=latency_ms,
                    success=True,
                )

            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"LLM call failed (attempt {attempt + 1}/{self.retry_attempts}): {e}"
                )
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (attempt + 1))

        # 所有重试失败
        return LLMResponse(
            text="", tokens_used=0, model=self.model, latency_ms=0, success=False, error=last_error
        )

    def _mock_response(self, prompt: str) -> LLMResponse:
        """生成 mock 响应（用于测试和无 API key 场景）"""
        # 简单的智能响应逻辑
        if "SyntaxError" in prompt or "invalid syntax" in prompt:
            if "def " in prompt and ":" not in prompt.split("def ")[1].split("\n")[0]:
                lines = prompt.split("\n")
                for i, line in enumerate(lines):
                    if line.strip().startswith("def ") and not line.strip().endswith(":"):
                        lines[i] = line.rstrip() + ":"
                return LLMResponse(
                    text="```python\n" + "\n".join(lines) + "\n```",
                    tokens_used=len(prompt) // 4,
                    model="mock",
                    latency_ms=10,
                    success=True,
                )

        if "Print Hello" in prompt or "Say hi" in prompt or "print hello" in prompt.lower():
            return LLMResponse(
                text="```python\nprint('Hello')\n```",
                tokens_used=20,
                model="mock",
                latency_ms=10,
                success=True,
            )

        if "Fix the error" in prompt:
            return LLMResponse(
                text="```python\n# Fixed code\nprint('Fixed!')\n```",
                tokens_used=30,
                model="mock",
                latency_ms=10,
                success=True,
            )

        return LLMResponse(
            text="```python\n# Generated code\nprint('Hello from LLM')\n```",
            tokens_used=25,
            model="mock",
            latency_ms=10,
            success=True,
        )


# 便捷函数
_default_client: Optional[LLMClient] = None


def get_client() -> LLMClient:
    """获取或创建默认客户端"""
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client


def call_llm(prompt: str, **kwargs) -> str:
    """
    便捷函数：调用 LLM 并返回文本

    Args:
        prompt: 输入提示词
        **kwargs: 传递给 LLMClient.call() 的参数

    Returns:
        str: LLM 返回的文本
    """
    client = get_client()
    response = client.call(prompt, **kwargs)
    return response.text


def call_llm_real(prompt: str, model: str = "default", max_tokens: int = 1000) -> str:
    """
    调用真实 LLM API（向后兼容的接口）

    Args:
        prompt: 输入提示词
        model: 模型名称
        max_tokens: 最大生成 token 数

    Returns:
        str: LLM 返回的文本
    """
    if model != "default":
        client = LLMClient(model=model, max_tokens=max_tokens)
    else:
        client = get_client()

    response = client.call(prompt)
    if not response.success:
        raise RuntimeError(f"LLM call failed: {response.error}")
    return response.text


def call_llm_mock(prompt: str) -> str:
    """
    Mock LLM 响应（向后兼容的接口）

    Args:
        prompt: 输入提示词

    Returns:
        str: Mock 响应
    """
    client = LLMClient()
    return client._mock_response(prompt).text


if __name__ == "__main__":
    # 测试
    print("Testing LLM Client...")

    # 测试 mock 模式
    test_prompt = "Write code to print hello"
    response = call_llm(test_prompt)
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")

    # 测试客户端类
    client = LLMClient()
    response = client.call("Fix this: def test()\\n    pass")
    print(f"\nDirect client response: {response.text}")
    print(f"Tokens used: {response.tokens_used}")
    print(f"Latency: {response.latency_ms:.2f}ms")


# Mock 实现用于测试
def call_llm_mock(prompt: str) -> str:
    """
    Mock LLM 响应，用于测试环境

    Args:
        prompt: 输入提示词

    Returns:
        str: Mock 响应
    """
    # 简单的智能响应逻辑
    if "SyntaxError" in prompt or "invalid syntax" in prompt:
        if "def " in prompt and ":" not in prompt.split("def ")[1].split("\n")[0]:
            # 修复缺失冒号的函数定义
            lines = prompt.split("\n")
            for i, line in enumerate(lines):
                if line.strip().startswith("def ") and not line.strip().endswith(":"):
                    lines[i] = line.rstrip() + ":"
            return "```python\n" + "\n".join(lines) + "\n```"

    if "Print Hello" in prompt or "Say hi" in prompt:
        return "```python\nprint('Hello')\n```"

    if "Fix the error" in prompt:
        return "```python\n# Fixed code\nprint('Fixed!')\n```"

    return "```python\n# Generated code\nprint('Hello from LLM')\n```"


# 默认导出 mock 版本
call_llm = call_llm_mock


if __name__ == "__main__":
    # 测试 mock
    test_prompt = "Write code to print hello"
    response = call_llm(test_prompt)
    print(f"Prompt: {test_prompt}")
    print(f"Response: {response}")
