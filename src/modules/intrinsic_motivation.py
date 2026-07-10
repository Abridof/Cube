"""
内在动机模块 - Intrinsic Motivation Module
====================================
第九阶段核心突破：引入好奇心驱动与自主探索能力

功能:
- 预测误差计算（新奇度检测）
- 信息增益最大化
- 好奇心驱动探索
- 内在奖励生成
- 自主目标形成

作者：AI Cognition Engine Team
版本：v9.0
"""

import time
import math
import hashlib
import random
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import copy

# ==================== 核心数据结构 ====================


class MotivationType(Enum):
    """内在动机类型"""

    CURIOSITY = "curiosity"  # 好奇心：探索未知
    COMPETENCE = "competence"  # 能力感：掌握技能
    NOVELTY = "novelty"  # 新奇性：寻求新异刺激
    SURPRISE = "surprise"  # 惊讶：预测误差
    LEARNING_PROGRESS = "learning_progress"  # 学习进步：能力提升
    CONTROL = "control"  # 控制感：影响环境


@dataclass
class PredictionError:
    """预测误差 - 内在动机的核心信号"""

    error_id: str
    predicted_value: Any
    actual_value: Any
    error_magnitude: float  # 误差大小
    normalized_error: float  # 归一化误差 [0, 1]
    surprise_level: float  # 惊讶程度 [0, 1]
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    source_variable: str = ""  # 产生误差的变量名

    def to_dict(self) -> Dict:
        return {
            "error_id": self.error_id,
            "predicted_value": self.predicted_value,
            "actual_value": self.actual_value,
            "error_magnitude": self.error_magnitude,
            "normalized_error": self.normalized_error,
            "surprise_level": self.surprise_level,
            "timestamp": self.timestamp,
            "context": self.context,
            "source_variable": self.source_variable,
        }


@dataclass
class InformationGain:
    """信息增益 - 学习带来的知识增量"""

    gain_id: str
    before_entropy: float  # 学习前的熵
    after_entropy: float  # 学习后的熵
    information_gain: float  # 信息增益量
    knowledge_area: str  # 知识领域
    timestamp: float = field(default_factory=time.time)
    learning_event: str = ""  # 触发学习的事件

    def to_dict(self) -> Dict:
        return {
            "gain_id": self.gain_id,
            "before_entropy": self.before_entropy,
            "after_entropy": self.after_entropy,
            "information_gain": self.information_gain,
            "knowledge_area": self.knowledge_area,
            "timestamp": self.timestamp,
            "learning_event": self.learning_event,
        }


@dataclass
class IntrinsicReward:
    """内在奖励 - 驱动自主学习的信号"""

    reward_id: str
    reward_type: MotivationType
    magnitude: float  # 奖励强度
    source: str  # 奖励来源（误差、信息增益等）
    timestamp: float = field(default_factory=time.time)
    decay_rate: float = 0.95  # 衰减率
    accumulated: float = 0.0  # 累积奖励

    def to_dict(self) -> Dict:
        return {
            "reward_id": self.reward_id,
            "reward_type": self.reward_type.value,
            "magnitude": self.magnitude,
            "source": self.source,
            "timestamp": self.timestamp,
            "decay_rate": self.decay_rate,
            "accumulated": self.accumulated,
        }


@dataclass
class ExplorationGoal:
    """自主探索目标"""

    goal_id: str
    description: str
    motivation_type: MotivationType
    priority: float  # 优先级 [0, 1]
    expected_information_gain: float  # 预期信息增益
    current_state: Any = None  # 当前状态
    target_state: Any = None  # 目标状态
    created_at: float = field(default_factory=time.time)
    achieved: bool = False
    achievement_time: Optional[float] = None

    def to_dict(self) -> Dict:
        return {
            "goal_id": self.goal_id,
            "description": self.description,
            "motivation_type": self.motivation_type.value,
            "priority": self.priority,
            "expected_information_gain": self.expected_information_gain,
            "current_state": self.current_state,
            "target_state": self.target_state,
            "created_at": self.created_at,
            "achieved": self.achieved,
            "achievement_time": self.achievement_time,
        }


