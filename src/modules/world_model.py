"""
世界模型模块 - World Model Module
====================================
第四阶段核心突破：构建内部环境模拟与预测能力

功能:
- 状态空间建模与演化
- 因果推理与预测
- 反事实推理（"如果...会怎样"）
- 心理理论（建模其他智能体）
- 自我模型（元认知）

作者：AI Cognition Engine Team
版本：v8.0
"""

import time
import json
import hashlib
import random
from typing import Dict, List, Optional, Tuple, Set, Callable, Union, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import copy

# Import strict types - 使用精确类型替代 Any
from src.core.strict_types import (
    JsonValueT, 
    StateVariable as TypedStateVariable, 
    WorldState,
    StateType as TypedStateType,
)
from src.core.types import (
    validate_string_length,
    validate_list_length,
    validate_dict_size,
    sanitize_input,
    ResourceTracker,
    MAX_GRAPH_NODES,
    MAX_THINKING_ITERATIONS,
    MAX_WORKING_MEMORY_ITEMS,
)

# ==================== 核心数据结构 ====================


class StateType(Enum):
    """状态类型枚举"""

    PHYSICAL = "physical"  # 物理状态（位置、速度等）
    COGNITIVE = "cognitive"  # 认知状态（信念、知识）
    EMOTIONAL = "emotional"  # 情感状态（ valence, arousal）
    SOCIAL = "social"  # 社会状态（关系、角色）
    ENVIRONMENTAL = "environmental"  # 环境状态（温度、光照等）
    ABSTRACT = "abstract"  # 抽象状态（概念、理论）


class TransitionType(Enum):
    """状态转移类型"""

    DETERMINISTIC = "deterministic"  # 确定性转移
    PROBABILISTIC = "probabilistic"  # 概率性转移
    CONDITIONAL = "conditional"  # 条件转移
    LEARNED = "learned"  # 学习到的转移
    RULE_BASED = "rule_based"  # 基于规则的转移


@dataclass
class StateVariable:
    """状态变量 - 世界模型的基本组成单元
    
    类型安全改进:
    - value: Union[str, float, int, bool] 替代 Any
    - domain: Optional[List[Union[str, float, int]]] 替代 List[Any]
    """

    name: str
    value: Union[str, float, int, bool]
    var_type: StateType
    domain: Optional[List[Union[str, float, int]]] = None  # 离散值域或连续范围 [min, max]
    uncertainty: float = 0.0  # 不确定性 [0, 1]
    timestamp: float = field(default_factory=time.time)
    source: str = "sensor"  # 来源：sensor, inference, prediction
    confidence: float = 1.0  # 置信度
    
    def __post_init__(self):
        """验证字段类型和长度"""
        validate_string_length(self.name, max_length=256, field_name="StateVariable.name")
        if isinstance(self.value, str):
            validate_string_length(self.value, max_length=10000, field_name="StateVariable.value")
        if self.domain and len(self.domain) > MAX_GRAPH_NODES:
            raise ValueError(f"Domain size {len(self.domain)} exceeds limit {MAX_GRAPH_NODES}")

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "var_type": self.var_type.value,
            "domain": self.domain,
            "uncertainty": self.uncertainty,
            "timestamp": self.timestamp,
            "source": self.source,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "StateVariable":
        return cls(
            name=data["name"],
            value=data["value"],
            var_type=StateType(data["var_type"]),
            domain=data.get("domain"),
            uncertainty=data.get("uncertainty", 0.0),
            timestamp=data.get("timestamp", time.time()),
            source=data.get("source", "sensor"),
            confidence=data.get("confidence", 1.0),
        )


