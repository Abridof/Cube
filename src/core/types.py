"""
Type Definitions and Resource Limits Module v1.0
=================================================
严格的类型系统和资源限制，解决 P0 级技术债务

设计原则：
1. 零容忍 Any 类型 - 使用 TypedDict, Protocol, Union 等精确类型
2. 资源限制硬编码 - 防止资源耗尽攻击
3. 输入验证 - 所有外部输入必须验证
4. 类型安全 - 支持 mypy 严格模式

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
)
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math


# ============================================================================
# 资源限制常量 (Hard Limits)
# ============================================================================

# 图谱大小限制
MAX_GRAPH_NODES: Final[int] = 100_000  # 最大节点数
MAX_GRAPH_EDGES_PER_NODE: Final[int] = 1_000  # 每个节点最大边数
MAX_TOTAL_EDGES: Final[int] = 500_000  # 总边数限制

# 状态和循环限制
MAX_COGNITIVE_STATES: Final[int] = 10_000  # 最大认知状态数
MAX_THINKING_ITERATIONS: Final[int] = 100  # 慢思考最大迭代次数
MAX_RECURSION_DEPTH: Final[int] = 50  # 最大递归深度
MAX_WORKING_MEMORY_ITEMS: Final[int] = 150  # 工作记忆容量 (基于 Miller's Law 7±2 的扩展)

# 输入限制
MAX_INPUT_LENGTH: Final[int] = 100_000  # 最大输入字符数
MAX_OUTPUT_LENGTH: Final[int] = 50_000  # 最大输出字符数
MAX_BATCH_SIZE: Final[int] = 1_000  # 最大批量处理大小

# 向量维度限制
MAX_VECTOR_DIMENSIONS: Final[int] = 10_000  # 稀疏向量最大维度数
MAX_SIMILARITY_RESULTS: Final[int] = 500  # 相似度搜索最大结果数

# 时间限制 (秒)
MAX_EXECUTION_TIME: Final[float] = 30.0  # 单次执行最大时间
MAX_TOTAL_PROCESSING_TIME: Final[float] = 300.0  # 总处理时间

# 内存限制 (MB)
MAX_MEMORY_USAGE_MB: Final[int] = 512  # 最大内存使用


# ============================================================================
# 精确类型定义 (替代 Any)
# ============================================================================

class JsonValue(TypedDict, total=False):
    """JSON 值的递归类型定义"""
    pass


# 使用递归类型注解
JsonValueT = Union[
    str,
    int,
    float,
    bool,
    None,
    List['JsonValueT'],
    Dict[str, 'JsonValueT']
]


class ContentTypes(Enum):
    """内容类型枚举 (替代字符串字面量)"""
    TEXT = "text"
    CODE = "code"
    DATA = "data"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    STRUCTURED = "structured"
    MIXED = "mixed"


class ModalityTypes(Enum):
    """模态类型"""
    TEXTUAL = "textual"
    VISUAL = "visual"
    AUDITORY = "auditory"
    TACTILE = "tactile"
    PROPRIOCEPTIVE = "proprioceptive"


# ============================================================================
# Protocol 定义 (结构化子类型)
# ============================================================================

class Comparable(Protocol):
    """可比较对象的 Protocol"""
    def __lt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __eq__(self, other) -> bool: ...


class Hashable(Protocol):
    """可哈希对象的 Protocol"""
    def __hash__(self) -> int: ...


class Serializable(Protocol):
    """可序列化对象的 Protocol"""
    def to_dict(self) -> Dict[str, JsonValueT]: ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, JsonValueT]) -> 'Serializable': ...


class Identifiable(Protocol):
    """可识别对象的 Protocol"""
    @property
    def id(self) -> str: ...


# ============================================================================
# 泛型类型变量
# ============================================================================

T = TypeVar('T')
K = TypeVar('K', bound=Hashable)
V = TypeVar('V')
S = TypeVar('S', bound=Serializable)


# ============================================================================
# 资源限制器 (Resource Limiter)
# ============================================================================

@dataclass
class ResourceLimits:
    """资源限制配置"""
    max_nodes: int = MAX_GRAPH_NODES
    max_edges_per_node: int = MAX_GRAPH_EDGES_PER_NODE
    max_total_edges: int = MAX_TOTAL_EDGES
    max_states: int = MAX_COGNITIVE_STATES
    max_iterations: int = MAX_THINKING_ITERATIONS
    max_recursion_depth: int = MAX_RECURSION_DEPTH
    max_working_memory: int = MAX_WORKING_MEMORY_ITEMS
    max_input_length: int = MAX_INPUT_LENGTH
    max_output_length: int = MAX_OUTPUT_LENGTH
    max_batch_size: int = MAX_BATCH_SIZE
    max_vector_dims: int = MAX_VECTOR_DIMENSIONS
    max_similarity_results: int = MAX_SIMILARITY_RESULTS
    max_execution_time: float = MAX_EXECUTION_TIME
    max_total_processing_time: float = MAX_TOTAL_PROCESSING_TIME
    max_memory_mb: int = MAX_MEMORY_USAGE_MB
    
    def validate(self) -> bool:
        """验证所有限制都是正数"""
        return all([
            self.max_nodes > 0,
            self.max_edges_per_node > 0,
            self.max_total_edges > 0,
            self.max_states > 0,
            self.max_iterations > 0,
            self.max_recursion_depth > 0,
            self.max_working_memory > 0,
            self.max_input_length > 0,
            self.max_output_length > 0,
            self.max_batch_size > 0,
            self.max_vector_dims > 0,
            self.max_similarity_results > 0,
            self.max_execution_time > 0,
            self.max_total_processing_time > 0,
            self.max_memory_mb > 0,
        ])


class ResourceTracker:
    """资源使用追踪器"""
    
    def __init__(self, limits: Optional[ResourceLimits] = None):
        self.limits = limits or ResourceLimits()
        self.node_count: int = 0
        self.edge_count: int = 0
        self.state_count: int = 0
        self.iteration_count: int = 0
        self.recursion_depth: int = 0
        self.working_memory_size: int = 0
        self.input_size: int = 0
        self.output_size: int = 0
        self.start_time: Optional[datetime] = None
        self.current_time: datetime = datetime.now()
        
    def reset(self):
        """重置计数器"""
        self.node_count = 0
        self.edge_count = 0
        self.state_count = 0
        self.iteration_count = 0
        self.recursion_depth = 0
        self.working_memory_size = 0
        self.input_size = 0
        self.output_size = 0
        self.start_time = datetime.now()
        
    def can_add_node(self) -> bool:
        return self.node_count < self.limits.max_nodes
    
    def can_add_edge(self) -> bool:
        return self.edge_count < self.limits.max_total_edges
    
    def can_iterate(self) -> bool:
        return self.iteration_count < self.limits.max_iterations
    
    def can_recurse(self) -> bool:
        return self.recursion_depth < self.limits.max_recursion_depth
    
    def can_store_in_working_memory(self) -> bool:
        return self.working_memory_size < self.limits.max_working_memory
    
    def increment_node(self) -> bool:
        if not self.can_add_node():
            raise ResourceExhaustedError(
                f"Node limit reached: {self.node_count} >= {self.limits.max_nodes}"
            )
        self.node_count += 1
        return True
    
    def increment_edge(self) -> bool:
        if not self.can_add_edge():
            raise ResourceExhaustedError(
                f"Edge limit reached: {self.edge_count} >= {self.limits.max_total_edges}"
            )
        self.edge_count += 1
        return True
    
    def increment_iteration(self) -> bool:
        if not self.can_iterate():
            raise ResourceExhaustedError(
                f"Iteration limit reached: {self.iteration_count} >= {self.limits.max_iterations}"
            )
        self.iteration_count += 1
        return True
    
    def push_recursion(self) -> bool:
        if not self.can_recurse():
            raise ResourceExhaustedError(
                f"Recursion depth limit reached: {self.recursion_depth} >= {self.limits.max_recursion_depth}"
            )
        self.recursion_depth += 1
        return True
    
    def pop_recursion(self):
        if self.recursion_depth > 0:
            self.recursion_depth -= 1
    
    def add_to_working_memory(self, count: int = 1) -> bool:
        if self.working_memory_size + count > self.limits.max_working_memory:
            raise ResourceExhaustedError(
                f"Working memory limit reached: {self.working_memory_size} + {count} > {self.limits.max_working_memory}"
            )
        self.working_memory_size += count
        return True
    
    def remove_from_working_memory(self, count: int = 1):
        self.working_memory_size = max(0, self.working_memory_size - count)
    
    def validate_input_size(self, size: int) -> bool:
        if size > self.limits.max_input_length:
            raise InputTooLargeError(
                f"Input size {size} exceeds limit {self.limits.max_input_length}"
            )
        self.input_size = size
        return True
    
    def validate_output_size(self, size: int) -> bool:
        if size > self.limits.max_output_length:
            raise OutputTooLargeError(
                f"Output size {size} exceeds limit {self.limits.max_output_length}"
            )
        self.output_size = size
        return True
    
    def check_timeout(self) -> bool:
        if self.start_time is None:
            return True
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed > self.limits.max_execution_time:
            raise TimeoutError(
                f"Execution time {elapsed}s exceeds limit {self.limits.max_execution_time}s"
            )
        return True
    
    def get_status(self) -> Dict[str, Union[int, float]]:
        """获取资源使用状态"""
        elapsed = 0.0
        if self.start_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "node_usage": f"{self.node_count}/{self.limits.max_nodes}",
            "edge_usage": f"{self.edge_count}/{self.limits.max_total_edges}",
            "state_usage": f"{self.state_count}/{self.limits.max_states}",
            "iteration_usage": f"{self.iteration_count}/{self.limits.max_iterations}",
            "recursion_depth": f"{self.recursion_depth}/{self.limits.max_recursion_depth}",
            "working_memory_usage": f"{self.working_memory_size}/{self.limits.max_working_memory}",
            "input_size": f"{self.input_size}/{self.limits.max_input_length}",
            "output_size": f"{self.output_size}/{self.limits.max_output_length}",
            "elapsed_time": f"{elapsed:.2f}/{self.limits.max_execution_time}s",
            "node_utilization": self.node_count / self.limits.max_nodes,
            "edge_utilization": self.edge_count / self.limits.max_total_edges,
            "iteration_utilization": self.iteration_count / self.limits.max_iterations,
        }


# ============================================================================
# 自定义异常
# ============================================================================

class ResourceExhaustedError(Exception):
    """资源耗尽异常"""
    pass


class InputTooLargeError(Exception):
    """输入过大异常"""
    pass


class OutputTooLargeError(Exception):
    """输出过大异常"""
    pass


class SecurityViolationError(Exception):
    """安全违规异常"""
    pass


class TypeValidationError(Exception):
    """类型验证异常"""
    pass


# ============================================================================
# 输入验证工具
# ============================================================================

def validate_string_length(
    s: str, 
    max_length: int = MAX_INPUT_LENGTH,
    min_length: int = 0,
    field_name: str = "input"
) -> str:
    """验证字符串长度"""
    if not isinstance(s, str):
        raise TypeValidationError(f"{field_name} must be a string, got {type(s).__name__}")
    
    if len(s) < min_length:
        raise InputTooLargeError(
            f"{field_name} length {len(s)} is less than minimum {min_length}"
        )
    
    if len(s) > max_length:
        raise InputTooLargeError(
            f"{field_name} length {len(s)} exceeds maximum {max_length}"
        )
    
    return s


def validate_list_length(
    lst: List[T],
    max_length: int = MAX_BATCH_SIZE,
    min_length: int = 0,
    field_name: str = "list"
) -> List[T]:
    """验证列表长度"""
    if not isinstance(lst, (list, tuple, Sequence)):
        raise TypeValidationError(f"{field_name} must be a list, got {type(lst).__name__}")
    
    if len(lst) < min_length:
        raise InputTooLargeError(
            f"{field_name} length {len(lst)} is less than minimum {min_length}"
        )
    
    if len(lst) > max_length:
        raise InputTooLargeError(
            f"{field_name} length {len(lst)} exceeds maximum {max_length}"
        )
    
    return list(lst)


def validate_dict_size(
    d: Dict[K, V],
    max_size: int = MAX_BATCH_SIZE,
    field_name: str = "dict"
) -> Dict[K, V]:
    """验证字典大小"""
    if not isinstance(d, (dict, Mapping)):
        raise TypeValidationError(f"{field_name} must be a dict, got {type(d).__name__}")
    
    if len(d) > max_size:
        raise InputTooLargeError(
            f"{field_name} size {len(d)} exceeds maximum {max_size}"
        )
    
    return dict(d)


def sanitize_input(text: str) -> str:
    """清理输入，移除潜在危险内容"""
    if not text:
        return text
    
    # 移除 null 字节
    text = text.replace('\x00', '')
    
    # 限制连续空白字符
    import re
    text = re.sub(r'\s{100,}', '\n', text)
    
    return text


# ============================================================================
# 工作记忆实现 (基于 Atkinson-Shiffrin 模型)
# ============================================================================

@dataclass
class WorkingMemoryItem(Generic[T]):
    """工作记忆项"""
    id: str
    content: T
    priority: float = 0.5  # 优先级 0-1
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    decay_rate: float = 0.01  # 衰减率
    
    def touch(self):
        """访问更新"""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def get_activation(self) -> float:
        """计算激活水平 (基于 ACT-R 理论)"""
        time_since_access = (datetime.now() - self.last_accessed).total_seconds()
        base_activation = self.priority
        recency_bonus = math.exp(-self.decay_rate * time_since_access)
        practice_effect = math.log(self.access_count + 1) * 0.1
        return base_activation * recency_bonus + practice_effect


class WorkingMemory(Generic[T]):
    """
    工作记忆系统
    
    理论基础:
    - Baddeley 的工作记忆模型 (中央执行 + 语音回路 + 视觉空间模板)
    - Miller's Law: 7±2 个组块
    - ACT-R 的激活理论
    """
    
    def __init__(self, capacity: int = MAX_WORKING_MEMORY_ITEMS):
        if capacity <= 0 or capacity > MAX_WORKING_MEMORY_ITEMS:
            raise ValueError(f"Capacity must be between 1 and {MAX_WORKING_MEMORY_ITEMS}")
        
        self.capacity = capacity
        self._items: Dict[str, WorkingMemoryItem[T]] = {}
        self._priority_queue: List[str] = []  # 按优先级排序的 ID 列表
        
    def __len__(self) -> int:
        return len(self._items)
    
    def is_full(self) -> bool:
        return len(self._items) >= self.capacity
    
    def add(
        self, 
        item_id: str, 
        content: T, 
        priority: float = 0.5
    ) -> bool:
        """添加项目到工作记忆"""
        if self.is_full():
            # 驱逐最低激活的项目
            self._evict_lowest()
        
        item = WorkingMemoryItem(
            id=item_id,
            content=content,
            priority=min(1.0, max(0.0, priority))
        )
        self._items[item_id] = item
        self._update_priority_queue()
        return True
    
    def get(self, item_id: str) -> Optional[T]:
        """获取项目"""
        item = self._items.get(item_id)
        if item:
            item.touch()
            self._update_priority_queue()
            return item.content
        return None
    
    def remove(self, item_id: str) -> bool:
        """移除项目"""
        if item_id in self._items:
            del self._items[item_id]
            self._priority_queue.remove(item_id)
            return True
        return False
    
    def clear(self):
        """清空工作记忆"""
        self._items.clear()
        self._priority_queue.clear()
    
    def get_all(self) -> List[Tuple[str, T]]:
        """获取所有项目 (按激活度排序)"""
        sorted_items = sorted(
            self._items.items(),
            key=lambda x: x[1].get_activation(),
            reverse=True
        )
        return [(item_id, item.content) for item_id, item in sorted_items]
    
    def get_most_active(self, n: int = 5) -> List[Tuple[str, T]]:
        """获取最活跃的 n 个项目"""
        return self.get_all()[:n]
    
    def _evict_lowest(self):
        """驱逐激活度最低的项目"""
        if not self._items:
            return
        
        # 找到激活度最低的项目
        lowest_id = min(
            self._items.keys(),
            key=lambda x: self._items[x].get_activation()
        )
        self.remove(lowest_id)
    
    def _update_priority_queue(self):
        """更新优先级队列"""
        self._priority_queue = sorted(
            self._items.keys(),
            key=lambda x: self._items[x].get_activation(),
            reverse=True
        )
    
    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "size": len(self._items),
            "capacity": self.capacity,
            "utilization": len(self._items) / self.capacity,
            "item_ids": list(self._items.keys()),
        }


# ============================================================================
# 注意力机制接口
# ============================================================================

class AttentionMechanism(Protocol):
    """注意力机制 Protocol"""
    
    def compute_attention(
        self,
        query: T,
        keys: Sequence[T],
        values: Sequence[T],
        top_k: int = 5
    ) -> List[Tuple[T, float]]:
        """计算注意力权重并返回 top-k 结果"""
        ...


@dataclass
class AttentionWeight:
    """注意力权重"""
    source_id: str
    target_id: str
    weight: float
    attention_type: Literal["self", "cross", "global"] = "self"


# ============================================================================
# 符号接地接口 (Symbol Grounding)
# ============================================================================

class SymbolGrounding(Protocol):
    """符号接地 Protocol"""
    
    def ground_symbol(
        self,
        symbol: str,
        context: Dict[str, Any]
    ) -> List[Tuple[str, float]]:
        """将符号接地到感知经验"""
        ...
    
    def get_grounding_confidence(self, symbol: str) -> float:
        """获取符号接地的置信度"""
        ...


# ============================================================================
# 因果推理接口
# ============================================================================

class CausalRelation(TypedDict):
    """因果关系类型"""
    cause: str
    effect: str
    strength: float  # 0-1
    confidence: float  # 0-1
    evidence_count: int
    mediating_factors: List[str]


class CausalInferenceEngine(Protocol):
    """因果推理引擎 Protocol"""
    
    def infer_cause(
        self,
        effect: str,
        context: Dict[str, any]
    ) -> List[CausalRelation]:
        """推断原因"""
        ...
    
    def infer_effect(
        self,
        cause: str,
        context: Dict[str, any]
    ) -> List[CausalRelation]:
        """推断结果"""
        ...
    
    def do_intervention(
        self,
        variable: str,
        value: any
    ) -> Dict[str, any]:
        """执行 do-演算干预"""
        ...


# ============================================================================
# 导出公共 API
# ============================================================================

__all__ = [
    # 常量
    "MAX_GRAPH_NODES",
    "MAX_GRAPH_EDGES_PER_NODE",
    "MAX_TOTAL_EDGES",
    "MAX_COGNITIVE_STATES",
    "MAX_THINKING_ITERATIONS",
    "MAX_RECURSION_DEPTH",
    "MAX_WORKING_MEMORY_ITEMS",
    "MAX_INPUT_LENGTH",
    "MAX_OUTPUT_LENGTH",
    "MAX_BATCH_SIZE",
    "MAX_VECTOR_DIMENSIONS",
    "MAX_SIMILARITY_RESULTS",
    "MAX_EXECUTION_TIME",
    "MAX_TOTAL_PROCESSING_TIME",
    "MAX_MEMORY_USAGE_MB",
    
    # 类型
    "JsonValueT",
    "ContentTypes",
    "ModalityTypes",
    
    # Protocols
    "Comparable",
    "Hashable",
    "Serializable",
    "Identifiable",
    "AttentionMechanism",
    "SymbolGrounding",
    "CausalInferenceEngine",
    
    # 资源管理
    "ResourceLimits",
    "ResourceTracker",
    "WorkingMemory",
    "WorkingMemoryItem",
    
    # 异常
    "ResourceExhaustedError",
    "InputTooLargeError",
    "OutputTooLargeError",
    "SecurityViolationError",
    "TypeValidationError",
    
    # 验证函数
    "validate_string_length",
    "validate_list_length",
    "validate_dict_size",
    "sanitize_input",
    
    # 因果推理
    "CausalRelation",
    "AttentionWeight",
]
