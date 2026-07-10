"""
Advanced Type Definitions for AGI Cognition Engine v2.0
========================================================
严格的类型系统定义，消除 Any 类型滥用

设计原则：
1. 使用 TypedDict 定义结构化数据
2. 使用 Protocol 定义接口契约  
3. 使用 Union 明确联合类型
4. 使用 Literal 限制字符串字面量
5. 零容忍不必要的 Any 类型

Author: AI Assistant (Computer Scientist & AGI Researcher)
"""

from __future__ import annotations
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    Set,
    Literal,
    TypedDict,
    Protocol,
    TypeVar,
    Generic,
    Callable,
    Mapping,
    Sequence,
    Final,
    runtime_checkable,
)
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ============================================================================
# UCR (Unified Cognitive Representation) 精确类型
# ============================================================================

class EntityType(Enum):
    """UCR 实体类型"""
    CONCEPT = "concept"
    PROPERTY = "property"
    RELATION = "relation"
    EVENT = "event"
    HYPOTHESIS = "hypothesis"
    EVIDENCE = "evidence"
    ACTION = "action"
    GOAL = "goal"
    STATE = "state"


class ModalityType(Enum):
    """感知模态类型"""
    TEXTUAL = "textual"
    VISUAL = "visual"
    AUDITORY = "auditory"
    TACTILE = "tactile"
    PROPRIOCEPTIVE = "proprioceptive"
    SYMBOLIC = "symbolic"


class UCRMetadata(TypedDict, total=False):
    """UCR 元数据类型"""
    source: str
    confidence: float
    timestamp: str
    modality: str
    domain: str
    tags: List[str]
    parent_id: str
    children_ids: List[str]


class UCRTyped(TypedDict):
    """严格类型的 UCR 表示"""
    entity_type: str
    symbol: str
    content: str
    vector: Optional[List[float]]
    metadata: UCRMetadata


# ============================================================================
# 知识图谱类型
# ============================================================================

class EdgeType(Enum):
    """边类型枚举"""
    IS_A = "is_a"
    HAS_PROPERTY = "has_property"
    CAUSES = "causes"
    ENABLES = "enables"
    PREVENTS = "prevents"
    SIMILAR_TO = "similar_to"
    PART_OF = "part_of"
    INSTANCE_OF = "instance_of"


class GraphNode(TypedDict):
    """图谱节点类型"""
    id: str
    label: str
    node_type: str
    properties: Dict[str, str]
    embedding: Optional[List[float]]


class GraphEdge(TypedDict):
    """图谱边类型"""
    source: str
    target: str
    edge_type: str
    weight: float
    properties: Dict[str, str]


# ============================================================================
# 工作记忆类型
# ============================================================================

class MemoryItemStatus(Enum):
    """记忆项状态"""
    ACTIVE = "active"
    DECAYING = "decaying"
    CONSOLIDATED = "consolidated"
    EVICTED = "evicted"


class WorkingMemoryItemTyped(TypedDict):
    """工作记忆项类型"""
    id: str
    content: str
    priority: float
    activation: float
    status: str
    created_at: str
    last_accessed: str
    access_count: int


# ============================================================================
# 认知循环类型
# ============================================================================

class CognitivePhase(Enum):
    """认知阶段"""
    PERCEPTION = "perception"
    ATTENTION = "attention"
    REASONING = "reasoning"
    DECISION = "decision"
    ACTION = "action"
    REFLECTION = "reflection"
    LEARNING = "learning"


class PerceptionInput(TypedDict):
    """感知输入类型"""
    raw_data: str
    modality: str
    metadata: Dict[str, str]
    timestamp: str


class AttentionFocus(TypedDict):
    """注意力焦点类型"""
    target_id: str
    relevance_score: float
    priority: float
    duration_ms: int


class ReasoningStep(TypedDict):
    """推理步骤类型"""
    step_id: str
    operation: str
    inputs: List[str]
    output: str
    confidence: float
    rule_applied: Optional[str]


class DecisionOutput(TypedDict):
    """决策输出类型"""
    action_type: str
    parameters: Dict[str, str]
    expected_outcome: str
    confidence: float
    alternatives: List[str]


# ============================================================================
# Protocol 定义 (接口契约)
# ============================================================================

@runtime_checkable
class PerceptualModule(Protocol):
    """感知模块接口"""
    
    def process(self, input_data: str, modality: str) -> UCRTyped:
        """处理原始感知数据"""
        ...
    
    def get_confidence(self) -> float:
        """获取当前置信度"""
        ...


@runtime_checkable
class ReasoningEngine(Protocol):
    """推理引擎接口"""
    
    def infer(self, premises: List[UCRTyped], rules: List[str]) -> List[UCRTyped]:
        """执行推理"""
        ...
    
    def validate(self, hypothesis: UCRTyped) -> bool:
        """验证假设"""
        ...


@runtime_checkable
class LearningModule(Protocol):
    """学习模块接口"""
    
    def update(self, experience: List[UCRTyped], reward: float) -> None:
        """基于经验更新模型"""
        ...
    
    def consolidate(self) -> None:
        """巩固记忆"""
        ...


@runtime_checkable
class AttentionMechanism(Protocol):
    """注意力机制接口"""
    
    def focus(self, items: List[UCRTyped], query: str) -> List[AttentionFocus]:
        """选择注意焦点"""
        ...
    
    def shift(self, new_focus: str) -> None:
        """转移注意力"""
        ...


# ============================================================================
# 因果推理类型
# ============================================================================

class CausalRelation(TypedDict):
    """因果关系类型"""
    cause: str
    effect: str
    strength: float
    mechanism: str
    evidence: List[str]
    confounders: List[str]


class CausalGraph(TypedDict):
    """因果图类型"""
    nodes: List[str]
    edges: List[CausalRelation]
    interventions: Dict[str, str]


class InterventionResult(TypedDict):
    """干预结果类型"""
    intervention: str
    outcome: str
    counterfactual: str
    ate: float  # Average Treatment Effect


# ============================================================================
# 符号接地类型
# ============================================================================

class GroundingLink(TypedDict):
    """符号接地链接类型"""
    symbol: str
    percept: str
    association_strength: float
    context: str
    learned_at: str


class SensorimotorSchema(TypedDict):
    """感觉运动模式类型"""
    action: str
    sensory_prediction: str
    actual_sensation: str
    prediction_error: float


# ============================================================================
# 泛型类型变量
# ============================================================================

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
UCR = TypeVar('UCR', bound=UCRTyped)


# ============================================================================
# 资源追踪类型
# ============================================================================

class ResourceUsage(TypedDict):
    """资源使用类型"""
    node_count: int
    edge_count: int
    memory_items: int
    iterations: int
    elapsed_time_ms: float
    memory_mb: float


class ResourceLimits(TypedDict):
    """资源限制类型"""
    max_nodes: int
    max_edges: int
    max_memory_items: int
    max_iterations: int
    max_time_ms: float
    max_memory_mb: float
