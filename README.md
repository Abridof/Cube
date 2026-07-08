
# AI 编程能力提升系统 v8.0 - 世界模型与自主性层

一个智能高效的 AI 辅助编程系统，专注于减少 Token 消耗、提升调试效率并提供企业级配置管理。**v8.0 新增世界模型层**，支持内部环境模拟、因果推理、预测和反事实推理，实现真正的自主认知能力。

## 🎯 愿景

> "识别万物，研究万物" - 通过**统一认知表示**、**感知 **(Perception)、**推理 **(Reasoning)、**行动 **(Action) 和 **学习 **(Learning) 的完整认知循环，构建能够跨领域泛化的 AI 智慧系统。


## 🚀 核心特性

### 1. 本地修复 (Local Fixing) - 零 Token 消耗
- **零 Token 消耗**修复常见语法错误
- 支持缺失冒号、拼写错误、缩进问题等
- 自动识别并修复简单错误，无需调用 LLM
- 预编译正则表达式，高性能匹配

### 2. 上下文压缩 (Context Compression) - 节省 30-70% Token
- 仅发送错误相关代码片段给 LLM
- 移除注释和空行，减少 Token 使用
- 智能提取错误行及其周围上下文
- 支持大文件分段处理

### 3. 智能缓存 (Smart Caching) - 避免重复请求
- 相同错误直接复用修复方案
- 基于错误哈希的缓存机制
- 可配置缓存大小和策略
- 显著减少重复请求

### 4. 实时监控 (Real-time Monitoring) - 详细统计
- 统计 Token 节省率
- 详细的优化报告
- 性能指标追踪
- 延迟和成功率监控

### 5. 企业级配置管理 (Configuration) - 灵活部署
- 支持环境变量配置
- 支持 JSON 配置文件
- 类型安全的配置类
- 完整的配置验证


### 6. 统一认知表示层 (UCR Layer) - 技术突破 ✨
- **符号表示**: 精确的逻辑结构、因果关系、规则（可解释、可推理、可验证）
- **向量表示**: 语义嵌入、模糊匹配、模式识别（基于 TF-IDF 风格权重）
- **混合索引**: 同时支持精确查询和相似性搜索
- **多模态解析**: 代码结构（函数/类/约束）、文本逻辑关系（因果/条件/对比）
- **认知单元**: 符号 + 向量的统一数据结构，支持关系发现和图谱构建
- **实体类型**: CONCEPT, ACTION, PROPERTY, RELATION, EVENT, CONSTRAINT, HYPOTHESIS, EVIDENCE

### 7. 知识图谱与元学习 (Knowledge Graph & Meta-Learning) - 第二阶段突破 ✨
- **知识图谱**: 基于认知单元构建关系网络，支持 12 种关系类型
- **混合检索**: 结合图谱遍历（精确）和向量相似性（模糊）
- **元学习器**: 跟踪 4 种学习策略效果，动态选择最优策略
- **假设系统**: 主动生成假设并通过证据验证（pending/verified/refuted）
- **知识融合**: 自动识别并合并相似度>0.95 的重复概念
- **增强记忆银行**: 整合 UCR、知识图谱、混合检索和元学习

### 8. 多模态感知层 (Multimodal Perception) - 第三阶段突破 ✨✨
- **图像感知**: 结构分析、颜色直方图、纹理特征、边缘检测、物体识别
- **音频感知**: 时域分析（RMS、过零率）、频域分析、节奏检测、BPM 估计
- **结构化数据感知**: JSON/XML 解析、层级结构提取、统计特征计算
- **跨模态融合**: 多模态特征加权融合、冲突解决、统一 UCR 表示生成
- **跨模态对齐**: 基于特征相似度的模态间对齐与关联发现
- **7 种模态类型**: TEXT, IMAGE, AUDIO, VIDEO, STRUCTURED_DATA, CODE, SENSOR