# ==================== 预测误差计算器 ====================


class PredictionErrorCalculator:
    """
    预测误差计算器 - 内在动机的核心引擎

    核心能力:
    1. 多尺度误差检测：在不同时间尺度上检测预测误差
    2. 归一化处理：将误差转换为可比较的标准形式
    3. 惊讶度计算：基于历史误差分布计算惊讶程度
    4. 误差溯源：追踪误差来源以指导学习
    5. 适应性阈值：动态调整误差检测阈值
    """

    def __init__(self, calculator_id: str = "default_error_calc"):
        self.calculator_id = calculator_id

        # 误差历史记录（用于统计和归一化）
        self.error_history: Dict[str, List[float]] = defaultdict(list)
        self.max_history_length = 1000

        # 误差统计信息
        self.error_stats: Dict[str, Dict[str, float]] = {}  # {var_name: {mean, std, min, max}}

        # 惊讶度模型
        self.surprise_thresholds: Dict[str, float] = {}  # 每个变量的惊讶阈值
        self.default_surprise_threshold = 2.0  # 默认 2 个标准差

        # 预测误差记录
        self.errors: Dict[str, PredictionError] = {}
        self.error_count = 0

        # 自适应参数
        self.adaptive_learning_rate = 0.1
        self.baseline_window = 50  # 基线计算窗口大小

    def _generate_id(self, prefix: str) -> str:
        """生成唯一 ID"""
        timestamp = str(time.time())
        random_suffix = str(random.random())[2:8]
        hash_input = f"{prefix}_{timestamp}_{random_suffix}"
        return f"{prefix}_{hashlib.sha256(hash_input.encode()).hexdigest()[:16]}"

    def calculate_error(
        self, predicted: Any, actual: Any, var_name: str = "default", context: Optional[Dict] = None
    ) -> PredictionError:
        """
        计算预测误差

        Args:
            predicted: 预测值
            actual: 实际值
            var_name: 变量名称
            context: 可选上下文

        Returns:
            PredictionError 对象
        """
        # 计算原始误差
        if isinstance(predicted, (int, float)) and isinstance(actual, (int, float)):
            error_magnitude = abs(actual - predicted)
        elif isinstance(predicted, list) and isinstance(actual, list):
            # 向量误差（欧氏距离）
            if len(predicted) == len(actual):
                error_magnitude = math.sqrt(sum((p - a) ** 2 for p, a in zip(predicted, actual)))
            else:
                error_magnitude = float("inf")
        else:
            # 离散值误差
            error_magnitude = 0.0 if predicted == actual else 1.0

        # 更新误差历史
        self._update_error_history(var_name, error_magnitude)

        # 归一化误差
        normalized_error = self._normalize_error(var_name, error_magnitude)

        # 计算惊讶度
        surprise_level = self._calculate_surprise(var_name, error_magnitude)

        # 创建误差对象
        error = PredictionError(
            error_id=self._generate_id("error"),
            predicted_value=predicted,
            actual_value=actual,
            error_magnitude=error_magnitude,
            normalized_error=normalized_error,
            surprise_level=surprise_level,
            context=context or {},
            source_variable=var_name,
        )

        self.errors[error.error_id] = error
        self.error_count += 1

        return error

    def _update_error_history(self, var_name: str, error: float):
        """更新误差历史记录"""
        self.error_history[var_name].append(error)

        # 限制历史长度
        if len(self.error_history[var_name]) > self.max_history_length:
            self.error_history[var_name] = self.error_history[var_name][-self.max_history_length :]

        # 更新统计信息
        self._update_statistics(var_name)

    def _update_statistics(self, var_name: str):
        """更新误差统计信息"""
        errors = self.error_history[var_name]
        if not errors:
            return

        n = len(errors)
        mean = sum(errors) / n

        if n > 1:
            variance = sum((e - mean) ** 2 for e in errors) / (n - 1)
            std = math.sqrt(variance)
        else:
            std = 0.0

        self.error_stats[var_name] = {
            "mean": mean,
            "std": std,
            "min": min(errors),
            "max": max(errors),
            "count": n,
        }

        # 更新惊讶阈值（均值的 2 个标准差）
        if std > 0:
            self.surprise_thresholds[var_name] = mean + self.default_surprise_threshold * std
        else:
            self.surprise_thresholds[var_name] = mean * 2

    def _normalize_error(self, var_name: str, error: float) -> float:
        """
        归一化误差到 [0, 1] 范围

        使用历史最大误差作为归一化因子
        """
        stats = self.error_stats.get(var_name, {})
        max_error = stats.get("max", error)

        if max_error == 0:
            return 0.0

        normalized = min(1.0, error / max_error)
        return normalized

    def _calculate_surprise(self, var_name: str, error: float) -> float:
        """
        计算惊讶度

        基于误差与历史分布的偏离程度
        使用 Z-score 方法：Z = (error - mean) / std
        """
        stats = self.error_stats.get(var_name, {})
        mean = stats.get("mean", 0)
        std = stats.get("std", 1)

        if std == 0 or std < 1e-10:
            # 如果没有方差，使用相对误差
            if mean == 0:
                return 0.5
            return min(1.0, abs(error - mean) / mean)

        # Z-score
        z_score = abs(error - mean) / std

        # 将 Z-score 转换为 [0, 1] 的惊讶度
        # 使用 sigmoid 函数的变体
        surprise = 2 / (1 + math.exp(-z_score / 2)) - 1

        return min(1.0, max(0.0, surprise))

    def get_surprising_errors(
        self, threshold: float = 0.7, limit: int = 10
    ) -> List[PredictionError]:
        """获取高惊讶度的误差"""
        surprising = [e for e in self.errors.values() if e.surprise_level >= threshold]
        surprising.sort(key=lambda e: e.surprise_level, reverse=True)
        return surprising[:limit]

    def get_learning_priorities(self) -> Dict[str, float]:
        """
        获取学习优先级

        基于各变量的平均预测误差，误差越大优先级越高
        """
        priorities = {}
        for var_name, stats in self.error_stats.items():
            # 综合考虑平均误差和方差
            priority = stats["mean"] * (1 + stats["std"])
            priorities[var_name] = min(1.0, priority / (stats["max"] + 1e-10))

        return priorities

    def reset_baseline(self, var_name: str = None):
        """重置基线统计信息"""
        if var_name:
            self.error_history[var_name] = []
            if var_name in self.error_stats:
                del self.error_stats[var_name]
        else:
            self.error_history.clear()
            self.error_stats.clear()


