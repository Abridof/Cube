"""
阶段 9: 内在动机与好奇心驱动模块

实现目标：
- 让系统主动探索未知领域，而非仅依赖外部指令
- 基于预测误差和信息增益的内在奖励机制
- 支持多种内在动机类型：好奇心、能力感、新奇性、惊讶、学习进步、控制感
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import math


class IntrinsicMotivationType(Enum):
    """内在动机类型"""
    CURIOSITY = "curiosity"  # 好奇心 - 预测误差驱动
    COMPETENCE = "competence"  # 能力感 - 掌握程度提升
    NOVELTY = "novelty"  # 新奇性 - 从未经历的状态
    SURPRISE = "surprise"  # 惊讶 - 预期违背
    LEARNING_PROGRESS = "learning_progress"  # 学习进步 - 能力提升速率
    CONTROL = "control"  # 控制感 - 对环境的影响力


@dataclass
class PredictionError:
    """预测误差数据结构"""
    predicted: np.ndarray
    actual: np.ndarray
    error: float
    error_vector: np.ndarray
    modality: str
    timestamp: int


@dataclass
class IntrinsicReward:
    """内在奖励数据结构"""
    motivation_type: IntrinsicMotivationType
    reward_value: float
    state_description: str
    action_taken: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExplorationGoal:
    """自动生成的探索目标"""
    goal_id: str
    description: str
    target_state: Optional[np.ndarray]
    priority: float
    motivation_type: IntrinsicMotivationType
    created_at: int
    completed: bool = False


class PredictionErrorCalculator:
    """
    预测误差计算器
    
    计算世界模型预测与实际观测之间的差异
    支持多模态预测误差的加权融合
    """
    
    def __init__(self, modality_weights: Optional[Dict[str, float]] = None):
        """
        初始化预测误差计算器
        
        Args:
            modality_weights: 各模态的权重，默认均匀分布
        """
        self.modality_weights = modality_weights or {}
        self.error_history: List[PredictionError] = []
        
    def calculate_error(
        self,
        predicted: np.ndarray,
        actual: np.ndarray,
        modality: str = "default"
    ) -> PredictionError:
        """
        计算单次预测误差
        
        Args:
            predicted: 预测值
            actual: 实际观测值
            modality: 模态类型
            
        Returns:
            PredictionError: 包含误差信息的数据结构
        """
        if predicted.shape != actual.shape:
            raise ValueError(f"Shape mismatch: {predicted.shape} vs {actual.shape}")
        
        error_vector = actual - predicted
        error = np.linalg.norm(error_vector)
        
        pred_error = PredictionError(
            predicted=predicted.copy(),
            actual=actual.copy(),
            error=error,
            error_vector=error_vector.copy(),
            modality=modality,
            timestamp=len(self.error_history)
        )
        
        self.error_history.append(pred_error)
        return pred_error
    
    def calculate_weighted_error(
        self,
        predictions: Dict[str, np.ndarray],
        actuals: Dict[str, np.ndarray]
    ) -> float:
        """
        计算多模态加权预测误差
        
        Args:
            predictions: 各模态的预测值字典
            actuals: 各模态的实际观测值字典
            
        Returns:
            float: 加权总误差
        """
        total_error = 0.0
        total_weight = 0.0
        
        for modality in predictions.keys():
            if modality not in actuals:
                continue
                
            pred_err = self.calculate_error(
                predictions[modality],
                actuals[modality],
                modality
            )
            
            weight = self.modality_weights.get(modality, 1.0)
            total_error += weight * pred_err.error
            total_weight += weight
        
        return total_error / total_weight if total_weight > 0 else 0.0
    
    def get_recent_average_error(self, window_size: int = 10) -> float:
        """获取最近 N 次的平均误差"""
        if len(self.error_history) == 0:
            return 0.0
        
        recent = self.error_history[-window_size:]
        return np.mean([e.error for e in recent])
    
    def get_error_trend(self, window_size: int = 20) -> float:
        """
        获取误差变化趋势（负值表示误差在减小）
        
        Returns:
            float: 误差的一阶导数近似值
        """
        if len(self.error_history) < window_size:
            return 0.0
        
        recent = self.error_history[-window_size:]
        errors = [e.error for e in recent]
        
        first_half = np.mean(errors[:window_size//2])
        second_half = np.mean(errors[window_size//2:])
        
        return second_half - first_half


class InformationGainCalculator:
    """
    信息增益计算器
    
    基于熵减计算知识获取量
    支持新奇性检测和惊讶度量化
    """
    
    def __init__(self, state_bins: int = 10):
        """
        初始化信息增益计算器
        
        Args:
            state_bins: 状态离散化的 bin 数量
        """
        self.state_bins = state_bins
        self.state_distribution: Dict[str, np.ndarray] = {}
        self.visited_states: set = set()
        self.expectation_model: Dict[str, float] = {}
        
    def _discretize_state(self, state: np.ndarray) -> Tuple:
        """将连续状态离散化"""
        return tuple(np.digitize(state, np.linspace(state.min(), state.max(), self.state_bins)))
    
    def update_distribution(self, state: np.ndarray, context: str = "global"):
        """
        更新状态分布
        
        Args:
            state: 当前状态
            context: 上下文标识
        """
        discrete_state = self._discretize_state(state)
        self.visited_states.add(discrete_state)
        
        if context not in self.state_distribution:
            self.state_distribution[context] = np.zeros(self.state_bins ** len(state))
        
        idx = hash(discrete_state) % len(self.state_distribution[context])
        self.state_distribution[context][idx] += 1
        
    def calculate_entropy(self, context: str = "global") -> float:
        """
        计算当前分布的熵
        
        Returns:
            float: 熵值
        """
        if context not in self.state_distribution:
            return 0.0
        
        dist = self.state_distribution[context]
        total = dist.sum()
        
        if total == 0:
            return 0.0
        
        probs = dist / total
        probs = probs[probs > 0]
        
        return -np.sum(probs * np.log2(probs))
    
    def calculate_information_gain(
        self,
        old_context: str,
        new_context: str
    ) -> float:
        """
        计算信息增益（熵减）
        
        Args:
            old_context: 旧上下文的标识
            new_context: 新上下文的标识
            
        Returns:
            float: 信息增益量
        """
        old_entropy = self.calculate_entropy(old_context)
        new_entropy = self.calculate_entropy(new_context)
        
        return old_entropy - new_entropy
    
    def calculate_novelty(self, state: np.ndarray, context: str = "global") -> float:
        """
        计算状态的新奇性
        
        Args:
            state: 当前状态
            context: 上下文标识
            
        Returns:
            float: 新奇性得分 (0-1)，1 表示完全新奇
        """
        discrete_state = self._discretize_state(state)
        
        if discrete_state not in self.visited_states:
            return 1.0
        
        if context not in self.state_distribution:
            return 0.5
        
        idx = hash(discrete_state) % len(self.state_distribution[context])
        count = self.state_distribution[context][idx]
        total = self.state_distribution[context].sum()
        
        if total == 0:
            return 1.0
        
        frequency = count / total
        novelty = 1.0 / (1.0 + frequency * 10)
        
        return min(1.0, novelty)
    
    def calculate_surprise(
        self,
        observed: float,
        expected: float,
        variance: float = 1.0
    ) -> float:
        """
        计算惊讶度（基于预测误差的标准化）
        
        Args:
            observed: 观测值
            expected: 期望值
            variance: 预期方差
            
        Returns:
            float: 惊讶度得分 (0-1)
        """
        if variance <= 0:
            variance = 1e-6
        
        z_score = abs(observed - expected) / math.sqrt(variance)
        surprise = 1.0 - math.exp(-z_score ** 2 / 2)
        
        return min(1.0, surprise)
    
    def update_expectation(self, key: str, value: float, alpha: float = 0.1):
        """
        更新期望模型（指数移动平均）
        
        Args:
            key: 期望的键
            value: 新观测值
            alpha: 学习率
        """
        if key not in self.expectation_model:
            self.expectation_model[key] = value
        else:
            self.expectation_model[key] = (1 - alpha) * self.expectation_model[key] + alpha * value


class CompetenceTracker:
    """
    能力感追踪器
    
    追踪智能体在特定任务上的掌握程度
    计算学习进步速率
    """
    
    def __init__(self):
        self.task_performance: Dict[str, List[float]] = {}
        self.task_baseline: Dict[str, float] = {}
        
    def record_performance(self, task_id: str, performance: float):
        """记录任务表现"""
        if task_id not in self.task_performance:
            self.task_performance[task_id] = []
            self.task_baseline[task_id] = performance
        
        self.task_performance[task_id].append(performance)
    
    def get_competence(self, task_id: str) -> float:
        """
        获取当前能力水平
        
        Returns:
            float: 能力得分 (0-1)
        """
        if task_id not in self.task_performance or len(self.task_performance[task_id]) == 0:
            return 0.0
        
        performances = self.task_performance[task_id]
        baseline = self.task_baseline.get(task_id, 0)
        
        max_perf = max(performances)
        if max_perf == baseline:
            return 0.5
        
        improvement = (np.mean(performances[-5:]) - baseline) / (max_perf - baseline + 1e-6)
        return np.clip(0.5 + improvement * 0.5, 0, 1)
    
    def get_learning_progress(self, task_id: str, window: int = 10) -> float:
        """
        获取学习进步速率
        
        Returns:
            float: 进步速率，正值表示在进步
        """
        if task_id not in self.task_performance or len(self.task_performance[task_id]) < window:
            return 0.0
        
        performances = self.task_performance[task_id][-window:]
        first_half = np.mean(performances[:window//2])
        second_half = np.mean(performances[window//2:])
        
        return second_half - first_half


class ControlEstimator:
    """
    控制感估计器
    
    估计智能体对环境的影响力
    """
    
    def __init__(self):
        self.action_effects: Dict[str, List[float]] = {}
        self.random_effects: List[float] = []
        
    def record_action_effect(self, action: str, effect_magnitude: float):
        """记录动作效果"""
        if action not in self.action_effects:
            self.action_effects[action] = []
        self.action_effects[action].append(effect_magnitude)
    
    def record_random_effect(self, magnitude: float):
        """记录随机扰动效果（基线）"""
        self.random_effects.append(magnitude)
    
    def estimate_control(self, action: str) -> float:
        """
        估计对特定动作的控制感
        
        Returns:
            float: 控制感得分 (0-1)
        """
        if action not in self.action_effects or len(self.action_effects[action]) == 0:
            return 0.0
        
        action_mean = np.mean(self.action_effects[action])
        
        if len(self.random_effects) == 0:
            return 0.5
        
        random_mean = np.mean(self.random_effects)
        random_std = np.std(self.random_effects) + 1e-6
        
        z_score = (action_mean - random_mean) / random_std
        control = 1.0 / (1.0 + math.exp(-z_score))
        
        return control


class IntrinsicMotivationEngine:
    """
    内在动机引擎
    
    整合多种内在奖励信号
    实现探索 - 利用平衡策略
    自动生成探索目标
    """
    
    def __init__(
        self,
        curiosity_weight: float = 1.0,
        competence_weight: float = 0.8,
        novelty_weight: float = 1.2,
        surprise_weight: float = 1.0,
        progress_weight: float = 1.5,
        control_weight: float = 0.7,
        exploration_epsilon: float = 0.3,
        ucb_c: float = 2.0
    ):
        """
        初始化内在动机引擎
        
        Args:
            curiosity_weight: 好奇心权重
            competence_weight: 能力感权重
            novelty_weight: 新奇性权重
            surprise_weight: 惊讶权重
            progress_weight: 学习进步权重
            control_weight: 控制感权重
            exploration_epsilon: ε-greedy 的探索概率
            ucb_c: UCB 的探索系数
        """
        self.weights = {
            IntrinsicMotivationType.CURIOSITY: curiosity_weight,
            IntrinsicMotivationType.COMPETENCE: competence_weight,
            IntrinsicMotivationType.NOVELTY: novelty_weight,
            IntrinsicMotivationType.SURPRISE: surprise_weight,
            IntrinsicMotivationType.LEARNING_PROGRESS: progress_weight,
            IntrinsicMotivationType.CONTROL: control_weight,
        }
        
        self.prediction_calculator = PredictionErrorCalculator()
        self.info_gain_calculator = InformationGainCalculator()
        self.competence_tracker = CompetenceTracker()
        self.control_estimator = ControlEstimator()
        
        self.exploration_epsilon = exploration_epsilon
        self.ucb_c = ucb_c
        
        self.goals: List[ExplorationGoal] = []
        self.total_reward = 0.0
        self.timestep = 0
        
        self.state_visit_counts: Dict[Tuple, int] = {}
        self.action_counts: Dict[str, int] = {}
        
    def compute_intrinsic_reward(
        self,
        state: np.ndarray,
        action: str,
        next_state: np.ndarray,
        prediction: Optional[np.ndarray] = None,
        task_id: Optional[str] = None,
        context: str = "global"
    ) -> IntrinsicReward:
        """
        计算综合内在奖励
        
        Args:
            state: 当前状态
            action: 采取的动作
            next_state: 下一状态
            prediction: 预测的下一状态（可选）
            task_id: 任务标识（可选）
            context: 上下文标识
            
        Returns:
            IntrinsicReward: 内在奖励数据结构
        """
        self.timestep += 1
        
        rewards = {}
        
        # 1. 好奇心奖励（预测误差）
        curiosity_reward = 0.0
        if prediction is not None:
            pred_error = self.prediction_calculator.calculate_error(
                prediction, next_state, "state"
            )
            curiosity_reward = pred_error.error
            rewards[IntrinsicMotivationType.CURIOSITY] = curiosity_reward
        
        # 2. 新奇性奖励
        novelty_reward = self.info_gain_calculator.calculate_novelty(next_state, context)
        rewards[IntrinsicMotivationType.NOVELTY] = novelty_reward
        
        # 3. 更新状态分布
        self.info_gain_calculator.update_distribution(next_state, context)
        
        # 4. 惊讶度奖励
        surprise_reward = 0.0
        if prediction is not None:
            expected_val = np.mean(prediction)
            observed_val = np.mean(next_state)
            variance = np.var(prediction) + 1e-6
            surprise_reward = self.info_gain_calculator.calculate_surprise(
                observed_val, expected_val, variance
            )
            rewards[IntrinsicMotivationType.SURPRISE] = surprise_reward
        
        # 5. 能力感奖励
        competence_reward = 0.0
        if task_id is not None:
            performance = 1.0 / (1.0 + np.linalg.norm(next_state - state))
            self.competence_tracker.record_performance(task_id, performance)
            competence_reward = self.competence_tracker.get_competence(task_id)
            rewards[IntrinsicMotivationType.COMPETENCE] = competence_reward
        
        # 6. 学习进步奖励
        progress_reward = 0.0
        if task_id is not None:
            progress_reward = self.competence_tracker.get_learning_progress(task_id)
            progress_reward = max(0, progress_reward)
            rewards[IntrinsicMotivationType.LEARNING_PROGRESS] = progress_reward
        
        # 7. 控制感奖励
        effect_magnitude = np.linalg.norm(next_state - state)
        self.control_estimator.record_action_effect(action, effect_magnitude)
        control_reward = self.control_estimator.estimate_control(action)
        rewards[IntrinsicMotivationType.CONTROL] = control_reward
        
        # 加权求和
        total_reward = sum(
            self.weights[motivation_type] * reward_value
            for motivation_type, reward_value in rewards.items()
        )
        
        self.total_reward += total_reward
        
        intrinsic_reward = IntrinsicReward(
            motivation_type=self._get_dominant_motivation(rewards),
            reward_value=total_reward,
            state_description=f"State dim={len(state)}",
            action_taken=action,
            metadata={
                "individual_rewards": {k.value: v for k, v in rewards.items()},
                "timestep": self.timestep,
                "cumulative_reward": self.total_reward,
            }
        )
        
        return intrinsic_reward
    
    def _get_dominant_motivation(
        self,
        rewards: Dict[IntrinsicMotivationType, float]
    ) -> IntrinsicMotivationType:
        """获取主导动机类型"""
        if not rewards:
            return IntrinsicMotivationType.CURIOSITY
        
        weighted_rewards = {
            k: self.weights[k] * v for k, v in rewards.items()
        }
        return max(weighted_rewards, key=weighted_rewards.get)
    
    def decide_explore_or_exploit(
        self,
        state: np.ndarray,
        available_actions: List[str],
        q_values: Optional[Dict[str, float]] = None
    ) -> Tuple[str, bool]:
        """
        决定探索还是利用
        
        Args:
            state: 当前状态
            available_actions: 可用动作列表
            q_values: Q 值估计（可选）
            
        Returns:
            Tuple[str, bool]: (选择的动作，是否探索)
        """
        discrete_state = tuple(np.digitize(
            state,
            np.linspace(state.min(), state.max(), 10)
        ))
        
        self.state_visit_counts[discrete_state] = \
            self.state_visit_counts.get(discrete_state, 0) + 1
        
        state_count = self.state_visit_counts[discrete_state]
        
        if q_values is None:
            q_values = {a: 0.0 for a in available_actions}
        
        if np.random.random() < self.exploration_epsilon:
            action = np.random.choice(available_actions)
            is_exploring = True
        else:
            ucb_values = {}
            for action in available_actions:
                self.action_counts[action] = self.action_counts.get(action, 0) + 1
                action_count = self.action_counts[action]
                
                exploitation = q_values.get(action, 0)
                exploration_bonus = self.ucb_c * math.sqrt(
                    math.log(state_count + 1) / (action_count + 1e-6)
                )
                ucb_values[action] = exploitation + exploration_bonus
            
            action = max(ucb_values, key=ucb_values.get)
            is_exploring = action != max(q_values, key=q_values.get) if q_values else True
        
        self.action_counts[action] = self.action_counts.get(action, 0) + 1
        
        return action, is_exploring
    
    def generate_exploration_goal(
        self,
        current_state: np.ndarray,
        context: str = "global"
    ) -> ExplorationGoal:
        """
        自动生成探索目标
        
        Args:
            current_state: 当前状态
            context: 上下文标识
            
        Returns:
            ExplorationGoal: 生成的探索目标
        """
        high_error_regions = self._find_high_uncertainty_regions(context)
        novel_regions = self._find_novel_regions(context)
        
        if np.random.random() < 0.5 and high_error_regions:
            target = high_error_regions[0]
            motivation_type = IntrinsicMotivationType.CURIOSITY
            description = "Explore high prediction error region"
        elif novel_regions:
            target = novel_regions[0]
            motivation_type = IntrinsicMotivationType.NOVELTY
            description = "Explore novel state region"
        else:
            target = current_state + np.random.randn(*current_state.shape) * 0.5
            motivation_type = IntrinsicMotivationType.CURIOSITY
            description = "Random exploration"
        
        priority = self._calculate_goal_priority(target, current_state, context)
        
        goal = ExplorationGoal(
            goal_id=f"goal_{len(self.goals)}",
            description=description,
            target_state=target,
            priority=priority,
            motivation_type=motivation_type,
            created_at=self.timestep
        )
        
        self.goals.append(goal)
        return goal
    
    def _find_high_uncertainty_regions(
        self,
        context: str
    ) -> List[np.ndarray]:
        """找到高不确定性区域"""
        if not self.prediction_calculator.error_history:
            return []
        
        recent_errors = self.prediction_calculator.error_history[-20:]
        high_error_states = [
            e.actual for e in recent_errors
            if e.error > self.prediction_calculator.get_recent_average_error()
        ]
        
        return high_error_states[:5]
    
    def _find_novel_regions(self, context: str) -> List[np.ndarray]:
        """找到新奇区域"""
        if context not in self.info_gain_calculator.state_distribution:
            return []
        
        dist = self.info_gain_calculator.state_distribution[context]
        low_visit_indices = np.argsort(dist)[:10]
        
        regions = []
        for idx in low_visit_indices:
            region = np.random.randn(10) * 0.1 + idx * 0.1
            regions.append(region)
        
        return regions
    
    def _calculate_goal_priority(
        self,
        target: np.ndarray,
        current: np.ndarray,
        context: str
    ) -> float:
        """计算目标优先级"""
        distance = np.linalg.norm(target - current)
        novelty = self.info_gain_calculator.calculate_novelty(target, context)
        
        priority = novelty * 10.0 / (1.0 + distance * 0.1)
        return priority
    
    def get_next_goal(self) -> Optional[ExplorationGoal]:
        """获取下一个最高优先级的未完成目标"""
        incomplete_goals = [g for g in self.goals if not g.completed]
        
        if not incomplete_goals:
            return None
        
        return max(incomplete_goals, key=lambda g: g.priority)
    
    def mark_goal_completed(self, goal_id: str):
        """标记目标为已完成"""
        for goal in self.goals:
            if goal.goal_id == goal_id:
                goal.completed = True
                break
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "timestep": self.timestep,
            "total_intrinsic_reward": self.total_reward,
            "num_goals_generated": len(self.goals),
            "num_goals_completed": sum(1 for g in self.goals if g.completed),
            "unique_states_visited": len(self.state_visit_counts),
            "unique_actions_taken": len(self.action_counts),
            "average_prediction_error": self.prediction_calculator.get_recent_average_error(),
            "error_trend": self.prediction_calculator.get_error_trend(),
            "exploration_ratio": sum(1 for g in self.goals if g.motivation_type in [
                IntrinsicMotivationType.CURIOSITY,
                IntrinsicMotivationType.NOVELTY
            ]) / max(1, len(self.goals)),
        }


def demo():
    """演示内在动机引擎的使用"""
    print("=" * 60)
    print("内在动机与好奇心驱动模块演示")
    print("=" * 60)
    
    engine = IntrinsicMotivationEngine(
        curiosity_weight=1.0,
        novelty_weight=1.2,
        exploration_epsilon=0.3
    )
    
    state_dim = 5
    num_steps = 50
    
    state = np.random.randn(state_dim)
    actions = ["move_left", "move_right", "move_up", "move_down", "explore"]
    
    cumulative_reward = 0.0
    exploration_count = 0
    
    print(f"\n开始 {num_steps} 步模拟...\n")
    
    for step in range(num_steps):
        q_values = {a: np.random.randn() * 0.1 for a in actions}
        action, is_exploring = engine.decide_explore_or_exploit(state, actions, q_values)
        
        if is_exploring:
            exploration_count += 1
        
        next_state = state + np.random.randn(state_dim) * 0.3
        prediction = state + np.random.randn(state_dim) * 0.2
        
        reward = engine.compute_intrinsic_reward(
            state=state,
            action=action,
            next_state=next_state,
            prediction=prediction,
            task_id="demo_task",
            context="demo"
        )
        
        cumulative_reward += reward.reward_value
        
        if step % 10 == 0:
            print(f"Step {step}: Action={action}, Reward={reward.reward_value:.3f}, "
                  f"Type={reward.motivation_type.value}, Exploring={is_exploring}")
        
        state = next_state
        
        if step % 20 == 0 and step > 0:
            goal = engine.generate_exploration_goal(state)
            print(f"  → Generated goal: {goal.description} (priority={goal.priority:.2f})")
    
    stats = engine.get_statistics()
    
    print("\n" + "=" * 60)
    print("统计结果:")
    print(f"  总内在奖励：{stats['total_intrinsic_reward']:.2f}")
    print(f"  生成目标数：{stats['num_goals_generated']}")
    print(f"  访问状态数：{stats['unique_states_visited']}")
    print(f"  探索比例：{stats['exploration_ratio']:.2%}")
    print(f"  平均预测误差：{stats['average_prediction_error']:.3f}")
    print(f"  误差趋势：{stats['error_trend']:+.3f} (负值表示改进)")
    print("=" * 60)
    
    return stats


if __name__ == "__main__":
    demo()