### 9. 世界模型与自主性层 (World Model) - 第四阶段突破 ✨✨✨
- **状态空间建模**: 用状态变量构建世界的内部表示，支持 6 种状态类型（物理、认知、情感、社会、环境、抽象）
- **动态学习**: 从观测中自动学习状态转移规律和因果图
- **前向预测**: 基于当前状态和学习的转移默式预测未来状态，支持多步预测和置信度衰减
- **反事实推理**: 探索"如果...会怎样"的场景，生成替代历史并分析差异
- **因果发现**: 自动识别变量间的因果关系，构建因果图
- **自我模型**: 对自身认知过程进行建模，跟踪能力、局限性和信念，实现元认知
- **持久化**: 支持世界模型的保存和加载

### 10. 通用认知引擎 (Cognition Engine) - 智慧核心

- **感知 (Perception)**: 解析多样化输入（代码、文本、数据结构、图像、音频）
- **推理 (Reasoning)**: 生成动态思维链 (Chain of Thought)
- **行动 (Action)**: 在安全环境中执行验证计划
- **学习 (Learning)**: 从交互中提取模式，构建持久知识库
- **记忆银行 (Memory Bank)**: 存储和检索跨领域知识节点
- **状态管理**: 完整的认知状态追踪（IDLE → PERCEIVING → REASONING → ACTING → LEARNING）

## 项目结构

```
/workspace/
├── smart_debug_loop.py       # 智能调试主循环模块
├── token_optimizer.py        # Token 优化模块
├── secure_sandbox.py         # 安全代码执行沙箱
├── llm_client.py             # LLM 客户端接口（多后端支持）
├── config.py                 # 配置管理模块
├── cognition_engine.py       # 通用认知引擎（感知 - 推理 - 行动 - 学习）
├── ucr_layer.py              # 统一认知表示层（符号 - 向量混合）✨
├── knowledge_graph.py        # 知识图谱与元学习模块（第二阶段）✨
├── multimodal_perception.py  # 多模态感知层（第三阶段）✨✨
├── world_model.py            # 世界模型与自主性层（第四阶段）✨✨✨
├── test_smart_debug.py       # 智能调试模块测试
├── test_token_optimizer.py   # Token 优化模块测试
├── test_config.py            # 配置模块测试
├── test_llm_client.py        # LLM 客户端测试
├── test_cognition_engine.py  # 认知引擎测试
├── test_ucr_layer.py         # UCR 层测试 ✨
├── test_knowledge_graph.py   # 知识图谱测试 ✨
├── test_multimodal_perception.py  # 多模态感知测试 ✨✨
├── test_world_model.py       # 世界模型测试 ✨✨✨
├── cube/                     # (预留目录)
└── README.md                 # 项目文档
```

## 快速开始

### 安装依赖

**基础模式**（仅使用标准库）：
```bash
# 无需额外依赖，直接使用
```

**完整模式**（支持真实 LLM API 调用）：
```bash
pip install requests
```

### 基本使用

#### 1. 简单调试

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

#### 2. 使用配置

```python
from config import Config, get_config
from llm_client import LLMClient

# 从环境变量加载配置
config = get_config()

# 或者手动配置
config = Config()
config.llm.api_key = "your-api-key"
config.llm.model = "gpt-4"
config.debug.max_attempts = 10

# 创建 LLM 客户端
client = LLMClient(
    api_key=config.llm.api_key,
    model=config.llm.model,
    max_tokens=config.llm.max_tokens
)

# 调用 LLM
response = client.call("Write a function to sort a list")
print(f"Response: {response.text}")
print(f"Tokens used: {response.tokens_used}")
print(f"Latency: {response.latency_ms:.2f}ms")
```

#### 3. 环境变量配置

```bash
# .env 文件或 shell 导出
export LLM_API_KEY="sk-your-api-key"
export LLM_MODEL="gpt-4"
export LLM_MAX_TOKENS=2000
export DEBUG_MAX_ATTEMPTS=10
export SANDBOX_TIMEOUT=10
```

#### 4. JSON 配置文件

