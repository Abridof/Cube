"""
CLI 工具模块 v1.0
==================
提供命令行接口，方便用户与认知引擎交互

功能特性:
1. 交互式 REPL 模式
2. 批量任务处理
3. 系统状态监控
4. 配置管理
5. 日志查看

Author: AI Assistant (DevOps Engineer)
"""

import argparse
import sys
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
import readline  # 用于命令行历史

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import EngineConfig
from modules.system_orchestrator import SystemOrchestrator
from services.rate_limiter import RateLimiter, create_rate_limiter


class CLIColors:
    """ANSI 颜色代码"""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"


def print_colored(text: str, color: str = CLIColors.RESET, bold: bool = False):
    """打印彩色文本"""
    prefix = CLIColors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{CLIColors.RESET}")


class CognitiveEngineCLI:
    """认知引擎命令行接口"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化 CLI
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.orchestrator: Optional[SystemOrchestrator] = None
        self.rate_limiter = create_rate_limiter(
            max_requests=60,
            window_seconds=60.0,
            burst_size=10
        )
        self.history: list = []
        self.verbose = False
    
    def _load_config(self) -> EngineConfig:
        """加载配置"""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config_dict = json.load(f)
            return EngineConfig(**config_dict)
        return EngineConfig()
    
    def initialize_engine(self):
        """初始化认知引擎"""
        print_colored("Initializing Cognitive Engine...", CLIColors.CYAN, bold=True)
        try:
            self.orchestrator = SystemOrchestrator(config=self.config)
            print_colored("✓ Engine initialized successfully", CLIColors.GREEN)
        except Exception as e:
            print_colored(f"✗ Failed to initialize engine: {e}", CLIColors.RED)
            self.orchestrator = None
    
    def cmd_help(self, args):
        """显示帮助信息"""
        help_text = """
Cognitive Engine CLI - Available Commands:
==========================================

Core Commands:
  init              Initialize the cognitive engine
  think <query>     Process a query through the cognition loop
  learn <data>      Learn new knowledge from data
  reason <problem>  Perform reasoning on a problem
  act <action>      Execute an action

System Commands:
  status            Show system status and metrics
  config            Show current configuration
  memory            Query the knowledge graph
  logs [level]      Show recent logs

Session Commands:
  history           Show command history
  clear             Clear the screen
  verbose [on|off]  Toggle verbose mode
  quit/exit         Exit the CLI

Examples:
  > think What is the capital of France?
  > learn {"concept": "gravity", "definition": "..."}
  > reason If A causes B and B causes C, what is the relation between A and C?
  > status
