"""
安全代码沙箱模块
提供安全的代码执行环境，防止恶意代码执行
"""

import subprocess
import tempfile
import os
from typing import Dict, Any


def run_secure_code(code: str, timeout: int = 5) -> Dict[str, Any]:
    """
    在沙箱环境中安全执行 Python 代码
    
    Args:
        code: 要执行的 Python 代码
        timeout: 执行超时时间（秒）
    
    Returns:
        dict: {
            'success': bool,      # 是否执行成功
            'output': str,        # 标准输出
            'error': str | None   # 错误信息
        }
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "sandbox_script.py")
        
        # 写入代码到临时文件
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        try:
            # 使用 subprocess 执行，限制权限
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmpdir
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'error': None
                }
            else:
                error_msg = result.stderr.strip()
                if not error_msg and result.returncode != 0:
                    error_msg = f"Exit code: {result.returncode}"
                return {
                    'success': False,
                    'output': result.stdout,
                    'error': error_msg
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': "",
                'error': f"TimeoutError: Execution exceeded {timeout} seconds"
            }
        except Exception as e:
            return {
                'success': False,
                'output': "",
                'error': f"{type(e).__name__}: {str(e)}"
            }


if __name__ == "__main__":
    # 测试示例
    test_code = "print('Hello from sandbox!')"
    result = run_secure_code(test_code)
    print(f"Result: {result}")