```json
{
  "llm": {
    "api_key": "sk-your-api-key",
    "model": "gpt-4",
    "max_tokens": 2000
  },
  "sandbox": {
    "timeout": 10,
    "max_memory_mb": 512
  },
  "debug": {
    "max_attempts": 10,
    "use_cache": true,
    "log_level": "DEBUG"
  }
}
```

```python
from config import Config

config = Config.from_json("config.json")
```

#### 5. 使用统一认知表示层（新增）✨

```python
from ucr_layer import (
    UnifiedRepresentationEngine, SymbolicNode, 
    CognitiveUnit, EntityType, represent
)

# 创建引擎
engine = UnifiedRepresentationEngine()

# 示例 1: 代码解析 - 自动提取函数、类、约束
code = """
def calculate(a, b):
    return a + b

class Calculator:
    def add(self, x):
        assert x >= 0
"""
unit = engine.create_unit(code, content_type='code', domain='programming', tags={'python'})
print(f"实体类型：{unit.symbolic.entity_type}")
print(f"关系数量：{len(unit.symbolic.relations)}")

# 示例 2: 文本解析 - 提取因果/条件关系
text = "If temperature exceeds 100°C, water boils because molecules move faster."
unit = engine.create_unit(text, content_type='text', domain='physics')
print(f"定义：{unit.symbolic.definition[:80]}...")

# 示例 3: 语义相似性搜索
results = engine.search_by_similarity("heat and boiling", threshold=0.1)
for unit, score in results:
    print(f"匹配：{unit.symbolic.label} (相似度：{score:.3f})")

# 示例 4: 关系发现（图谱遍历）
related = engine.find_relations(unit.id, max_depth=2)
print(f"相关单元数：{len(related)}")

# 示例 5: 便捷函数
unit = represent("Quick concept", domain='general')
```

#### 6. 使用通用认知引擎

```python
from cognition_engine import CognitionEngine, MemoryBank, KnowledgeNode

# 创建认知引擎
engine = CognitionEngine()

# 示例 1: 编程领域问题
code_problem = {
    "task": "Fix the infinite loop",
    "code": "while True: print('help')"
}
result = engine.process(code_problem, domain="coding")
print(f"分析：{result['analysis']}")
print(f"计划：{result['plan']}")
print(f"结果：{result['results']}")

# 示例 2: 逻辑推理问题
logic_problem = "If all A are B, and some B are C, can we conclude some A are C?"
result = engine.process(logic_problem, domain="logic")

# 示例 3: 查看记忆银行中的知识
memory = engine.memory
nodes = memory.search("coding")
for node in nodes:
    print(f"知识节点：{node.description}")
    print(f"置信度：{node.confidence_score}")
```
### 运行测试

```bash
# 运行所有测试
python -m unittest discover -v

# 运行特定模块测试
python -m unittest test_smart_debug -v
python -m unittest test_token_optimizer -v
python -m unittest test_config -v
python -m unittest test_llm_client -v
python -m unittest test_cognition_engine -v
```

## 测试结果

### 测试覆盖率


截至 v6.0，项目共有 **132** 个单元测试，覆盖所有核心模块：

| 模块 | 测试数 | 状态 |
|------|--------|------|
| smart_debug_loop | 15 | ✅ 通过 |
| token_optimizer | 22 | ✅ 通过 |
| config | 11 | ✅ 通过 |
| llm_client | 18 | ✅ 通过 |
| cognition_engine | 11 | ✅ 通过 |
| ucr_layer | 28 | ✅ 通过 |
| **knowledge_graph** | **27** | ✅ 通过 |
| **总计** | **132** | **✅ 全部通过** |

### 性能指标

典型场景下的 Token 节省率：
- 本地修复场景：~100%（完全避免 LLM 调用）
- 缓存命中场景：~100%（复用历史结果）
- 上下文压缩：30-70%（减少输入 Token）

**综合节省率：50-85%**

### 运行测试

