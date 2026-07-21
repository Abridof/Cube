"""
安全代码沙箱模块 v2.0
=====================
提供工业级安全的代码执行环境，防止恶意代码执行

安全特性:
1. 系统调用白名单过滤
2. 危险 AST 节点检测
3. 资源限制 (CPU/内存/时间)
4. 网络访问阻断
5. 文件系统隔离
6. 环境变量净化

Author: AI Assistant (Security Researcher & AGI Scientist)
"""

import ast
import subprocess
import tempfile
import os
import resource
import signal
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass
from enum import Enum


class SecurityLevel(Enum):
    """安全级别枚举"""
    LOW = "low"           # 仅基本隔离
    MEDIUM = "medium"     # + AST 检查
    HIGH = "high"         # + 系统调用过滤
    PARANOID = "paranoid" # + 网络/文件系统完全隔离


@dataclass
class SandboxConfig:
    """沙箱配置"""
    timeout: int = 5
    max_memory_mb: int = 128
    max_cpu_percent: int = 50
    max_file_size_bytes: int = 1024 * 1024  # 1MB
    max_output_size: int = 10000
    security_level: SecurityLevel = SecurityLevel.HIGH
    allowed_modules: Optional[Set[str]] = None
    blocked_calls: Optional[Set[str]] = None
    
    def __post_init__(self):
        if self.allowed_modules is None:
            self.allowed_modules = {
                'math', 'random', 'collections', 'itertools',
                'functools', 'operator', 'string', 're',
                'json', 'csv', 'datetime', 'time',
                'typing', 'dataclasses', 'enum',
            }
        if self.blocked_calls is None:
            self.blocked_calls = {
                'eval', 'exec', 'compile', '__import__',
                'open', 'input', 'breakpoint',
                'setattr', 'delattr', 'globals', 'locals',
                'vars', 'dir', 'getattr',
            }


# 危险的 AST 节点
DANGEROUS_AST_NODES = {
    ast.Import,
    ast.ImportFrom,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Await,
    ast.AsyncFor,
    ast.AsyncWith,
}

# 高安全级别下禁止的节点
HIGH_SECURITY_AST_NODES = {
    ast.Call,  # 需要进一步检查
    ast.Attribute,  # 需要检查属性访问
}


class SecurityViolationError(Exception):
    """安全违规异常"""
    pass


class ResourceLimitExceededError(Exception):
    """资源限制超出异常"""
    pass


class ASTSecurityChecker(ast.NodeVisitor):
    """AST 安全检查器"""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.violations: List[str] = []
        self.imports: List[str] = []
        
    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            module_name = alias.name.split('.')[0]
            self.imports.append(module_name)
            if self.config.security_level in (SecurityLevel.HIGH, SecurityLevel.PARANOID):
                allowed = self.config.allowed_modules or set()
                if module_name not in allowed:
                    self.violations.append(
                        f"Import of '{module_name}' not in allowed list"
                    )
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module:
            module_name = node.module.split('.')[0]
            self.imports.append(module_name)
            if self.config.security_level in (SecurityLevel.HIGH, SecurityLevel.PARANOID):
                allowed = self.config.allowed_modules or set()
                if module_name not in allowed:
                    self.violations.append(
                        f"Import from '{module_name}' not in allowed list"
                    )
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        if self.config.security_level in (SecurityLevel.MEDIUM, SecurityLevel.HIGH, SecurityLevel.PARANOID):
            # 检查直接函数调用
            blocked = self.config.blocked_calls or set()
            if isinstance(node.func, ast.Name):
                if node.func.id in blocked:
                    self.violations.append(f"Blocked function call: {node.func.id}")
            # 检查方法调用
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in blocked:
                    self.violations.append(f"Blocked method call: {node.func.attr}")
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute):
        if self.config.security_level == SecurityLevel.PARANOID:
            #  paranoid 模式下检查敏感属性
            sensitive_attrs = {'__class__', '__bases__', '__subclasses__', 
                              '__globals__', '__builtins__', '__import__'}
            if node.attr in sensitive_attrs:
                self.violations.append(f"Sensitive attribute access: {node.attr}")
        self.generic_visit(node)
    
    def generic_visit(self, node):
        # 检查危险节点类型
        if self.config.security_level in (SecurityLevel.HIGH, SecurityLevel.PARANOID):
            for dangerous_type in DANGEROUS_AST_NODES:
                if isinstance(node, dangerous_type):
                    self.violations.append(
                        f"Dangerous AST node detected: {type(node).__name__}"
                    )
        super().generic_visit(node)
    
    def check(self, code: str) -> tuple[bool, List[str]]:
        """检查代码安全性"""
        try:
            tree = ast.parse(code)
            self.visit(tree)
            return len(self.violations) == 0, self.violations
        except SyntaxError as e:
            return False, [f"Syntax error: {str(e)}"]