# ==================== 信息增益计算器 ====================


class InformationGainCalculator:
    """
    信息增益计算器 - 量化学习带来的知识增量

    核心能力:
    1. 熵计算：计算概率分布的不确定性
    2. 条件熵：计算给定条件下的不确定性
    3. 互信息：衡量变量间的信息共享
    4. 学习进度跟踪：跟踪知识增长曲线
    """

    def __init__(self, calculator_id: str = "default_info_gain"):
        self.calculator_id = calculator_id
        self.gains: Dict[str, InformationGain] = {}
        self.gain_count = 0

        # 知识状态跟踪
        self.knowledge_states: Dict[str, List[float]] = defaultdict(list)

        # 学习进度记录
        self.learning_curves: Dict[str, List[Tuple[float, float]]] = defaultdict(list)

    def _generate_id(self, prefix: str) -> str:
        """生成唯一 ID"""
        timestamp = str(time.time())
        random_suffix = str(random.random())[2:8]
        hash_input = f"{prefix}_{timestamp}_{random_suffix}"
        return f"{prefix}_{hashlib.sha256(hash_input.encode()).hexdigest()[:16]}"

    def calculate_entropy(self, probabilities: List[float]) -> float:
        """
        计算香农熵

        Args:
            probabilities: 概率分布列表

        Returns:
            熵值（比特）
        """
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    def calculate_information_gain(
        self,
        before_probs: List[float],
        after_probs: List[float],
        knowledge_area: str = "general",
        learning_event: str = "",
    ) -> InformationGain:
        """
        计算信息增益

        Args:
            before_probs: 学习前的概率分布
            after_probs: 学习后的概率分布
            knowledge_area: 知识领域
            learning_event: 触发学习的事件

        Returns:
            InformationGain 对象
        """
        before_entropy = self.calculate_entropy(before_probs)
        after_entropy = self.calculate_entropy(after_probs)

        # 信息增益 = 学习前熵 - 学习后熵
        info_gain = before_entropy - after_entropy

        # 确保非负（理论上应该如此，但数值误差可能导致负值）
        info_gain = max(0.0, info_gain)

        gain = InformationGain(
            gain_id=self._generate_id("gain"),
            before_entropy=before_entropy,
            after_entropy=after_entropy,
            information_gain=info_gain,
            knowledge_area=knowledge_area,
            learning_event=learning_event,
        )

        self.gains[gain.gain_id] = gain
        self.gain_count += 1

        # 更新知识状态
        self.knowledge_states[knowledge_area].append(after_entropy)

        # 记录学习曲线
        timestamp = time.time()
        cumulative_gain = sum(
            g.information_gain for g in self.gains.values() if g.knowledge_area == knowledge_area
        )
        self.learning_curves[knowledge_area].append((timestamp, cumulative_gain))

        return gain

    def calculate_mutual_information(
        self, joint_probs: Dict[Tuple[Any, Any], float], x_values: List[Any], y_values: List[Any]
    ) -> float:
        """
        计算互信息 - 衡量两个变量间的信息共享

        I(X;Y) = Σ p(x,y) * log(p(x,y) / (p(x)*p(y)))
        """
        # 计算边缘分布
        p_x = {x: 0.0 for x in x_values}
        p_y = {y: 0.0 for y in y_values}

        for (x, y), p_xy in joint_probs.items():
            p_x[x] += p_xy
            p_y[y] += p_xy

        # 计算互信息
        mutual_info = 0.0
        for (x, y), p_xy in joint_probs.items():
            if p_xy > 0 and p_x[x] > 0 and p_y[y] > 0:
                mutual_info += p_xy * math.log2(p_xy / (p_x[x] * p_y[y]))

        return mutual_info

    def get_knowledge_growth_rate(self, knowledge_area: str, window_size: int = 10) -> float:
        """
        获取知识增长率

        基于最近的学习曲线斜率
        """
        curve = self.learning_curves.get(knowledge_area, [])
        if len(curve) < 2:
            return 0.0

        # 取最近的窗口
        recent = curve[-window_size:] if len(curve) > window_size else curve

        if len(recent) < 2:
            return 0.0

        # 计算斜率
        time_diff = recent[-1][0] - recent[0][0]
        gain_diff = recent[-1][1] - recent[0][1]

        if time_diff == 0:
            return 0.0

        return gain_diff / time_diff

    def get_total_knowledge(self, knowledge_area: str = None) -> float:
        """获取总知识量（累积信息增益）"""
        if knowledge_area:
            return sum(
                g.information_gain
                for g in self.gains.values()
                if g.knowledge_area == knowledge_area
            )
        else:
            return sum(g.information_gain for g in self.gains.values())


