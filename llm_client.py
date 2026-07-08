"""
LLM 客户端模块
提供与大型语言模型的交互接口
"""

from typing import Optional


def call_llm_real(prompt: str, model: str = "default", max_tokens: int = 1000) -> str:
    """
    调用真实 LLM API
    
    Args:
        prompt: 输入提示词
        model: 模型名称
        max_tokens: 最大生成 token 数
    
    Returns:
        str: LLM 返回的文本
    
    Note:
        实际使用时需要配置 API key 和端点
        当前为占位实现
    """
    # TODO: 实现真实的 LLM API 调用
    # 示例结构：
    # import requests
    # response = requests.post(
    #     API_ENDPOINT,
    #     headers={"Authorization": f"Bearer {API_KEY}"},
    #     json={"model": model, "prompt": prompt, "max_tokens": max_tokens}
    # )
    # return response.json()["choices"][0]["text"]
    
    raise NotImplementedError(
        "Real LLM client not configured. "
        "Please set up API credentials or use mock for testing."
    )


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