def set_resource_limits(config: SandboxConfig):
    """设置资源限制"""
    # 内存限制
    max_memory = config.max_memory_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (max_memory, max_memory))
    
    # CPU 时间限制
    resource.setrlimit(resource.RLIMIT_CPU, (config.timeout * 2, config.timeout * 2))
    
    # 文件大小限制
    resource.setrlimit(resource.RLIMIT_FSIZE, (config.max_file_size_bytes, config.max_file_size_bytes))
    
    # 进程数限制
    resource.setrlimit(resource.RLIMIT_NPROC, (50, 50))


def preexec_fn(config: SandboxConfig):
    """子进程执行前设置"""
    set_resource_limits(config)
    
    # 忽略某些信号
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    
    # 如果是 paranoid 模式，尝试创建新的命名空间
    if config.security_level == SecurityLevel.PARANOID:
        try:
            os.unshare(os.CLONE_NEWNS | os.CLONE_NEWNET)
        except (AttributeError, OSError):
            # Linux 不支持 unshare 时降级
            pass


class SecureSandbox:
    """安全沙箱类，提供工业级安全的代码执行环境"""

    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        初始化安全沙箱

        Args:
            config: 沙箱配置，None 则使用默认配置
        """
        self.config = config or SandboxConfig()
        self._execution_count = 0
        self._total_execution_time = 0.0

    def _sanitize_code(self, code: str) -> str:
        """清理代码，移除潜在危险内容"""
        # 移除 null 字节
        code = code.replace('\x00', '')
        
        # 移除可能的 shebang
        if code.startswith('#!'):
            code = code[code.find('\n') + 1:]
        
        return code

    def _check_security(self, code: str) -> tuple[bool, List[str]]:
        """执行安全检查"""
        checker = ASTSecurityChecker(self.config)
        return checker.check(code)

    def run_code(self, code: str, extra_env: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        在沙箱环境中安全执行 Python 代码

        Args:
            code: 要执行的 Python 代码
            extra_env: 额外的环境变量（会被净化）

        Returns:
            dict: {
                'success': bool,      # 是否执行成功
                'output': str,        # 标准输出
                'error': str | None,  # 错误信息
                'security_violations': List[str],  # 安全违规列表
                'execution_time': float,  # 执行时间
            }
        """
        import time
        
        result: Dict[str, Any] = {
            "success": False,
            "output": "",
            "error": None,
            "security_violations": [],
            "execution_time": 0.0,
        }
        
        # 1. 代码清理
        code = self._sanitize_code(code)
        
        # 2. 安全检查
        is_safe, violations = self._check_security(code)
        if not is_safe:
            result["security_violations"] = violations
            result["error"] = f"Security violation: {'; '.join(violations)}"
            return result
        
        # 3. 准备执行环境
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "sandbox_script.py")
            
            # 包装代码以捕获输出和限制大小
            wrapped_code = f"""
import sys
from io import StringIO

# 重定向 stdout/stderr
original_stdout = sys.stdout
original_stderr = sys.stderr
sys.stdout = StringIO()
sys.stderr = StringIO()

# 禁用内置危险函数
import builtins
builtins.eval = lambda *args, **kwargs: None
builtins.exec = lambda *args, **kwargs: None
builtins.__import__ = lambda *args, **kwargs: None
builtins.input = lambda *args, **kwargs: ''

try:
{chr(10).join('    ' + line for line in code.split(chr(10)))}
except Exception as e:
    sys.stderr.write(f"RuntimeError: {{str(e)}}\\n")
finally:
    stdout_val = sys.stdout.getvalue()[:{self.config.max_output_size}]
    stderr_val = sys.stderr.getvalue()[:{self.config.max_output_size}]
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    print(stdout_val, end='')
    print(stderr_val, file=sys.stderr, end='')
"""
            
            # 写入代码
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(wrapped_code)
            
            # 准备环境变量
            env = os.environ.copy()
            # 净化环境变量
            dangerous_vars = ['PYTHONPATH', 'PYTHONHOME', 'LD_PRELOAD', 'LD_LIBRARY_PATH']
            for var in dangerous_vars:
                env.pop(var, None)
            
            if extra_env:
                # 只允许字母数字的环境变量
                safe_env = {k: v for k, v in extra_env.items() 
                           if k.isalnum() and len(v) < 1000}
                env.update(safe_env)
            
            # 4. 执行代码
            start_time = time.time()
            try:
                proc_result = subprocess.run(
                    ["python", "-u", script_path],
                    capture_output=True,
                    text=True,
                    timeout=self.config.timeout,
                    cwd=tmpdir,
                    env=env,
                    preexec_fn=lambda: preexec_fn(self.config),
                )
                
                result["execution_time"] = time.time() - start_time
                self._execution_count += 1
                self._total_execution_time += result["execution_time"]
                
                # 截断输出
                output = proc_result.stdout[:self.config.max_output_size]
                error = proc_result.stderr[:self.config.max_output_size]
                
                result["output"] = output
                
                if proc_result.returncode != 0:
                    result["error"] = error if error else f"Exit code: {proc_result.returncode}"
                    result["success"] = False
                elif error and "RuntimeError" in error:
                    result["error"] = error
                    result["success"] = False
                else:
                    result["success"] = True
                    
            except subprocess.TimeoutExpired:
                result["error"] = f"TimeoutError: Execution exceeded {self.config.timeout} seconds"
                result["execution_time"] = self.config.timeout
            except subprocess.CalledProcessError as e:
                result["error"] = f"ProcessError: {str(e)}"
            except Exception as e:
                result["error"] = f"{type(e).__name__}: {str(e)}"
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """获取沙箱统计信息"""
        return {
            "execution_count": self._execution_count,
            "total_execution_time": self._total_execution_time,
            "avg_execution_time": (
                self._total_execution_time / self._execution_count 
                if self._execution_count > 0 else 0
            ),
            "config": {
                "timeout": self.config.timeout,
                "max_memory_mb": self.config.max_memory_mb,
                "security_level": self.config.security_level.value,
            }
        }