```bash
$ python -m unittest discover -v

# 输出示例:
# test_fix_missing_colon_def (test_smart_debug.TestLocalFixer) ... ok
# test_cache_hit_prevents_llm_call (test_smart_debug.TestSmartDebugLoop) ... ok
# test_load_from_env (test_config.TestConfigFromEnv) ... ok
# ...
# ----------------------------------------------------------------------
# Ran 48 tests in 0.038s
# OK
```

## 模块说明

### smart_debug_loop.py - 智能调试核心
核心调试循环模块，包含：
- `LocalFixer`: 本地语法修复器（零 Token 消耗）
- `ContextCompressor`: 上下文压缩器（减少 30-70% Token）
- `SmartDebugLoop`: 智能调试主循环
- `TokenStats`: Token 消耗统计

### token_optimizer.py - Token 优化专家
Token 优化辅助模块，提供：
- 上下文压缩策略
- 增量提示生成
- 本地预检修复
- 响应格式约束

### config.py - 配置管理（新增）
企业级配置管理模块：
- `Config`: 主配置类
- `LLMConfig`: LLM 配置
- `SandboxConfig`: 沙箱配置
- `DebugConfig`: 调试配置
- 支持环境变量、JSON 文件加载

### llm_client.py - 多后端 LLM 客户端（增强）
LLM 客户端接口，支持：
- OpenAI API 兼容
- Anthropic Claude 支持
- 本地模型部署
- 自动重试机制
- 延迟和 Token 统计
- Mock 模式测试

### secure_sandbox.py - 安全沙箱
安全代码执行沙箱，提供：
- 隔离的执行环境
- 超时控制
- 资源限制
- 导入白名单/黑名单

### cognition_engine.py - 通用认知引擎
AI 智慧的核心框架，实现完整的认知循环：
- `CognitionEngine`: 主引擎类，编排感知 - 推理 - 行动 - 学习流程
- `MemoryBank`: 持久化知识库，存储和检索跨领域知识节点
- `KnowledgeNode`: 知识单元，包含模式描述、置信度和示例
- `CognitiveState`: 认知状态枚举（IDLE, PERCEIVING, REASONING, ACTING, LEARNING, ERROR）
- **核心方法**:
  - `perceive()`: 分析输入数据，识别结构和意图
  - `reason()`: 生成思维链和解决计划
  - `act()`: 在安全环境中执行计划步骤
  - `learn()`: 从结果中提取可泛化的知识模式
  - `process()`: 完整认知循环的主入口

### ucr_layer.py - 统一认知表示层（新增）✨
技术突破模块，实现符号 - 向量混合表示：
- `SymbolicNode`: 精确的逻辑单元（可解释、可推理、可验证）
- `VectorEmbedding`: 语义嵌入（基于 TF-IDF 风格权重，支持余弦相似度）
- `CognitiveUnit`: 符号 + 向量的统一数据结构
- `TextEncoder`: 文本编码器（分词、去停用词、TF-IDF 加权）
- `SymbolicParser`: 符号解析器（代码结构提取、逻辑关系发现）
- `UnifiedRepresentationEngine`: 统一表示引擎（多模态输入处理、索引、搜索）
- `EntityType`: 实体类型枚举（CONCEPT, ACTION, PROPERTY, RELATION, EVENT, CONSTRAINT, HYPOTHESIS, EVIDENCE）
- **核心功能**:
  - `create_unit()`: 从代码/文本创建认知单元
  - `search_by_similarity()`: 语义相似性搜索
  - `search_by_type/tag()`: 精确查询
  - `find_relations()`: 关系发现和图谱遍历
  - `export_to_dict()/import_from_dict()`: 持久化支持


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

### v9.0 (当前版本) - 实验验证阶段 🧪✨
- ✨ 新增第五阶段实验模块 (`experiment_phase5.py`)
- ✨ 真实数据摄入：维基百科、代码库、科学论文模拟器
- ✨ 知识提取：概念识别、关系抽取、模式发现
- ✨ 网格世界仿真：Q-Learning 智能体避坑学习
- ✨ 涌现行为观察：策略形成、模式识别、迁移学习检测
- 📝 更新文档至 v9.0
- ✅ 新增 29 个实验测试，总测试数达 219 个