# ==================== 内在动机引擎 ====================


class IntrinsicMotivationEngine:
    """
    内在动机引擎 - 整合预测误差和信息增益，生成自主驱动力

    核心能力:
    1. 多动机融合：整合多种内在动机信号
    2. 动机权重学习：动态调整不同动机的权重
    3. 目标生成：基于动机生成探索目标
    4. 奖励分配：生成内在奖励信号
    5. 好奇心调度：决定何时探索 vs 利用
    """

    def __init__(self, engine_id: str = "default_motivation"):
        self.engine_id = engine_id

        # 子组件
        self.error_calculator = PredictionErrorCalculator()
        self.info_gain_calculator = InformationGainCalculator()

        # 动机权重（可学习）
        self.motivation_weights = {
            MotivationType.CURIOSITY: 0.3,
            MotivationType.COMPETENCE: 0.2,
            MotivationType.NOVELTY: 0.2,
            MotivationType.SURPRISE: 0.15,
            MotivationType.LEARNING_PROGRESS: 0.1,
            MotivationType.CONTROL: 0.05,
        }

        # 内在奖励历史
        self.rewards: Dict[str, IntrinsicReward] = {}
        self.reward_count = 0

        # 探索目标队列
        self.goals: Dict[str, ExplorationGoal] = {}
        self.active_goal_id: Optional[str] = None

        # 探索 - 利用平衡
        self.exploration_rate = 0.5  # ε-greedy 中的 ε
        self.exploration_decay = 0.995  # 随时间衰减

        # 统计信息
        self.total_intrinsic_reward = 0.0
        self.goals_achieved = 0

    def _generate_id(self, prefix: str) -> str:
        """生成唯一 ID"""
        timestamp = str(time.time())
        random_suffix = str(random.random())[2:8]
        hash_input = f"{prefix}_{timestamp}_{random_suffix}"
        return f"{prefix}_{hashlib.sha256(hash_input.encode()).hexdigest()[:16]}"

    def process_prediction(
        self, predicted: Any, actual: Any, var_name: str = "default", context: Optional[Dict] = None
    ) -> IntrinsicReward:
        """
        处理预测结果，生成内在奖励

        流程：
        1. 计算预测误差
        2. 根据误差生成惊讶奖励（高误差=高惊讶=高奖励）
        3. 如果误差降低，生成能力感奖励
        """
        # 计算预测误差
        error = self.error_calculator.calculate_error(predicted, actual, var_name, context)

        # 生成惊讶奖励（高误差带来高惊讶，驱动探索）
        surprise_reward = error.surprise_level * self.motivation_weights[MotivationType.SURPRISE]

        # 检查是否是能力感提升（误差低于平均水平）
        stats = self.error_calculator.error_stats.get(var_name, {})
        mean_error = stats.get("mean", 0)
        competence_reward = 0.0
        if error.error_magnitude < mean_error * 0.8:  # 比平均水平好 20%
            competence_reward = (mean_error - error.error_magnitude) / (mean_error + 1e-10)
            competence_reward *= self.motivation_weights[MotivationType.COMPETENCE]

        # 总内在奖励
        total_reward = surprise_reward + competence_reward

        reward = IntrinsicReward(
            reward_id=self._generate_id("reward"),
            reward_type=(
                MotivationType.SURPRISE
                if surprise_reward > competence_reward
                else MotivationType.COMPETENCE
            ),
            magnitude=total_reward,
            source=f"prediction_{var_name}",
        )

        self.rewards[reward.reward_id] = reward
        self.reward_count += 1
        self.total_intrinsic_reward += total_reward

        return reward

    def process_learning_event(
        self,
        before_probs: List[float],
        after_probs: List[float],
        knowledge_area: str = "general",
        learning_event: str = "",
    ) -> IntrinsicReward:
        """
        处理学习事件，生成内在奖励

        基于信息增益生成学习进步奖励
        """
        # 计算信息增益
        gain = self.info_gain_calculator.calculate_information_gain(
            before_probs, after_probs, knowledge_area, learning_event
        )

        # 生成学习进步奖励
        progress_reward = (
            gain.information_gain * self.motivation_weights[MotivationType.LEARNING_PROGRESS]
        )

        # 生成好奇心奖励（新知识领域）
        novelty_bonus = 0.0
        if len(self.info_gain_calculator.knowledge_states[knowledge_area]) <= 1:
            novelty_bonus = gain.information_gain * 0.5  # 新领域额外奖励
            novelty_bonus *= self.motivation_weights[MotivationType.NOVELTY]

        total_reward = progress_reward + novelty_bonus

        reward = IntrinsicReward(
            reward_id=self._generate_id("reward"),
            reward_type=MotivationType.LEARNING_PROGRESS,
            magnitude=total_reward,
            source=f"learning_{knowledge_area}",
        )

        self.rewards[reward.reward_id] = reward
        self.reward_count += 1
        self.total_intrinsic_reward += total_reward

        return reward

    def generate_exploration_goal(
        self,
        description: str,
        motivation_type: MotivationType,
        expected_gain: float,
        target_state: Any = None,
    ) -> ExplorationGoal:
        """
        生成探索目标

        基于当前动机状态自动生成探索目标
        """
        # 计算优先级
        base_priority = self.motivation_weights[motivation_type]

        # 根据预期信息增益调整优先级
        priority = min(1.0, base_priority + expected_gain * 0.3)

        goal = ExplorationGoal(
            goal_id=self._generate_id("goal"),
            description=description,
            motivation_type=motivation_type,
            priority=priority,
            expected_information_gain=expected_gain,
            target_state=target_state,
        )

        self.goals[goal.goal_id] = goal

        # 如果是最高优先级，设为活跃目标
        if self.active_goal_id is None or priority > self.goals[self.active_goal_id].priority:
            self.active_goal_id = goal.goal_id

        return goal

    def auto_generate_goals(self, context: Dict[str, Any] = None) -> List[ExplorationGoal]:
        """
        自动生成探索目标

        基于当前预测误差和学习进度分析
        """
        goals = []

        # 1. 基于高误差区域生成好奇心目标
        priorities = self.error_calculator.get_learning_priorities()
        for var_name, priority in priorities.items():
            if priority > 0.5:  # 高误差区域
                goal = self.generate_exploration_goal(
                    description=f"Explore and reduce uncertainty in {var_name}",
                    motivation_type=MotivationType.CURIOSITY,
                    expected_gain=priority * 0.8,
                    target_state={var_name: "reduced_uncertainty"},
                )
                goals.append(goal)

        # 2. 基于惊讶事件生成探索目标
        surprising_errors = self.error_calculator.get_surprising_errors(threshold=0.6, limit=3)
        for error in surprising_errors:
            goal = self.generate_exploration_goal(
                description=f"Investigate surprising event in {error.source_variable}",
                motivation_type=MotivationType.SURPRISE,
                expected_gain=error.surprise_level * 0.9,
                target_state={error.source_variable: "understood"},
            )
            goals.append(goal)

        # 3. 基于低知识增长率生成学习目标
        for area in self.info_gain_calculator.knowledge_states.keys():
            growth_rate = self.info_gain_calculator.get_knowledge_growth_rate(area)
            if growth_rate < 0.01:  # 增长缓慢
                goal = self.generate_exploration_goal(
                    description=f"Accelerate learning in {area}",
                    motivation_type=MotivationType.LEARNING_PROGRESS,
                    expected_gain=0.5,
                    target_state={area: "accelerated_growth"},
                )
                goals.append(goal)

        return goals

    def should_explore(self) -> bool:
        """
        决定是否探索（vs 利用）

        使用 ε-greedy 策略，ε 随时间衰减
        """
        if random.random() < self.exploration_rate:
            return True

        # 如果有高优先级的未达成目标，强制探索
        for goal in self.goals.values():
            if not goal.achieved and goal.priority > 0.7:
                return True

        return False

    def update_exploration_rate(self):
        """更新探索率（衰减）"""
        self.exploration_rate = max(0.05, self.exploration_rate * self.exploration_decay)

    def achieve_goal(self, goal_id: str):
        """标记目标为已达成"""
        if goal_id in self.goals:
            self.goals[goal_id].achieved = True
            self.goals[goal_id].achievement_time = time.time()
            self.goals_achieved += 1

            if self.active_goal_id == goal_id:
                self.active_goal_id = None

    def get_motivation_summary(self) -> Dict[str, Any]:
        """获取动机状态摘要"""
        return {
            "total_intrinsic_reward": self.total_intrinsic_reward,
            "exploration_rate": self.exploration_rate,
            "active_goal": self.goals.get(self.active_goal_id, None),
            "goals_achieved": self.goals_achieved,
            "total_goals": len(self.goals),
            "motivation_weights": {k.value: v for k, v in self.motivation_weights.items()},
            "error_stats_summary": {
                k: {"mean": v["mean"], "std": v["std"]}
                for k, v in self.error_calculator.error_stats.items()
            },
            "knowledge_areas": list(self.info_gain_calculator.knowledge_states.keys()),
        }