"""
        print(help_text)
    
    def cmd_init(self, args):
        """初始化引擎"""
        self.initialize_engine()
    
    def cmd_think(self, args):
        """处理思考请求"""
        if not self.orchestrator:
            print_colored("Error: Engine not initialized. Run 'init' first.", CLIColors.RED)
            return
        
        query = ' '.join(args)
        if not query:
            print_colored("Error: Please provide a query.", CLIColors.YELLOW)
            return
        
        # 速率限制检查
        allowed, info = self.rate_limiter.allow_request("cli_user")
        if not allowed:
            retry_after = info.get('retry_after', 1.0)
            print_colored(
                f"Rate limit exceeded. Please wait {retry_after:.1f} seconds.",
                CLIColors.YELLOW
            )
            return
        
        print_colored("Thinking...", CLIColors.CYAN)
        try:
            result = self.orchestrator.process_query(query)
            print_colored("\nResult:", CLIColors.GREEN, bold=True)
            if isinstance(result, dict):
                print(json.dumps(result, indent=2))
            else:
                print(str(result))
            
            self.history.append({
                "type": "think",
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "success": True
            })
        except Exception as e:
            print_colored(f"Error: {e}", CLIColors.RED)
            self.history.append({
                "type": "think",
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            })
    
    def cmd_learn(self, args):
        """学习新知识"""
        if not self.orchestrator:
            print_colored("Error: Engine not initialized. Run 'init' first.", CLIColors.RED)
            return
        
        data_str = ' '.join(args)
        if not data_str:
            print_colored("Error: Please provide data to learn.", CLIColors.YELLOW)
            return
        
        try:
            # 尝试解析 JSON
            if data_str.startswith('{'):
                data = json.loads(data_str)
            else:
                data = {"text": data_str}
            
            print_colored("Learning...", CLIColors.CYAN)
            result = self.orchestrator.learn(data)
            print_colored("✓ Learning complete", CLIColors.GREEN)
            if self.verbose:
                print(json.dumps(result, indent=2))
        except json.JSONDecodeError as e:
            print_colored(f"Error: Invalid JSON format - {e}", CLIColors.RED)
        except Exception as e:
            print_colored(f"Error: {e}", CLIColors.RED)
    
    def cmd_reason(self, args):
        """执行推理"""
        if not self.orchestrator:
            print_colored("Error: Engine not initialized. Run 'init' first.", CLIColors.RED)
            return
        
        problem = ' '.join(args)
        if not problem:
            print_colored("Error: Please provide a problem to reason about.", CLIColors.YELLOW)
            return
        
        print_colored("Reasoning...", CLIColors.CYAN)
        try:
            result = self.orchestrator.reason(problem)
            print_colored("\nConclusion:", CLIColors.GREEN, bold=True)
            if isinstance(result, dict):
                print(json.dumps(result, indent=2))
            else:
                print(str(result))
        except Exception as e:
            print_colored(f"Error: {e}", CLIColors.RED)
    
    def cmd_act(self, args):
        """执行动作"""
        if not self.orchestrator:
            print_colored("Error: Engine not initialized. Run 'init' first.", CLIColors.RED)
            return
        
        action = ' '.join(args)
        if not action:
            print_colored("Error: Please specify an action.", CLIColors.YELLOW)
            return
        
        print_colored("Executing action...", CLIColors.CYAN)
        try:
            result = self.orchestrator.act(action)
            print_colored("✓ Action executed", CLIColors.GREEN)
            if self.verbose:
                print(json.dumps(result, indent=2))
        except Exception as e:
            print_colored(f"Error: {e}", CLIColors.RED)
    
    def cmd_status(self, args):
        """显示系统状态"""
        print_colored("System Status", CLIColors.CYAN, bold=True)
        print("=" * 50)
        
        # 引擎状态
        if self.orchestrator:
            print_colored("Engine: ", CLIColors.WHITE, bold=True)
            print(f"  Status: {CLIColors.GREEN}Running{CLIColors.RESET}")
            try:
                stats = self.orchestrator.get_stats()
                print(f"  Processing cycles: {stats.get('cycles', 0)}")
                print(f"  Knowledge nodes: {stats.get('knowledge_nodes', 0)}")
                print(f"  Memory usage: {stats.get('memory_mb', 0):.2f} MB")
            except Exception as e:
                print(f"  Stats unavailable: {e}")
        else:
            print_colored("Engine: ", CLIColors.WHITE, bold=True)
            print(f"  Status: {CLIColors.YELLOW}Not initialized{CLIColors.RESET}")
        
        # 速率限制状态
        print_colored("\nRate Limiter:", CLIColors.WHITE, bold=True)
        rate_stats = self.rate_limiter.get_stats("cli_user")
        print(f"  Total requests: {rate_stats['total_requests']}")
        print(f"  Allowed: {rate_stats['allowed_requests']}")
        print(f"  Rejected: {rate_stats['rejected_requests']}")
        
        # 会话统计
        print_colored("\nSession Statistics:", CLIColors.WHITE, bold=True)
        successful = sum(1 for h in self.history if h.get('success', False))
        failed = len(self.history) - successful
        print(f"  Total commands: {len(self.history)}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
    
    def cmd_config(self, args):
        """显示配置"""
        print_colored("Current Configuration", CLIColors.CYAN, bold=True)
        print("=" * 50)
        config_dict = self.config.to_dict() if hasattr(self.config, 'to_dict') else vars(self.config)
        print(json.dumps(config_dict, indent=2))
    
    def cmd_memory(self, args):
        """查询知识图谱"""
        if not self.orchestrator:
            print_colored("Error: Engine not initialized. Run 'init' first.", CLIColors.RED)
            return
        
        query = ' '.join(args) if args else "*"
        print_colored(f"Querying memory for: {query}", CLIColors.CYAN)
        try:
            result = self.orchestrator.query_memory(query)
            print_colored("\nResults:", CLIColors.GREEN)
            if isinstance(result, list):
                for item in result[:10]:  # 限制显示数量
                    print(f"  - {item}")
                if len(result) > 10:
                    print(f"  ... and {len(result) - 10} more")
            else:
                print(json.dumps(result, indent=2))
        except Exception as e:
            print_colored(f"Error: {e}", CLIColors.RED)
    
    def cmd_logs(self, args):
        """显示日志"""
        level = args[0] if args else "INFO"
        print_colored(f"Recent Logs (Level: {level})", CLIColors.CYAN)
        print("=" * 50)
        # TODO: 实现真实的日志获取
        print("(Log functionality to be implemented)")
    
    def cmd_history(self, args):
        """显示命令历史"""
        print_colored("Command History", CLIColors.CYAN, bold=True)
        for i, entry in enumerate(self.history[-20:], 1):  # 显示最近 20 条
            status = "✓" if entry.get('success', False) else "✗"
            print(f"  {i}. [{status}] {entry['type']}: {entry.get('query', entry.get('data', 'N/A'))[:50]}")
    
    def cmd_clear(self, args):
        """清屏"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def cmd_verbose(self, args):
        """切换详细模式"""
        if not args:
            self.verbose = not self.verbose
        else:
            self.verbose = args[0].lower() in ('on', 'true', '1')
        
        status = "ON" if self.verbose else "OFF"
        print_colored(f"Verbose mode: {status}", CLIColors.CYAN)
    
    def cmd_quit(self, args):
        """退出 CLI"""
        print_colored("Goodbye!", CLIColors.CYAN)
        sys.exit(0)
    
    def process_command(self, line: str):
        """处理单行命令"""
        parts = line.strip().split(maxsplit=1)
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []
        
        # 命令映射
        commands = {
            'help': self.cmd_help,
            'init': self.cmd_init,
            'think': self.cmd_think,
            'learn': self.cmd_learn,
            'reason': self.cmd_reason,
            'act': self.cmd_act,
            'status': self.cmd_status,
            'config': self.cmd_config,
            'memory': self.cmd_memory,
            'logs': self.cmd_logs,
            'history': self.cmd_history,
            'clear': self.cmd_clear,
            'verbose': self.cmd_verbose,
            'quit': self.cmd_quit,
            'exit': self.cmd_quit,
        }
        
        if cmd in commands:
            try:
                commands[cmd](args)
            except KeyboardInterrupt:
                print_colored("\nOperation cancelled.", CLIColors.YELLOW)
            except Exception as e:
                print_colored(f"Command error: {e}", CLIColors.RED)
        else:
            print_colored(f"Unknown command: {cmd}. Type 'help' for available commands.", CLIColors.YELLOW)
    
    def run_interactive(self):
        """运行交互式模式"""
        print_colored("""
╔══════════════════════════════════════════════════════════╗
║           Cognitive Engine CLI v1.0                       ║
║           Type 'help' for available commands              ║
╚══════════════════════════════════════════════════════════╝
""", CLIColors.CYAN, bold=True)
        
        # 自动初始化引擎
        self.initialize_engine()
        
        while True:
            try:
                prompt = f"{CLIColors.GREEN}cog-engine{CLIColors.RESET}> "
                line = input(prompt)
                
                if line.strip():
                    self.process_command(line)
                    readline.add_history(line)
                    
            except EOFError:
                print()
                self.cmd_quit([])
            except KeyboardInterrupt:
                print()
                continue
    
    def run_batch(self, commands_file: str):
        """运行批处理模式"""
        if not os.path.exists(commands_file):
            print_colored(f"Error: Commands file not found: {commands_file}", CLIColors.RED)
            sys.exit(1)
        
        with open(commands_file, 'r') as f:
            commands = f.readlines()
        
        print_colored(f"Executing batch commands from: {commands_file}", CLIColors.CYAN)
        self.initialize_engine()
        
        for line in commands:
            line = line.strip()
            if line and not line.startswith('#'):  # 跳过空行和注释
                print_colored(f"> {line}", CLIColors.WHITE)
                self.process_command(line)


def main():
    """CLI 入口点"""
    parser = argparse.ArgumentParser(
        description="Cognitive Engine CLI - Interact with the AGI system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cog-engine                    # Start interactive mode
  cog-engine --config config.json
  cog-engine --batch commands.txt
  cog-engine --eval "think hello"
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--batch', '-b',
        type=str,
        help='Path to batch commands file'
    )
    
    parser.add_argument(
        '--eval', '-e',
        type=str,
        help='Execute a single command and exit'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Cognitive Engine CLI v1.0.0'
    )
    
    args = parser.parse_args()
    
    cli = CognitiveEngineCLI(config_path=args.config)
    cli.verbose = args.verbose
    
    if args.eval:
        cli.initialize_engine()
        cli.process_command(args.eval)
    elif args.batch:
        cli.run_batch(args.batch)
    else:
        cli.run_interactive()


if __name__ == "__main__":
    main()
