"""
Strict Type Definitions for AGI Cognition Engine v3.0
======================================================
严格的类型定义系统 - 消除所有不必要的 Any 类型

设计原则:
1. 使用 TypedDict 定义所有结构化数据
2. 使用 Protocol 定义接口契约
3. 使用 Union 明确联合类型
4. 使用 Literal 限制字符串字面量
5. 零容忍不必要的 Any 类型
6. 所有外部输入必须验证

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
# 通用数据类型 (替代 Any)
# ============================================================================

class JsonPrimitive(Enum):
    """JSON 原始类型标记"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    NULL = "null"


JsonValueT = Union[
    str,
    int,
    float,
    bool,
    None,
    List['JsonValueT'],
    Dict[str, 'JsonValueT']
]


class DataContent(TypedDict, total=False):
    """通用数据内容类型 - 替代 Any"""
    text: str
    code: str
    numeric_value: float
    boolean_value: bool
    structured_data: Dict[str, JsonValueT]
    raw_bytes: str  # base64 encoded


@runtime_checkable
class ContentContainer(Protocol):
    """可包含内容的对象协议"""
    
    def get_content(self) -> DataContent:
        """获取内容"""
        ...
    
    def set_content(self, content: DataContent) -> None:
        """设置内容"""
        ...


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
    PERCEPT = "percept"
    SYMBOL = "symbol"


class ModalityType(Enum):
    """感知模态类型"""
    TEXTUAL = "textual"
    VISUAL = "visual"
    AUDITORY = "auditory"
    TACTILE = "tactile"
    PROPRIOCEPTIVE = "proprioceptive"
    SYMBOLIC = "symbolic"
    ABSTRACT = "abstract"


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
    grounding_links: List[str]
    attention_weight: float


class UCRTyped(TypedDict):
    """严格类型的 UCR 表示"""
    entity_type: str
    symbol: str
    content: str
    vector: Optional[List[float]]
    metadata: UCRMetadata


class UCRContainer(TypedDict, total=False):
    """UCR 容器类型 - 用于认知循环输入输出"""
    ucrs: List[UCRTyped]
    phase: str
    timestamp: str
    processing_metadata: Dict[str, str]


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
    CORRELATES_WITH = "correlates_with"
    ANTAGONIZES = "antagonizes"


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