# ==================== 演示函数 ====================


def demo_intrinsic_motivation():
    """演示内在动机系统"""
    print("=" * 60)
    print("内在动机系统演示")
    print("=" * 60)

    # 创建引擎
    engine = IntrinsicMotivationEngine("demo_engine")

    print("\n【1】预测误差与惊讶奖励")
    print("-" * 40)

    # 模拟一系列预测
    true_func = lambda x: 2 * x + 1
    predictions = [3.0, 5.0, 7.0, 9.0, 11.0]  # 初始预测

    for i in range(10):
        x = i
        actual = true_func(x)
        predicted = predictions[i] if i < len(predictions) else 2 * x + random.uniform(-2, 2)

        reward = engine.process_prediction(
            predicted=predicted, actual=actual, var_name="linear_function", context={"step": i}
        )

        print(
            f"Step {i}: predicted={predicted:.2f}, actual={actual:.2f}, "
            f"reward={reward.magnitude:.3f}, type={reward.reward_type.value}"
        )

    print("\n【2】信息增益与学习进步奖励")
    print("-" * 40)

    # 模拟学习过程：从均匀分布到集中分布
    before_learning = [0.2, 0.2, 0.2, 0.2, 0.2]  # 均匀分布，高熵
    after_learning_1 = [0.1, 0.1, 0.6, 0.1, 0.1]  # 开始集中
    after_learning_2 = [0.05, 0.05, 0.8, 0.05, 0.05]  # 更集中

    reward1 = engine.process_learning_event(
        before_probs=before_learning,
        after_probs=after_learning_1,
        knowledge_area="physics",
        learning_event="learned_gravity",
    )

    reward2 = engine.process_learning_event(
        before_probs=after_learning_1,
        after_probs=after_learning_2,
        knowledge_area="physics",
        learning_event="refined_gravity_model",
    )

    print(f"Learning event 1: info_gain -> reward={reward1.magnitude:.3f}")
    print(f"Learning event 2: info_gain -> reward={reward2.magnitude:.3f}")

    print("\n【3】自动生成探索目标")
    print("-" * 40)

    goals = engine.auto_generate_goals()
    print(f"Generated {len(goals)} exploration goals:")
    for goal in goals[:5]:
        print(
            f"  - {goal.description} (priority={goal.priority:.2f}, "
            f"type={goal.motivation_type.value})"
        )

    print("\n【4】探索 - 利用决策")
    print("-" * 40)

    explore_count = 0
    for i in range(20):
        if engine.should_explore():
            explore_count += 1
        engine.update_exploration_rate()

    print(f"Exploration decisions: {explore_count}/20")
    print(f"Final exploration rate: {engine.exploration_rate:.3f}")

    print("\n【5】动机状态摘要")
    print("-" * 40)

    summary = engine.get_motivation_summary()
    print(f"Total intrinsic reward: {summary['total_intrinsic_reward']:.3f}")
    print(f"Goals achieved: {summary['goals_achieved']}/{summary['total_goals']}")
    print(f"Knowledge areas: {summary['knowledge_areas']}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return engine


if __name__ == "__main__":
    demo_engine = demo_intrinsic_motivation()