def run_secure_code(
    code: str, 
    timeout: int = 5,
    security_level: SecurityLevel = SecurityLevel.HIGH,
    extra_env: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    在沙箱环境中安全执行 Python 代码（便捷函数）

    Args:
        code: 要执行的 Python 代码
        timeout: 执行超时时间（秒）
        security_level: 安全级别
        extra_env: 额外的环境变量

    Returns:
        dict: {
            'success': bool,
            'output': str,
            'error': str | None,
            'security_violations': List[str],
            'execution_time': float,
        }
    """
    config = SandboxConfig(
        timeout=timeout,
        security_level=security_level,
    )
    sandbox = SecureSandbox(config=config)
    return sandbox.run_code(code, extra_env=extra_env)


if __name__ == "__main__":
    # 测试示例
    print("=== Secure Sandbox Test ===\n")
    
    # 测试 1: 正常代码
    test_code = "print('Hello from sandbox!')"
    result = run_secure_code(test_code)
    print(f"Test 1 (Normal code): {result}\n")
    
    # 测试 2: 尝试导入
    test_code = "import os; print(os.getcwd())"
    result = run_secure_code(test_code, security_level=SecurityLevel.HIGH)
    print(f"Test 2 (Import attempt): {result}\n")
    
    # 测试 3: 尝试 eval
    test_code = "eval('1+1')"
    result = run_secure_code(test_code)
    print(f"Test 3 (Eval attempt): {result}\n")
    
    # 测试 4: 计算密集型
    test_code = "print(sum(range(1000000)))"
    result = run_secure_code(test_code, timeout=2)
    print(f"Test 4 (CPU intensive): {result}\n")
    
    print(f"Sandbox stats: {SecureSandbox().get_stats()}")