@dataclass
class State:
    """完整状态 - 所有状态变量的集合
    
    类型安全改进:
    - context: Dict[str, JsonValueT] 替代 Dict[str, Any]
    - get_value 返回 Union[str, float, int, bool, None] 替代 Any
    - set_value 接受 Union[str, float, int, bool] 替代 Any
    """

    state_id: str
    variables: Dict[str, StateVariable] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, JsonValueT] = field(default_factory=dict)

    def __post_init__(self):
        """验证状态 ID 和上下文大小"""
        validate_string_length(self.state_id, max_length=256, field_name="State.state_id")
        validate_dict_size(self.context, max_size=MAX_BATCH_SIZE, field_name="State.context")

    def add_variable(self, var: StateVariable) -> None:
        """添加状态变量，检查资源限制"""
        if len(self.variables) >= MAX_GRAPH_NODES:
            raise ValueError(f"Cannot add more variables: limit {MAX_GRAPH_NODES} reached")
        self.variables[var.name] = var

    def get_value(self, var_name: str) -> Optional[Union[str, float, int, bool]]:
        """获取变量值，类型安全的返回值"""
        var = self.variables.get(var_name)
        if isinstance(var, StateVariable):
            return var.value
        return None

    def set_value(
        self, 
        var_name: str, 
        value: Union[str, float, int, bool], 
        var_type: StateType = StateType.ABSTRACT
    ) -> None:
        if var_name in self.variables:
            self.variables[var_name].value = value
            self.variables[var_name].timestamp = time.time()
        else:
            self.add_variable(StateVariable(name=var_name, value=value, var_type=var_type))

    def similarity(self, other: "State") -> float:
        """计算两个状态的相似度"""
        common_vars = set(self.variables.keys()) & set(other.variables.keys())
        if not common_vars:
            return 0.0

        similarities = []
        for var_name in common_vars:
            v1 = self.variables[var_name].value
            v2 = other.variables[var_name].value

            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                # 数值相似度
                max_val = max(abs(v1), abs(v2), 1e-10)
                sim = 1.0 - abs(v1 - v2) / max_val
                similarities.append(max(0, sim))
            else:
                # 离散值相似度
                similarities.append(1.0 if v1 == v2 else 0.0)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def to_dict(self) -> Dict:
        return {
            "state_id": self.state_id,
            "variables": {k: v.to_dict() for k, v in self.variables.items()},
            "timestamp": self.timestamp,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "State":
        state = cls(
            state_id=data["state_id"],
            timestamp=data.get("timestamp", time.time()),
            context=data.get("context", {}),
        )
        for k, v in data.get("variables", {}).items():
            state.variables[k] = StateVariable.from_dict(v)
        return state


@dataclass
class Transition:
    """状态转移 - 描述从一个状态到另一个状态的变化
    
    类型安全改进:
    - conditions: Dict[str, JsonValueT] 替代 Dict[str, Any]
    - causal_graph: Dict[str, List[JsonValueT]] 替代 Dict[str, List[str]]
    """

    transition_id: str
    from_state_id: str
    to_state_id: str
    action: Optional[str] = None  # 触发动作
    conditions: Dict[str, JsonValueT] = field(default_factory=dict)  # 触发条件
    probability: float = 1.0  # 转移概率
    transition_type: TransitionType = TransitionType.DETERMINISTIC
    causal_graph: Dict[str, List[JsonValueT]] = field(default_factory=dict)  # 因果图
    learned_at: float = field(default_factory=time.time)
    support_count: int = 0  # 支持此转移的观测次数
    
    def __post_init__(self):
        """验证资源限制"""
        validate_string_length(self.transition_id, max_length=256, field_name="Transition.transition_id")
        validate_dict_size(self.conditions, max_size=MAX_BATCH_SIZE, field_name="Transition.conditions")
        validate_dict_size(self.causal_graph, max_size=MAX_BATCH_SIZE, field_name="Transition.causal_graph")

    def to_dict(self) -> Dict:
        return {
            "transition_id": self.transition_id,
            "from_state_id": self.from_state_id,
            "to_state_id": self.to_state_id,
            "action": self.action,
            "conditions": self.conditions,
            "probability": self.probability,
            "transition_type": self.transition_type.value,
            "causal_graph": self.causal_graph,
            "learned_at": self.learned_at,
            "support_count": self.support_count,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Transition":
        return cls(
            transition_id=data["transition_id"],
            from_state_id=data["from_state_id"],
            to_state_id=data["to_state_id"],
            action=data.get("action"),
            conditions=data.get("conditions", {}),
            probability=data.get("probability", 1.0),
            transition_type=TransitionType(data.get("transition_type", "deterministic")),
            causal_graph=data.get("causal_graph", {}),
            learned_at=data.get("learned_at", time.time()),
            support_count=data.get("support_count", 0),
        )


@dataclass
class Prediction:
    """预测结果"""

    predicted_state: State
    confidence: float
    prediction_horizon: int  # 预测步数
    uncertainty_sources: List[str] = field(default_factory=list)
    alternative_outcomes: List[Tuple[State, float]] = field(default_factory=list)  # (状态，概率)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        return {
            "predicted_state": self.predicted_state.to_dict(),
            "confidence": self.confidence,
            "prediction_horizon": self.prediction_horizon,
            "uncertainty_sources": self.uncertainty_sources,
            "alternative_outcomes": [(s.to_dict(), p) for s, p in self.alternative_outcomes],
            "timestamp": self.timestamp,
        }


@dataclass
class Counterfactual:
    """反事实推理结果
    
    类型安全改进:
    - difference_analysis: Dict[str, JsonValueT] 替代 Dict[str, Any]
    - causal_chain: List[str] 保持精确类型
    """

    premise: str  # 前提："如果 X 发生"
    actual_outcome: State  # 实际结果
    counterfactual_outcome: State  # 反事实结果
    difference_analysis: Dict[str, JsonValueT]  # 差异分析
    causal_chain: List[str] = field(default_factory=list)  # 因果链
    plausibility: float = 0.0  # 合理性评分
    
    def __post_init__(self):
        """验证资源限制"""
        validate_string_length(self.premise, max_length=1000, field_name="Counterfactual.premise")
        validate_dict_size(self.difference_analysis, max_size=MAX_BATCH_SIZE, field_name="Counterfactual.difference_analysis")
        validate_list_length(self.causal_chain, max_length=MAX_THINKING_ITERATIONS, field_name="Counterfactual.causal_chain")


# ==================== 世界模型核心引擎 ====================


class WorldModel:
    """
    世界模型 - 内部环境模拟与预测引擎

    核心能力:
    1. 状态表示：用状态变量构建世界的内部表示
    2. 动态学习：从观测中学习状态转移规律
    3. 前向预测：基于当前状态预测未来
    4. 反事实推理：探索"如果...会怎样"的场景
    5. 因果发现：识别变量间的因果关系
    6. 自我模型：对自身认知过程的建模
    """

    def __init__(self, model_id: str = "default_world"):
        self.model_id = model_id
        self.states: Dict[str, State] = {}
        self.transitions: Dict[str, Transition] = {}
        self.causal_graph: Dict[str, Set[str]] = defaultdict(set)  # 因果图：cause -> effects
        self.current_state_id: Optional[str] = None

        # 学习参数
        self.min_support = 3  # 最小支持次数才能学习转移
        self.similarity_threshold = 0.8  # 状态相似度阈值
        self.prediction_decay = 0.95  # 预测置信度随步数衰减

        # 统计信息
        self.observation_count = 0
        self.prediction_count = 0
        self.prediction_accuracy = []

        # 自我模型
        self.self_model = {
            "capabilities": [],
            "limitations": [],
            "beliefs_about_self": {},
            "meta_cognitive_state": "unknown",
        }

    def _generate_id(self, prefix: str) -> str:
        """生成唯一 ID"""
        timestamp = str(time.time())
        random_suffix = str(random.random())[2:8]
        hash_input = f"{prefix}_{timestamp}_{random_suffix}"
        return f"{prefix}_{hashlib.sha256(hash_input.encode()).hexdigest()[:16]}"

    # ========== 状态管理 ==========

    def observe(
        self, variables: Dict[str, Tuple[Any, StateType]], context: Optional[Dict] = None
    ) -> State:
        """
        观测并创建新状态

        Args:
            variables: {var_name: (value, var_type)}
            context: 可选上下文信息

        Returns:
            创建的 State 对象
        """
        state = State(state_id=self._generate_id("state"), context=context or {})

        for var_name, (value, var_type) in variables.items():
            state.add_variable(
                StateVariable(name=var_name, value=value, var_type=var_type, source="sensor")
            )

        self.states[state.state_id] = state

        # 学习状态转移
        if self.current_state_id:
            self._learn_transition(self.current_state_id, state.state_id)

        self.current_state_id = state.state_id
        self.observation_count += 1

        return state

    def get_current_state(self) -> Optional[State]:
        """获取当前状态"""
        if self.current_state_id:
            return self.states.get(self.current_state_id)
        return None

    def _find_similar_state(self, state: State, threshold: float = None) -> Optional[str]:
        """查找相似状态"""
        threshold = threshold or self.similarity_threshold

        for state_id, existing_state in self.states.items():
            if state_id == state.state_id:
                continue
            sim = state.similarity(existing_state)
            if sim >= threshold:
                return state_id
        return None

    # ========== 转移学习 ==========

    def _learn_transition(self, from_id: str, to_id: str, action: str = None):
        """学习状态转移"""
        # 检查是否已有类似转移
        for trans in self.transitions.values():
            if trans.from_state_id == from_id and trans.action == action:
                # 更新现有转移
                trans.support_count += 1
                trans.to_state_id = to_id  # 更新为最新观测
                return

        # 创建新转移
        transition = Transition(
            transition_id=self._generate_id("trans"),
            from_state_id=from_id,
            to_state_id=to_id,
            action=action,
            support_count=1,
            transition_type=TransitionType.LEARNED,
        )

        # 推断因果关系
        self._infer_causality(from_id, to_id, transition)

        self.transitions[transition.transition_id] = transition

    def _infer_causality(self, from_id: str, to_id: str, transition: Transition):
        """推断因果关系"""
        from_state = self.states.get(from_id)
        to_state = self.states.get(to_id)

        if not from_state or not to_state:
            return

        # 简单因果推断：如果 A 变化后 B 总是变化，则 A->B
        for var_name, from_var in from_state.variables.items():
            for to_var_name, to_var in to_state.variables.items():
                if var_name != to_var_name:
                    # 记录潜在因果关系
                    self.causal_graph[var_name].add(to_var_name)
                    transition.causal_graph.setdefault(var_name, []).append(to_var_name)

    # ========== 预测引擎 ==========

    def predict(self, steps: int = 1, action: str = None) -> Optional[Prediction]:
        """
        前向预测

        Args:
            steps: 预测步数
            action: 可选的动作序列

        Returns:
            Prediction 对象
        """
        current = self.get_current_state()
        if not current:
            return None

        predicted_states = [current]
        uncertainties = []
        alternatives = []

        for step in range(steps):
            prev_state = predicted_states[-1]

            # 找到适用的转移
            applicable_transitions = []
            for trans in self.transitions.values():
                if trans.from_state_id == prev_state.state_id:
                    if action is None or trans.action == action:
                        applicable_transitions.append(trans)

            if not applicable_transitions:
                # 没有已知转移，使用最相似状态的转移
                similar_id = self._find_similar_state(prev_state)
                if similar_id:
                    for trans in self.transitions.values():
                        if trans.from_state_id == similar_id:
                            applicable_transitions.append(trans)

            if not applicable_transitions:
                break

            # 选择最可能的转移
            best_trans = max(applicable_transitions, key=lambda t: t.support_count)

            # 获取预测状态
            next_state = self.states.get(best_trans.to_state_id)
            if next_state:
                # 复制并更新时间戳
                new_state = State.from_dict(next_state.to_dict())
                new_state.state_id = self._generate_id("pred")
                new_state.timestamp = time.time()

                # 增加不确定性
                for var in new_state.variables.values():
                    var.uncertainty = min(1.0, var.uncertainty + 0.1 * (step + 1))
                    var.source = "prediction"

                predicted_states.append(new_state)
                uncertainties.append(best_trans.probability)

                # 生成替代结果（如果有概率性转移）
                if best_trans.transition_type == TransitionType.PROBABILISTIC:
                    for other_trans in applicable_transitions:
                        if other_trans != best_trans:
                            alt_state = self.states.get(other_trans.to_state_id)
                            if alt_state:
                                alternatives.append((alt_state, other_trans.probability))

        if len(predicted_states) < 2:
            return None

        final_state = predicted_states[-1]
        confidence = sum(uncertainties) / len(uncertainties) if uncertainties else 0.5
        confidence *= self.prediction_decay**steps

        prediction = Prediction(
            predicted_state=final_state,
            confidence=confidence,
            prediction_horizon=steps,
            uncertainty_sources=[f"step_{i}" for i in range(len(predicted_states) - 1)],
            alternative_outcomes=alternatives[:3],  # 最多 3 个替代结果
        )

        self.prediction_count += 1
        return prediction

    def evaluate_prediction(self, actual_state: State, prediction: Prediction) -> float:
        """评估预测准确性"""
        sim = actual_state.similarity(prediction.predicted_state)
        self.prediction_accuracy.append(sim)

        # 保持最近的 100 次评估
        if len(self.prediction_accuracy) > 100:
            self.prediction_accuracy = self.prediction_accuracy[-100:]

        return sim

    # ========== 反事实推理 ==========

    def counterfactual(
        self, 
        intervention: Dict[str, Union[str, float, int, bool]], 
        compare_to: str = "actual"
    ) -> Counterfactual:
        """
        反事实推理："如果 X 发生，会怎样？"
        
        类型安全改进:
        - intervention: Dict[str, Union[str, float, int, bool]] 替代 Dict[str, Any]

        Args:
            intervention: {var_name: new_value} 干预措施
            compare_to: "actual" 或状态 ID

        Returns:
            Counterfactual 对象
        """
        # 验证输入大小
        validate_dict_size(intervention, max_size=MAX_BATCH_SIZE, field_name="intervention")
        current = self.get_current_state()
        if not current:
            raise ValueError("No current state available")

        # 创建干预后的状态
        cf_state = State.from_dict(current.to_dict())
        cf_state.state_id = self._generate_id("counterfactual")

        for var_name, new_value in intervention.items():
            cf_state.set_value(var_name, new_value)

        # 预测干预后的结果
        cf_prediction = self.predict(steps=1)

        # 获取实际结果
        if compare_to == "actual":
            actual_outcome = current
        else:
            actual_outcome = self.states.get(compare_to, current)

        # 分析差异
        diff_analysis = self._analyze_difference(
            actual_outcome, cf_prediction.predicted_state if cf_prediction else cf_state
        )

        # 构建因果链
        causal_chain = []
        for var_name in intervention.keys():
            effects = self.causal_graph.get(var_name, set())
            causal_chain.extend([f"{var_name} -> {e}" for e in effects])

        return Counterfactual(
            premise=f"If {intervention}",
            actual_outcome=actual_outcome,
            counterfactual_outcome=cf_prediction.predicted_state if cf_prediction else cf_state,
            difference_analysis=diff_analysis,
            causal_chain=causal_chain,
            plausibility=self._calculate_plausibility(intervention, current),
        )

    def _analyze_difference(
        self, state1: State, state2: State
    ) -> Dict[str, Union[List[str], Dict[str, Union[str, float, int, None]], int]]:
        """分析两个状态的差异
        
        类型安全改进:
        - 返回精确的 Dict 类型替代 Dict[str, Any]
        """
        differences: Dict[str, Dict[str, Union[str, float, int, None]]] = {}

        all_vars = set(state1.variables.keys()) | set(state2.variables.keys())

        for var_name in all_vars:
            v1 = state1.get_value(var_name)
            v2 = state2.get_value(var_name)

            if v1 != v2:
                change_val: Union[str, float, int, None] = "N/A"
                if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                    change_val = v2 - v1
                    
                differences[var_name] = {
                    "before": v1 if v1 is not None else "None",
                    "after": v2 if v2 is not None else "None",
                    "change": change_val,
                }

        return {
            "changed_variables": list(differences.keys()),
            "details": differences,
            "total_changes": len(differences),
        }

    def _calculate_plausibility(
        self, 
        intervention: Dict[str, Union[str, float, int, bool]], 
        base_state: State
    ) -> float:
        """计算反事实的合理性"""
        plausibility = 1.0

        for var_name, new_value in intervention.items():
            var = base_state.variables.get(var_name)
            if var and var.domain:
                # 检查是否在定义域内
                if isinstance(var.domain, list) and len(var.domain) == 2:
                    # 连续范围
                    min_val, max_val = var.domain
                    if not (min_val <= new_value <= max_val):
                        plausibility *= 0.5
                elif isinstance(var.domain, list):
                    # 离散值
                    if new_value not in var.domain:
                        plausibility *= 0.3

        return plausibility

    # ========== 自我模型 ==========

    def update_self_model(
        self, 
        capability: Optional[str] = None, 
        limitation: Optional[str] = None, 
        belief: Optional[Dict[str, JsonValueT]] = None
    ) -> None:
        """更新自我模型
        
        类型安全改进:
        - belief: Dict[str, JsonValueT] 替代 Dict[str, Any]
        - 添加明确的返回类型
        """
        if capability and capability not in self.self_model["capabilities"]:
            self.self_model["capabilities"].append(capability)

        if limitation and limitation not in self.self_model["limitations"]:
            self.self_model["limitations"].append(limitation)

        if belief:
            self.self_model["beliefs_about_self"].update(belief)

        # 更新元认知状态
        if len(self.self_model["capabilities"]) > 5:
            self.self_model["meta_cognitive_state"] = "developing"
        if len(self.self_model["capabilities"]) > 10:
            self.self_model["meta_cognitive_state"] = "aware"

    def get_self_model(self) -> Dict:
        """获取自我模型"""
        return copy.deepcopy(self.self_model)

    # ========== 持久化 ==========

    def save(self, filepath: str):
        """保存世界模型到文件"""
        data = {
            "model_id": self.model_id,
            "states": {k: v.to_dict() for k, v in self.states.items()},
            "transitions": {k: v.to_dict() for k, v in self.transitions.items()},
            "causal_graph": {k: list(v) for k, v in self.causal_graph.items()},
            "current_state_id": self.current_state_id,
            "observation_count": self.observation_count,
            "prediction_count": self.prediction_count,
            "prediction_accuracy": self.prediction_accuracy,
            "self_model": self.self_model,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: str):
        """从文件加载世界模型"""
        with open(filepath, "r") as f:
            data = json.load(f)

        self.model_id = data["model_id"]
        self.states = {k: State.from_dict(v) for k, v in data["states"].items()}
        self.transitions = {k: Transition.from_dict(v) for k, v in data["transitions"].items()}
        self.causal_graph = defaultdict(
            set, {k: set(v) for k, v in data.get("causal_graph", {}).items()}
        )
        self.current_state_id = data.get("current_state_id")
        self.observation_count = data.get("observation_count", 0)
        self.prediction_count = data.get("prediction_count", 0)
        self.prediction_accuracy = data.get("prediction_accuracy", [])
        self.self_model = data.get("self_model", self.self_model)

    def export_summary(self) -> Dict:
        """导出模型摘要"""
        return {
            "model_id": self.model_id,
            "total_states": len(self.states),
            "total_transitions": len(self.transitions),
            "causal_relations": sum(len(effects) for effects in self.causal_graph.values()),
            "observations": self.observation_count,
            "predictions_made": self.prediction_count,
            "avg_prediction_accuracy": (
                sum(self.prediction_accuracy) / len(self.prediction_accuracy)
                if self.prediction_accuracy
                else 0
            ),
            "self_awareness_level": self.self_model["meta_cognitive_state"],
        }


# ==================== 测试与演示 ====================


def demo_world_model():
    """演示世界模型功能"""
    print("=" * 60)
    print("世界模型演示 - World Model Demo")
    print("=" * 60)

    # 创建世界模型
    wm = WorldModel("demo_environment")

    # 1. 观测状态
    print("\n1. 观测初始状态...")
    state1 = wm.observe(
        {
            "temperature": (25.0, StateType.PHYSICAL),
            "humidity": (60.0, StateType.PHYSICAL),
            "light_level": (500, StateType.PHYSICAL),
            "agent_position": (0, 0),
            "agent_energy": (100, StateType.COGNITIVE),
        }
    )
    print(f"   观测到状态：{state1.state_id}")
    print(f"   温度：{state1.get_value('temperature')}°C")

    # 2. 观测状态变化（学习转移）
    print("\n2. 观测状态变化（学习转移默式）...")
    for i in range(5):
        new_temp = (25.0 + i * 2, StateType.PHYSICAL)
        new_humidity = (60.0 - i, StateType.PHYSICAL)
        new_light = (500 + i * 50, StateType.PHYSICAL)
        new_pos = ((i * 10, i * 5), StateType.PHYSICAL)
        new_energy = (max(0, 100 - i * 10), StateType.COGNITIVE)

        wm.observe(
            {
                "temperature": new_temp,
                "humidity": new_humidity,
                "light_level": new_light,
                "agent_position": new_pos,
                "agent_energy": new_energy,
            },
            context={"step": i},
        )
        print(f"   步骤 {i+1}: 温度={new_temp[0]}, 位置={new_pos[0]}, 能量={new_energy[0]}")

    # 3. 预测未来
    print("\n3. 预测未来状态...")
    prediction = wm.predict(steps=3)
    if prediction:
        print(f"   预测置信度：{prediction.confidence:.2f}")
        print(f"   预测温度：{prediction.predicted_state.get_value('temperature'):.1f}°C")
        print(f"   预测位置：{prediction.predicted_state.get_value('agent_position')}")
        print(f"   预测能量：{prediction.predicted_state.get_value('agent_energy')}")

    # 4. 反事实推理
    print("\n4. 反事实推理：如果温度突然升高到 40°C...")
    cf = wm.counterfactual({"temperature": 40.0})
    print(f"   前提：{cf.premise}")
    print(f"   合理性评分：{cf.plausibility:.2f}")
    print(f"   因果链：{cf.causal_chain}")
    print(f"   变化的变量：{cf.difference_analysis.get('changed_variables', [])}")

    # 5. 自我模型
    print("\n5. 更新自我模型...")
    wm.update_self_model(capability="predict_future_states")
    wm.update_self_model(capability="counterfactual_reasoning")
    wm.update_self_model(capability="causal_discovery")
    wm.update_self_model(limitation="limited_to_learned_patterns")
    wm.update_self_model(belief={"learning_rate": 0.1, "curiosity": 0.8})

    self_model = wm.get_self_model()
    print(f"   能力：{self_model['capabilities']}")
    print(f"   局限：{self_model['limitations']}")
    print(f"   元认知状态：{self_model['meta_cognitive_state']}")

    # 6. 模型摘要
    print("\n6. 世界模型摘要:")
    summary = wm.export_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 60)
    print("演示完成!")
    print("=" * 60)

    return wm


if __name__ == "__main__":
    demo_world_model()
