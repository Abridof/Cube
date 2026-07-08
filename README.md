# AI 编程能力提升系统 v2.1

一个智能高效的 AI 辅助编程系统，专注于减少 Token 消耗并提升调试效率。

## 核心特性

### 1. 本地修复 (Local Fixing)
- **零 Token 消耗**修复常见语法错误
- 支持缺失冒号、拼写错误、缩进问题等
- 自动识别并修复简单错误，无需调用 LLM

### 2. 上下文压缩 (Context Compression)
- 仅发送错误相关代码片段给 LLM
- 移除注释和空行，减少 Token 使用
- 智能提取错误行及其周围上下文

### 3. 智能缓存 (Smart Caching)
- 相同错误直接复用修复方案
- 基于错误哈希的缓存机制
- 显著减少重复请求

### 4. 实时监控 (Real-time Monitoring)
- 统计 Token 节省率
- 详细的优化报告
- 性能指标追踪

## 项目结构

```
/workspace/
├── smart_debug_loop.py    # 智能调试主循环模块
├── token_optimizer.py     # Token 优化模块
├── secure_sandbox.py      # 安全代码执行沙箱
├── llm_client.py          # LLM 客户端接口
├── test_smart_debug.py    # 智能调试模块测试
├── test_token_optimizer.py # Token 优化模块测试
├── cube/                  # (预留目录)
└── README.md              # 项目文档
```

## 快速开始

### 安装依赖

本项目使用 Python 标准库，无需额外依赖。

### 基本使用

```python
from smart_debug_loop import run_smart_debug

# 运行智能调试
result = run_smart_debug(
    requirement="Print Hello World",
    initial_code="def main()\n    print('Hello')"  # 有语法错误的代码
)

print(f"成功：{result.success}")
print(f"尝试次数：{result.attempts}")
print(f"输出：{result.output}")
print(result.get_stats_report())
```

### 运行测试

```bash
# 运行所有测试
python -m unittest discover -v

# 运行特定模块测试
python -m unittest test_smart_debug -v
python -m unittest test_token_optimizer -v
```

## 测试结果

### 智能调试模块 (test_smart_debug.py)
- ✅ 15 个测试全部通过
- 覆盖本地修复、上下文压缩、缓存机制、Token 统计

### Token 优化模块 (test_token_optimizer.py)
- ✅ 22 个测试全部通过
- 覆盖缓存机制、上下文压缩、边界情况、Token 估算

**总计：37/37 测试通过**

## Token 节省效果

典型场景下的 Token 节省率：
- 本地修复场景：~100%（完全避免 LLM 调用）
- 缓存命中场景：~100%（复用历史结果）
- 上下文压缩：30-70%（减少输入 Token）

**综合节省率：50-85%**

## 模块说明

### smart_debug_loop.py
核心调试循环模块，包含：
- `LocalFixer`: 本地语法修复器
  - 预编译正则表达式，提升匹配性能
  - 支持多种语法错误自动修复
- `ContextCompressor`: 上下文压缩器
  - 智能提取错误相关代码
  - 移除冗余注释和空行
- `SmartDebugLoop`: 智能调试主循环
  - 整合本地修复、缓存、压缩策略
  - 实时 Token 消耗统计
- `TokenStats`: Token 消耗统计

### token_optimizer.py
Token 优化辅助模块，提供额外的优化策略和工具函数：
- 上下文压缩与增量更新
- 本地预检与简单错误修复
- 响应格式约束
- 缓存机制

### secure_sandbox.py
安全代码执行沙箱，提供隔离的代码执行环境：
- 临时文件隔离
- 执行超时控制
- 错误捕获与处理
- 原子写入保护

### llm_client.py
LLM 客户端接口，支持真实 API 调用和 Mock 模式：
- 预编译错误模式匹配
- 智能 Mock 响应
- 易于扩展的真实 API 集成

## 配置 LLM

默认使用 Mock 模式进行测试。要使用真实 LLM：

1. 编辑 `llm_client.py`
2. 配置 API key 和端点
3. 调用 `call_llm_real()` 函数

## 扩展开发

### 添加新的本地修复规则

在 `LocalFixer.FIX_PATTERNS` 中添加正则表达式规则：

```python
FIX_PATTERNS = [
    (r'\\bprnt\\s*\\(', 'print('),  # 修复 prnt -> print
    # 添加更多规则...
]
```

### 自定义压缩策略

继承 `ContextCompressor` 并重写 `compress()` 方法。

## 版本历史

- **v2.1**: 性能优化版本
  - 预编译正则表达式，减少重复编译开销
  - 使用 frozenset 替代 list/tuple 进行成员检查
  - 位运算优化整数除法 (`>> 2` 替代 `// 4`)
  - 优化条件判断逻辑，减少不必要的计算
  - 添加常量定义，避免魔法数字
  - 改进文件写入的原子性和错误处理

- **v2.0**: 添加 Token 优化功能
  - 本地修复器
  - 上下文压缩器
  - 智能缓存机制
  - Token 统计报告

- **v1.0**: 基础调试循环

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！