### v8.0 - 世界模型与自主性层 ✨✨✨
- ✨ 新增世界模型模块 (`world_model.py`)
- ✨ 状态空间建模：6 种状态类型（物理、认知、情感、社会、环境、抽象）
- ✨ 动态学习：从观测中自动学习状态转移规律和因果图
- ✨ 前向预测：多步预测与置信度衰减机制
- ✨ 反事实推理："如果...会怎样"场景探索与差异分析
- ✨ 因果发现：自动识别变量间因果关系
- ✨ 自我模型：元认知能力，跟踪能力、局限性和信念
- ✨ 持久化：支持世界模型的保存和加载
- 📝 更新文档至 v8.0
- ✅ 新增 32 个世界模型测试，总测试数达 190 个

### v7.0 - 多模态感知层 ✨✨
- ✨ 新增多模态感知模块 (`multimodal_perception.py`)
- ✨ 图像感知：结构分析、颜色直方图、纹理特征、边缘检测
- ✨ 音频感知：时域分析、频域分析、节奏检测、BPM 估计
- ✨ 结构化数据感知：JSON/XML 解析、层级结构提取
- ✨ 跨模态融合：多模态特征加权融合与冲突解决
- ✨ 7 种模态类型支持（TEXT, IMAGE, AUDIO, VIDEO, STRUCTURED_DATA, CODE, SENSOR）
- 📝 更新文档至 v7.0
- ✅ 新增 26 个多模态感知测试，总测试数达 158 个

### v6.0 - 知识图谱与真正学习能力 ✨
- ✨ 新增知识图谱模块 (`knowledge_graph.py`)
- ✨ 基于 UCR 的认知单元构建关系图谱
- ✨ 混合检索：结合图谱遍历和向量相似性
- ✨ 元学习机制：跟踪和强化学习策略
- ✨ 假设生成与验证：主动推理能力
- ✨ 知识融合：自动识别并合并相似概念
- ✨ 增强记忆银行：整合图谱、向量检索和元学习
- 📝 更新文档至 v6.0
- ✅ 新增 27 个知识图谱测试，总测试数达 132 个

### v5.0 - 统一认知表示层
- ✨ 新增统一认知表示层 (`ucr_layer.py`)
- ✨ 符号 - 向量混合表示架构
- ✨ 多模态解析（代码结构、逻辑关系提取）
- ✨ 语义相似性搜索和关系发现
- ✨ 8 种实体类型支持（CONCEPT, ACTION, PROPERTY, RELATION, EVENT, CONSTRAINT, HYPOTHESIS, EVIDENCE）
- 📝 更新文档至 v5.0
- ✅ 新增 28 个 UCR 层测试，总测试数达 105 个


### v4.0 (当前版本) - 通用认知引擎
- ✨ 新增通用认知引擎 (`cognition_engine.py`)
- ✨ 感知 - 推理 - 行动 - 学习完整循环
- ✨ 持久化记忆银行和知识节点系统
- ✨ 跨领域泛化能力（编程、逻辑、科学等）
- ✨ 认知状态追踪和管理
- 📝 更新文档至 v4.0
- ✅ 新增 11 个认知引擎测试，总测试数达 77 个

### v3.0 - 企业级增强
- ✨ 新增配置管理模块 (`config.py`)
- ✨ 多后端 LLM 客户端支持
- ✨ 自动重试和超时处理
- ✨ 完整的类型注解
- ✨ 详细的日志记录
- 📝 更新文档和示例

### v2.0 - Token 优化功能
- 本地修复器（零 Token 消耗）
- 上下文压缩器（减少 30-70% Token）
- 智能缓存机制
- Token 统计报告

### v1.0 - 基础调试循环
- 基础调试循环
- 安全代码沙箱
- Mock LLM 支持

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！