class GraphSubgraph(TypedDict):
    """子图类型"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    center_node: str
    max_depth: int


# ============================================================================
# 工作记忆类型 (基于认知科学理论)
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
    decay_rate: float


class WorkingMemoryState(TypedDict):
    """工作记忆状态"""
    items: List[WorkingMemoryItemTyped]
    capacity: int
    current_load: float
    focus_of_attention: List[str]


# ============================================================================
# 注意力机制类型
# ============================================================================

class AttentionType(Enum):
    """注意力类型"""
    SELECTIVE = "selective"  # 选择性注意
    DIVIDED = "divided"  # 分配性注意
    SUSTAINED = "sustained"  # 持续性注意
    ALTERNATING = "alternating"  # 交替性注意


class AttentionFocus(TypedDict):
    """注意力焦点类型"""
    target_id: str
    relevance_score: float
    priority: float
    duration_ms: int
    attention_type: str


class AttentionState(TypedDict):
    """注意力状态"""
    current_focus: Optional[AttentionFocus]
    focus_history: List[AttentionFocus]
    attentional_resources: float
    blink_periods: List[Tuple[int, int]]  # 注意瞬脱周期


class AttentionConfig(TypedDict, total=False):
    """注意力配置"""
    capacity_limit: float
    filter_threshold: float
    blink_duration_ms: int
    recovery_time_ms: int


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


class CognitiveEvent(TypedDict):
    """认知事件类型"""
    phase: str
    timestamp: str
    input_summary: str
    output_summary: str
    metadata: Dict[str, str]


class CognitiveLoopState(TypedDict):
    """认知循环状态"""
    current_phase: str
    iteration_count: int
    elapsed_time_ms: float
    resource_usage: Dict[str, float]


# ============================================================================
# 因果推理类型 (基于 Pearl 因果理论)
# ============================================================================

class CausalRelation(TypedDict):
    """因果关系类型"""
    cause: str
    effect: str
    strength: float
    mechanism: str
    evidence: List[str]
    confounders: List[str]
    p_cause_given_effect: float
    p_effect_given_cause: float


class CausalGraph(TypedDict):
    """因果图类型"""
    nodes: List[str]
    edges: List[CausalRelation]
    interventions: Dict[str, str]
    adjustment_sets: Dict[str, List[str]]


class InterventionResult(TypedDict):
    """干预结果类型"""
    intervention: str
    outcome: str
    counterfactual: str
    ate: float  # Average Treatment Effect
    confidence_interval: Tuple[float, float]


class StructuralCausalModel(TypedDict):
    """结构因果模型"""
    endogenous_vars: List[str]
    exogenous_vars: List[str]
    structural_equations: Dict[str, str]
    causal_graph: CausalGraph


# ============================================================================
# 符号接地类型 (解决 Symbol Grounding Problem)
# ============================================================================

class GroundingLink(TypedDict):
    """符号接地链接类型"""
    symbol: str
    percept: str
    association_strength: float
    context: str
    learned_at: str
    reinforcement_history: List[float]


class SensorimotorSchema(TypedDict):
    """感觉运动模式类型"""
    action: str
    sensory_prediction: str
    actual_sensation: str
    prediction_error: float
    update_rule: str


class GroundingContext(TypedDict):
    """接地上下文"""
    physical_context: str
    social_context: str
    temporal_context: str
    modalities_involved: List[str]


class SymbolGroundingState(TypedDict):
    """符号接地状态"""
    grounded_symbols: List[GroundingLink]
    ungrounded_symbols: List[str]
    grounding_confidence: Dict[str, float]
    sensorimotor_schemas: List[SensorimotorSchema]


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


@runtime_checkable
class GroundingEngine(Protocol):
    """接地引擎接口"""
    
    def ground_symbol(self, symbol: str, context: GroundingContext) -> GroundingLink:
        """将符号接地到感知经验"""
        ...
    
    def get_grounding_confidence(self, symbol: str) -> float:
        """获取符号的接地置信度"""
        ...


@runtime_checkable
class CausalReasoner(Protocol):
    """因果推理器接口"""
    
    def discover_causes(self, effects: List[str], observations: Dict[str, float]) -> CausalGraph:
        """发现因果关系"""
        ...
    
    def compute_ate(self, treatment: str, outcome: str, data: Dict[str, float]) -> InterventionResult:
        """计算平均处理效应"""
        ...
    
    def do_calculus(self, graph: CausalGraph, intervention: str) -> float:
        """执行 do-calculus"""
        ...


# ============================================================================
# 世界模型类型
# ============================================================================

class StateType(Enum):
    """状态变量类型"""
    CONTINUOUS = "continuous"
    DISCRETE = "discrete"
    CATEGORICAL = "categorical"
    BINARY = "binary"
    ABSTRACT = "abstract"


class StateVariable(TypedDict):
    """状态变量类型"""
    name: str
    value: Union[str, float, int, bool]
    var_type: str
    domain: Optional[List[Union[str, float, int]]]
    uncertainty: float
    timestamp: str
    source: str
    confidence: float


class WorldState(TypedDict):
    """世界状态类型"""
    state_id: str
    variables: Dict[str, StateVariable]
    timestamp: str
    context: Dict[str, str]


class TransitionModel(TypedDict):
    """转移模型类型"""
    from_state: str
    to_state: str
    action: str
    probability: float
    reward: float


# ============================================================================
# 内在动机类型
# ============================================================================

class MotivationType(Enum):
    """动机类型"""
    CURIOSITY = "curiosity"
    COMPETENCE = "competence"
    NOVELTY = "novelty"
    SURPRISE = "surprise"
    INTRINSIC_REWARD = "intrinsic_reward"


class PredictionError(TypedDict):
    """预测误差类型"""
    variable: str
    predicted: Union[str, float, int, bool]
    actual: Union[str, float, int, bool]
    error_magnitude: float
    surprise_level: float


class IntrinsicReward(TypedDict):
    """内在奖励类型"""
    motivation_type: str
    magnitude: float
    source_event: str
    timestamp: str


class GoalRepresentation(TypedDict):
    """目标表示类型"""
    goal_id: str
    description: str
    target_state: WorldState
    current_progress: float
    sub_goals: List[str]
    intrinsic_motivation: List[IntrinsicReward]


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


class ResourceAlert(TypedDict):
    """资源告警类型"""
    resource_type: str
    current_usage: float
    limit: float
    utilization_percent: float
    alert_level: Literal["info", "warning", "critical"]


# ============================================================================
# 安全与验证类型
# ============================================================================

class SecurityLevel(Enum):
    """安全级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InputValidationResult(TypedDict):
    """输入验证结果"""
    is_valid: bool
    sanitized_input: str
    violations: List[str]
    security_level: str


class SandboxedExecutionResult(TypedDict):
    """沙箱执行结果"""
    success: bool
    output: Optional[str]
    error: Optional[str]
    execution_time_ms: float
    resources_used: ResourceUsage
    security_violations: List[str]


# ============================================================================
# 泛型类型变量
# ============================================================================

T = TypeVar('T')
K = TypeVar('K', bound=str)
V = TypeVar('V')
UCR = TypeVar('UCR', bound=UCRTyped)
M = TypeVar('M', bound=Mapping)


# ============================================================================
# 辅助函数类型
# ============================================================================

ValidatorFunc = Callable[[str], InputValidationResult]
TransformerFunc = Callable[[str], UCRTyped]
ScorerFunc = Callable[[UCRTyped], float]
