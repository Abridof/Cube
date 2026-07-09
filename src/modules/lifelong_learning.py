"""
阶段 16: 终身学习与神经可塑性 (Lifelong Learning & Neuroplasticity)

实现增量学习、灾难性遗忘避免、动态网络结构重组和技能迁移机制。
核心组件:
- EpisodicBuffer: 情节缓冲区
- SynapticPlasticity: 突触可塑性控制器
- KnowledgeDistiller: 知识蒸馏器
- SkillTransfer: 技能迁移引擎
- NeuralPruning: 神经修剪器
- LifelongLearner: 终身学习主引擎
"""

from __future__ import annotations
import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum
from collections import deque
import json


class PlasticityRule(Enum):
    """突触可塑性规则类型"""
    HEBBIAN = "hebbian"  # Hebbian 学习："一起激发的神经元连在一起"
    ANTI_HEBBIAN = "anti_hebbian"  # 反 Hebbian 学习
    STDP = "stdp"  # 脉冲时序依赖可塑性
    HOMEOSTATIC = "homeostatic"  # 稳态可塑性
    METAPLASTICITY = "metaplasticity"  # 元可塑性


class TransferType(Enum):
    """技能迁移类型"""
    POSITIVE = "positive"  # 正迁移（促进新任务）
    NEGATIVE = "negative"  # 负迁移（干扰新任务）
    NEUTRAL = "neutral"  # 零迁移
    BIDIRECTIONAL = "bidirectional"  # 双向迁移


class TaskCategory(Enum):
    """任务类别"""
    PERCEPTION = "perception"
    MEMORY = "memory"
    REASONING = "reasoning"
    MOTOR = "motor"
    SOCIAL = "social"
    CREATIVE = "creative"


@dataclass
class SynapticWeight:
    """突触权重数据"""
    source_id: str
    target_id: str
    weight: float
    importance: float = 1.0  # 对该突触对已学任务的重要性
    last_modified: float = field(default_factory=time.time)
    plasticity_rate: float = 0.1  # 可塑性速率
    
    def update_weight(self, delta: float, importance_factor: float = 1.0):
        """更新权重并记录重要性"""
        self.weight += delta * self.plasticity_rate * importance_factor
        self.last_modified = time.time()
    
    def to_dict(self) -> Dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "weight": self.weight,
            "importance": self.importance,
            "last_modified": self.last_modified,
            "plasticity_rate": self.plasticity_rate
        }


@dataclass
class Episode:
    """情节记忆单元"""
    episode_id: str
    task_type: TaskCategory
    input_pattern: List[float]
    output_pattern: List[float]
    reward: float
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    consolidation_level: float = 0.0  # 巩固程度 (0-1)
    
    def consolidate(self, strength: float = 0.1):
        """巩固情节记忆"""
        self.consolidation_level = min(1.0, self.consolidation_level + strength)
    
    def to_dict(self) -> Dict:
        return {
            "episode_id": self.episode_id,
            "task_type": self.task_type.value,
            "input_pattern": self.input_pattern,
            "output_pattern": self.output_pattern,
            "reward": self.reward,
            "timestamp": self.timestamp,
            "context": self.context,
            "consolidation_level": self.consolidation_level
        }


@dataclass
class TaskRepresentation:
    """任务表示"""
    task_id: str
    category: TaskCategory
    difficulty: float
    required_skills: Set[str]
    learned_parameters: Dict[str, float] = field(default_factory=dict)
    performance_history: List[float] = field(default_factory=list)
    
    def get_average_performance(self) -> float:
        if not self.performance_history:
            return 0.0
        return sum(self.performance_history) / len(self.performance_history)


class EpisodicBuffer:
    """
    情节缓冲区：存储关键学习事件
    支持记忆巩固、回放和优先级排序
    """
    
    def __init__(self, capacity: int = 1000, consolidation_threshold: float = 0.7):
        self.capacity = capacity
        self.consolidation_threshold = consolidation_threshold
        self.buffer: deque[Episode] = deque(maxlen=capacity)
        self.consolidated_episodes: List[Episode] = []
        self.priority_queue: List[Tuple[float, Episode]] = []
        
    def add_episode(self, episode: Episode) -> bool:
        """添加情节到缓冲区"""
        if len(self.buffer) >= self.capacity:
            # 移除最旧且未巩固的情节
            oldest = self.buffer[0]
            if oldest.consolidation_level < self.consolidation_threshold:
                self.buffer.popleft()
            else:
                return False
        
        self.buffer.append(episode)
        self._calculate_priority(episode)
        return True
    
    def _calculate_priority(self, episode: Episode):
        """计算情节优先级（基于奖励、新颖性和学习价值）"""
        novelty = 1.0 - episode.consolidation_level
        learning_value = abs(episode.reward) * novelty
        priority = learning_value * (1.0 + episode.consolidation_level)
        self.priority_queue.append((priority, episode))
        self.priority_queue.sort(key=lambda x: x[0], reverse=True)
    
    def sample_for_replay(self, batch_size: int = 32) -> List[Episode]:
        """采样情节用于回放"""
        if not self.priority_queue:
            return []
        
        # 优先选择高优先级情节
        total_priority = sum(p for p, _ in self.priority_queue)
        if total_priority == 0:
            return random.sample(list(self.buffer), min(batch_size, len(self.buffer)))
        
        sampled = []
        for _ in range(min(batch_size, len(self.priority_queue))):
            r = random.random() * total_priority
            cumulative = 0
            for priority, episode in self.priority_queue:
                cumulative += priority
                if r <= cumulative:
                    sampled.append(episode)
                    break
        
        return sampled
    
    def consolidate_episode(self, episode_id: str, strength: float = 0.1) -> bool:
        """巩固指定情节"""
        for episode in self.buffer:
            if episode.episode_id == episode_id:
                episode.consolidate(strength)
                if episode.consolidation_level >= self.consolidation_threshold:
                    self.consolidated_episodes.append(episode)
                    self.buffer.remove(episode)
                    self.priority_queue = [(p, e) for p, e in self.priority_queue 
                                          if e.episode_id != episode_id]
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """获取缓冲区统计信息"""
        return {
            "total_episodes": len(self.buffer) + len(self.consolidated_episodes),
            "active_episodes": len(self.buffer),
            "consolidated_episodes": len(self.consolidated_episodes),
            "average_consolidation": sum(e.consolidation_level for e in self.buffer) / 
                                    max(1, len(self.buffer)),
            "by_task_type": self._count_by_task_type()
        }
    
    def _count_by_task_type(self) -> Dict[str, int]:
        counts = {}
        for episode in self.buffer:
            key = episode.task_type.value
            counts[key] = counts.get(key, 0) + 1
        return counts


class SynapticPlasticity:
    """
    突触可塑性控制器
    实现多种可塑性规则，包括 Hebbian 学习和 EWC
    """
    
    def __init__(self, 
                 default_plasticity_rate: float = 0.1,
                 ewc_lambda: float = 0.5,
                 metaplasticity_window: int = 100):
        self.default_plasticity_rate = default_plasticity_rate
        self.ewc_lambda = ewc_lambda  # EWC 正则化系数
        self.metaplasticity_window = metaplasticity_window
        
        # 突触权重存储
        self.synapses: Dict[str, SynapticWeight] = {}
        
        # Fisher 信息矩阵近似（用于 EWC）
        self.fisher_information: Dict[str, float] = {}
        self.optimal_weights: Dict[str, float] = {}
        
        # 活动历史（用于 STDP 和元可塑性）
        self.activity_history: Dict[str, deque] = {}
        self.plasticity_modulators: Dict[str, float] = {}
        
    def create_synapse(self, source_id: str, target_id: str, 
                      initial_weight: float = 0.5) -> SynapticWeight:
        """创建新的突触连接"""
        synapse_id = f"{source_id}->{target_id}"
        if synapse_id not in self.synapses:
            self.synapses[synapse_id] = SynapticWeight(
                source_id=source_id,
                target_id=target_id,
                weight=initial_weight
            )
            self.activity_history[source_id] = deque(maxlen=self.metaplasticity_window)
            self.activity_history[target_id] = deque(maxlen=self.metaplasticity_window)
        return self.synapses[synapse_id]
    
    def apply_hebbian_learning(self, source_id: str, target_id: str,
                              source_activity: float, target_activity: float,
                              learning_rate: Optional[float] = None) -> float:
        """应用 Hebbian 学习规则"""
        synapse_id = f"{source_id}->{target_id}"
        if synapse_id not in self.synapses:
            self.create_synapse(source_id, target_id)
        
        synapse = self.synapses[synapse_id]
        lr = learning_rate or synapse.plasticity_rate
        
        # Hebbian 规则：Δw = η * pre * post
        delta = lr * source_activity * target_activity
        
        # 应用 EWC 约束
        ewc_penalty = self._calculate_ewc_penalty(synapse_id)
        delta -= ewc_penalty
        
        synapse.update_weight(delta)
        
        # 记录活动
        self._record_activity(source_id, source_activity)
        self._record_activity(target_id, target_activity)
        
        return delta
    
    def apply_stdp(self, pre_id: str, post_id: str, 
                   pre_spike_time: float, post_spike_time: float,
                   learning_rate: float = 0.01) -> float:
        """
        应用脉冲时序依赖可塑性 (STDP)
        如果突触前在突触后之前激发，增强连接；否则减弱
        """
        synapse_id = f"{pre_id}->{post_id}"
        if synapse_id not in self.synapses:
            self.create_synapse(pre_id, post_id)
        
        synapse = self.synapses[synapse_id]
        delta_t = post_spike_time - pre_spike_time
        
        # STDP 曲线
        if delta_t > 0:
            # LTP (长时程增强)
            delta = learning_rate * math.exp(-delta_t / 0.02)
        else:
            # LTD (长时程抑制)
            delta = -learning_rate * math.exp(delta_t / 0.02)
        
        synapse.update_weight(delta)
        return delta
    
    def _calculate_ewc_penalty(self, synapse_id: str) -> float:
        """计算 EWC (弹性权重巩固) 惩罚项"""
        if synapse_id not in self.fisher_information:
            return 0.0
        
        fisher = self.fisher_information[synapse_id]
        optimal = self.optimal_weights.get(synapse_id, 0.0)
        current = self.synapses[synapse_id].weight
        
        # EWC 惩罚：λ * F * (θ - θ*)
        penalty = self.ewc_lambda * fisher * (current - optimal)
        return penalty
    
    def store_optimal_weights(self, task_id: str, fisher_approximation: Dict[str, float]):
        """存储当前任务的最优权重和 Fisher 信息"""
        for synapse_id, weight in fisher_approximation.items():
            if synapse_id in self.synapses:
                self.optimal_weights[synapse_id] = self.synapses[synapse_id].weight
                # 累积 Fisher 信息
                prev_fisher = self.fisher_information.get(synapse_id, 0.0)
                self.fisher_information[synapse_id] = prev_fisher + weight
    
    def update_metaplasticity(self, neuron_id: str, activity: float):
        """更新元可塑性调节因子"""
        if neuron_id not in self.plasticity_modulators:
            self.plasticity_modulators[neuron_id] = 1.0
        
        # 高活动降低可塑性，低活动增加可塑性
        history = self.activity_history.get(neuron_id, deque())
        if len(history) > 0:
            avg_activity = sum(history) / len(history)
            if avg_activity > 0.8:
                self.plasticity_modulators[neuron_id] *= 0.95  # 降低可塑性
            elif avg_activity < 0.2:
                self.plasticity_modulators[neuron_id] *= 1.05  # 增加可塑性
        
        # 限制范围
        self.plasticity_modulators[neuron_id] = max(0.1, 
            min(2.0, self.plasticity_modulators[neuron_id]))
    
    def _record_activity(self, neuron_id: str, activity: float):
        """记录神经元活动"""
        if neuron_id in self.activity_history:
            self.activity_history[neuron_id].append(activity)
    
    def get_synapse_statistics(self) -> Dict:
        """获取突触统计信息"""
        if not self.synapses:
            return {"total_synapses": 0}
        
        weights = [s.weight for s in self.synapses.values()]
        importances = [s.importance for s in self.synapses.values()]
        
        return {
            "total_synapses": len(self.synapses),
            "average_weight": sum(weights) / len(weights),
            "weight_variance": sum((w - sum(weights)/len(weights))**2 
                                  for w in weights) / len(weights),
            "average_importance": sum(importances) / len(importances),
            "high_importance_count": sum(1 for i in importances if i > 0.8),
            "ewc_protected_count": len(self.fisher_information)
        }


class KnowledgeDistiller:
    """
    知识蒸馏器
    从复杂模型中提取核心知识，防止灾难性遗忘
    """
    
    def __init__(self, temperature: float = 2.0, distillation_ratio: float = 0.3):
        self.temperature = temperature  # 软化概率分布的温度
        self.distillation_ratio = distillation_ratio  # 保留知识的比例
        self.core_knowledge: Dict[str, Any] = {}
        self.knowledge_graph: Dict[str, Set[str]] = {}  # 知识依赖关系
        self.compression_history: List[Dict] = []
        
    def extract_core_knowledge(self, task_params: Dict[str, float], 
                              importance_scores: Dict[str, float]) -> Dict[str, float]:
        """从任务参数中提取核心知识"""
        # 按重要性排序
        sorted_params = sorted(importance_scores.items(), 
                              key=lambda x: x[1], reverse=True)
        
        # 保留最重要的参数
        keep_count = max(1, int(len(sorted_params) * self.distillation_ratio))
        core_params = {}
        
        for param_name, score in sorted_params[:keep_count]:
            if param_name in task_params:
                core_params[param_name] = task_params[param_name]
                self._update_knowledge_graph(param_name, score)
        
        return core_params
    
    def _update_knowledge_graph(self, param_name: str, importance: float):
        """更新知识依赖图"""
        if param_name not in self.core_knowledge:
            self.core_knowledge[param_name] = importance
            self.knowledge_graph[param_name] = set()
        else:
            self.core_knowledge[param_name] = max(
                self.core_knowledge[param_name], importance)
    
    def add_dependency(self, param_a: str, param_b: str):
        """添加知识依赖关系"""
        if param_a in self.knowledge_graph:
            self.knowledge_graph[param_a].add(param_b)
        if param_b in self.knowledge_graph:
            self.knowledge_graph[param_b].add(param_a)
    
    def generate_soft_targets(self, teacher_outputs: List[float]) -> List[float]:
        """生成软目标（软化概率分布）"""
        # 应用温度缩放
        exp_outputs = [math.exp(o / self.temperature) for o in teacher_outputs]
        sum_exp = sum(exp_outputs)
        return [e / sum_exp for e in exp_outputs]
    
    def calculate_distillation_loss(self, student_outputs: List[float],
                                   teacher_outputs: List[float]) -> float:
        """计算蒸馏损失（KL 散度）"""
        soft_targets = self.generate_soft_targets(teacher_outputs)
        soft_student = self.generate_soft_targets(student_outputs)
        
        # KL 散度
        loss = 0.0
        for t, s in zip(soft_targets, soft_student):
            if t > 0 and s > 0:
                loss += t * math.log(t / s)
        
        return loss
    
    def replay_core_knowledge(self, knowledge_id: str) -> Optional[Any]:
        """回放核心知识"""
        return self.core_knowledge.get(knowledge_id)
    
    def get_compression_statistics(self) -> Dict:
        """获取压缩统计信息"""
        total_params = len(self.core_knowledge)
        dependencies = sum(len(deps) for deps in self.knowledge_graph.values())
        
        return {
            "core_knowledge_items": total_params,
            "knowledge_dependencies": dependencies,
            "average_importance": sum(self.core_knowledge.values()) / 
                                 max(1, total_params),
            "compression_ratio": self.distillation_ratio
        }


class SkillTransfer:
    """
    技能迁移引擎
    实现跨领域知识应用和迁移学习
    """
    
    def __init__(self):
        self.source_tasks: Dict[str, TaskRepresentation] = {}
        self.transfer_matrix: Dict[Tuple[str, str], float] = {}  # 任务间迁移强度
        self.shared_representations: Dict[str, List[float]] = {}  # 共享表示
        self.transfer_history: List[Dict] = []
        
    def register_task(self, task: TaskRepresentation):
        """注册任务"""
        self.source_tasks[task.task_id] = task
    
    def calculate_transfer_potential(self, source_task_id: str, 
                                    target_task_id: str) -> Tuple[TransferType, float]:
        """计算两个任务间的迁移潜力"""
        if source_task_id not in self.source_tasks or \
           target_task_id not in self.source_tasks:
            return TransferType.NEUTRAL, 0.0
        
        source = self.source_tasks[source_task_id]
        target = self.source_tasks[target_task_id]
        
        # 计算技能重叠度
        shared_skills = source.required_skills & target.required_skills
        skill_overlap = len(shared_skills) / max(1, len(source.required_skills | 
                                                        target.required_skills))
        
        # 计算类别相似度
        category_similarity = 1.0 if source.category == target.category else 0.3
        
        # 综合迁移分数
        transfer_score = 0.6 * skill_overlap + 0.4 * category_similarity
        
        # 确定迁移类型
        if transfer_score > 0.7:
            transfer_type = TransferType.POSITIVE
        elif transfer_score < 0.2:
            transfer_type = TransferType.NEGATIVE
        else:
            transfer_type = TransferType.NEUTRAL
        
        # 缓存结果
        self.transfer_matrix[(source_task_id, target_task_id)] = transfer_score
        
        return transfer_type, transfer_score
    
    def transfer_knowledge(self, source_task_id: str, target_task_id: str,
                          knowledge: Dict[str, float]) -> Dict[str, float]:
        """执行知识迁移"""
        transfer_type, score = self.calculate_transfer_potential(
            source_task_id, target_task_id)
        
        if transfer_type == TransferType.NEGATIVE:
            # 负迁移：只迁移少量通用知识
            adapted_knowledge = {k: v * 0.1 for k, v in knowledge.items()}
        elif transfer_type == TransferType.POSITIVE:
            # 正迁移：充分利用源任务知识
            adapted_knowledge = knowledge.copy()
            # 根据目标任务调整
            if target_task_id in self.source_tasks:
                target = self.source_tasks[target_task_id]
                for skill in target.required_skills:
                    if skill in knowledge:
                        adapted_knowledge[skill] *= 1.2  # 增强相关技能
        else:
            # 中性迁移：适度迁移
            adapted_knowledge = {k: v * 0.5 for k, v in knowledge.items()}
        
        # 记录迁移
        self.transfer_history.append({
            "source": source_task_id,
            "target": target_task_id,
            "type": transfer_type.value,
            "score": score,
            "timestamp": time.time()
        })
        
        return adapted_knowledge
    
    def find_best_source_task(self, target_task: TaskRepresentation) -> Optional[str]:
        """为目标任务找到最佳源任务"""
        best_score = -1
        best_task = None
        
        for source_id in self.source_tasks:
            if source_id == target_task.task_id:
                continue
            
            _, score = self.calculate_transfer_potential(source_id, target_task.task_id)
            if score > best_score:
                best_score = score
                best_task = source_id
        
        return best_task if best_score > 0.3 else None
    
    def get_transfer_statistics(self) -> Dict:
        """获取迁移统计信息"""
        if not self.transfer_history:
            return {"total_transfers": 0}
        
        positive = sum(1 for t in self.transfer_history 
                      if t["type"] == TransferType.POSITIVE.value)
        negative = sum(1 for t in self.transfer_history 
                      if t["type"] == TransferType.NEGATIVE.value)
        
        return {
            "total_transfers": len(self.transfer_history),
            "positive_transfers": positive,
            "negative_transfers": negative,
            "neutral_transfers": len(self.transfer_history) - positive - negative,
            "average_transfer_score": sum(t["score"] for t in self.transfer_history) / 
                                     len(self.transfer_history),
            "registered_tasks": len(self.source_tasks)
        }


class NeuralPruning:
    """
    神经修剪器
    优化网络结构，移除冗余连接
    """
    
    def __init__(self, pruning_threshold: float = 0.05, 
                 activity_threshold: float = 0.1):
        self.pruning_threshold = pruning_threshold
        self.activity_threshold = activity_threshold
        self.pruned_connections: List[Dict] = []
        self.network_stats_history: List[Dict] = []
        
    def prune_low_importance_synapses(self, 
                                      synapses: Dict[str, SynapticWeight]) -> List[str]:
        """修剪低重要性的突触"""
        pruned = []
        
        for synapse_id, synapse in synapses.items():
            if synapse.importance < self.pruning_threshold:
                pruned.append(synapse_id)
                self.pruned_connections.append({
                    "synapse_id": synapse_id,
                    "importance": synapse.importance,
                    "weight": synapse.weight,
                    "timestamp": time.time()
                })
        
        return pruned
    
    def prune_inactive_neurons(self, neuron_activities: Dict[str, float]) -> List[str]:
        """修剪不活跃的神经元"""
        inactive = []
        
        for neuron_id, activity in neuron_activities.items():
            if abs(activity) < self.activity_threshold:
                inactive.append(neuron_id)
        
        return inactive
    
    def optimize_network_structure(self, 
                                   synapses: Dict[str, SynapticWeight],
                                   neuron_activities: Dict[str, float]) -> Dict:
        """执行完整的网络结构优化"""
        pruned_synapses = self.prune_low_importance_synapses(synapses)
        pruned_neurons = self.prune_inactive_neurons(neuron_activities)
        
        # 记录优化后的统计
        remaining_synapses = len(synapses) - len(pruned_synapses)
        remaining_neurons = len(neuron_activities) - len(pruned_neurons)
        
        stats = {
            "original_synapses": len(synapses),
            "pruned_synapses": len(pruned_synapses),
            "remaining_synapses": remaining_synapses,
            "original_neurons": len(neuron_activities),
            "pruned_neurons": len(pruned_neurons),
            "remaining_neurons": remaining_neurons,
            "synapse_pruning_ratio": len(pruned_synapses) / max(1, len(synapses)),
            "neuron_pruning_ratio": len(pruned_neurons) / max(1, len(neuron_activities)),
            "timestamp": time.time()
        }
        
        self.network_stats_history.append(stats)
        return stats
    
    def get_pruning_statistics(self) -> Dict:
        """获取修剪统计信息"""
        if not self.network_stats_history:
            return {"total_pruning_operations": 0}
        
        latest = self.network_stats_history[-1]
        total_pruned_synapses = sum(s["pruned_synapses"] 
                                   for s in self.network_stats_history)
        
        return {
            "total_pruning_operations": len(self.network_stats_history),
            "total_synapses_pruned": total_pruned_synapses,
            "latest_pruning_ratio": latest.get("synapse_pruning_ratio", 0),
            "connections_logged": len(self.pruned_connections)
        }


class LifelongLearner:
    """
    终身学习主引擎
    整合所有组件实现持续学习而不遗忘
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # 初始化各组件
        self.episodic_buffer = EpisodicBuffer(
            capacity=self.config.get("buffer_capacity", 1000)
        )
        self.synaptic_plasticity = SynapticPlasticity(
            ewc_lambda=self.config.get("ewc_lambda", 0.5)
        )
        self.knowledge_distiller = KnowledgeDistiller(
            temperature=self.config.get("temperature", 2.0)
        )
        self.skill_transfer = SkillTransfer()
        self.neural_pruner = NeuralPruning(
            pruning_threshold=self.config.get("pruning_threshold", 0.05)
        )
        
        # 学习状态
        self.current_task: Optional[TaskRepresentation] = None
        self.completed_tasks: Dict[str, TaskRepresentation] = {}
        self.learning_phase: str = "idle"  # idle, encoding, consolidation, retrieval
        self.global_learning_rate: float = 0.1
        
        # 元学习器
        self.meta_learning_rates: Dict[str, float] = {}
        self.task_difficulty_estimates: Dict[str, float] = {}
        
    def start_learning_task(self, task: TaskRepresentation):
        """开始学习新任务"""
        self.current_task = task
        self.learning_phase = "encoding"
        
        # 检查是否有可迁移的源任务
        best_source = self.skill_transfer.find_best_source_task(task)
        if best_source:
            print(f"检测到可迁移知识：{best_source} -> {task.task_id}")
        
        # 注册任务
        self.skill_transfer.register_task(task)
    
    def learn_from_experience(self, input_pattern: List[float], 
                             output_pattern: List[float],
                             reward: float,
                             neuron_activities: Optional[Dict[str, float]] = None) -> Dict:
        """从经验中学习"""
        if not self.current_task:
            raise ValueError("No active task. Call start_learning_task first.")
        
        episode = Episode(
            episode_id=f"ep_{time.time()}_{random.randint(0, 1000)}",
            task_type=self.current_task.category,
            input_pattern=input_pattern,
            output_pattern=output_pattern,
            reward=reward
        )
        
        # 添加到情节缓冲区
        self.episodic_buffer.add_episode(episode)
        
        # 更新突触可塑性
        if neuron_activities:
            for neuron_id, activity in neuron_activities.items():
                self.synaptic_plasticity.update_metaplasticity(neuron_id, activity)
        
        # 更新任务性能历史
        self.current_task.performance_history.append(reward)
        
        # 模拟突触学习
        learning_result = self._simulate_synaptic_learning(
            input_pattern, output_pattern, reward)
        
        return {
            "episode_added": True,
            "learning_delta": learning_result.get("total_delta", 0),
            "buffer_size": len(self.episodic_buffer.buffer),
            "phase": self.learning_phase
        }
    
    def _simulate_synaptic_learning(self, inputs: List[float], 
                                   outputs: List[float],
                                   reward: float) -> Dict:
        """模拟突触学习过程"""
        total_delta = 0
        
        # 创建虚拟神经元并应用 Hebbian 学习
        for i, inp in enumerate(inputs):
            for j, out in enumerate(outputs):
                source_id = f"input_{i}"
                target_id = f"output_{j}"
                
                # 创建突触
                self.synaptic_plasticity.create_synapse(source_id, target_id)
                
                # 应用 Hebbian 学习
                delta = self.synaptic_plasticity.apply_hebbian_learning(
                    source_id, target_id, inp, out,
                    learning_rate=self.global_learning_rate * abs(reward)
                )
                total_delta += abs(delta)
        
        return {"total_delta": total_delta}
    
    def consolidate_knowledge(self, strength: float = 0.1):
        """巩固已学知识"""
        self.learning_phase = "consolidation"
        
        # 采样情节进行回放
        episodes = self.episodic_buffer.sample_for_replay(batch_size=32)
        
        consolidated_count = 0
        for episode in episodes:
            if self.episodic_buffer.consolidate_episode(episode.episode_id, strength):
                consolidated_count += 1
        
        # 提取核心知识
        if self.current_task:
            task_params = self.current_task.learned_parameters
            importance_scores = {k: 1.0 for k in task_params.keys()}
            core_knowledge = self.knowledge_distiller.extract_core_knowledge(
                task_params, importance_scores)
            
            # 存储最优权重以防止遗忘
            fisher_approx = {k: 1.0 for k in core_knowledge.keys()}
            self.synaptic_plasticity.store_optimal_weights(
                self.current_task.task_id, fisher_approx)
        
        self.learning_phase = "idle"
        
        return {
            "consolidated_episodes": consolidated_count,
            "core_knowledge_extracted": len(self.knowledge_distiller.core_knowledge),
            "phase": self.learning_phase
        }
    
    def complete_task(self, performance: float):
        """完成任务并记录"""
        if not self.current_task:
            return
        
        self.current_task.performance_history.append(performance)
        self.completed_tasks[self.current_task.task_id] = self.current_task
        
        # 评估任务难度
        avg_perf = self.current_task.get_average_performance()
        self.task_difficulty_estimates[self.current_task.task_id] = 1.0 - avg_perf
        
        # 调整全局学习率（元学习）
        self._adapt_learning_rate(performance)
        
        # 可选：执行网络修剪
        if self.config.get("auto_prune", False):
            self._auto_prune_network()
        
        self.current_task = None
        self.learning_phase = "idle"
    
    def _adapt_learning_rate(self, performance: float):
        """自适应调整学习率"""
        if performance > 0.8:
            # 表现好，降低学习率以稳定
            self.global_learning_rate *= 0.95
        elif performance < 0.3:
            # 表现差，提高学习率以加快学习
            self.global_learning_rate *= 1.05
        
        # 限制范围
        self.global_learning_rate = max(0.01, min(0.5, self.global_learning_rate))
    
    def _auto_prune_network(self):
        """自动修剪网络"""
        synapses = self.synaptic_plasticity.synapses
        activities = {}
        
        # 收集神经元活动
        for neuron_id, history in self.synaptic_plasticity.activity_history.items():
            if history:
                activities[neuron_id] = sum(history) / len(history)
        
        if activities:
            self.neural_pruner.optimize_network_structure(synapses, activities)
    
    def retrieve_knowledge(self, query_task_type: TaskCategory) -> List[Episode]:
        """检索相关知识"""
        self.learning_phase = "retrieval"
        
        # 从情节缓冲区检索
        relevant_episodes = [
            ep for ep in self.episodic_buffer.buffer
            if ep.task_type == query_task_type and ep.consolidation_level > 0.5
        ]
        
        # 从核心知识检索
        # (这里可以扩展更复杂的检索逻辑)
        
        self.learning_phase = "idle"
        return relevant_episodes
    
    def transfer_to_new_task(self, new_task: TaskRepresentation) -> Dict[str, float]:
        """将已有知识迁移到新任务"""
        source_task_id = self.skill_transfer.find_best_source_task(new_task)
        
        if not source_task_id:
            return {}
        
        source_task = self.completed_tasks.get(source_task_id)
        if not source_task:
            return {}
        
        # 执行知识迁移
        transferred_knowledge = self.skill_transfer.transfer_knowledge(
            source_task_id, new_task.task_id, source_task.learned_parameters)
        
        # 初始化新任务的参数
        new_task.learned_parameters = transferred_knowledge
        
        return transferred_knowledge
    
    def get_learning_statistics(self) -> Dict:
        """获取完整的学习统计信息"""
        return {
            "current_phase": self.learning_phase,
            "global_learning_rate": self.global_learning_rate,
            "completed_tasks": len(self.completed_tasks),
            "episodic_buffer": self.episodic_buffer.get_statistics(),
            "synaptic_plasticity": self.synaptic_plasticity.get_synapse_statistics(),
            "knowledge_distiller": self.knowledge_distiller.get_compression_statistics(),
            "skill_transfer": self.skill_transfer.get_transfer_statistics(),
            "neural_pruning": self.neural_pruner.get_pruning_statistics(),
            "task_difficulties": self.task_difficulty_estimates
        }
    
    def export_state(self) -> Dict:
        """导出学习状态"""
        return {
            "config": self.config,
            "completed_tasks": [t.task_id for t in self.completed_tasks.values()],
            "statistics": self.get_learning_statistics(),
            "core_knowledge": self.knowledge_distiller.core_knowledge,
            "transfer_history": self.skill_transfer.transfer_history[-10:]  # 最近 10 次
        }


# 工具函数
def create_sample_task(task_id: str, category: TaskCategory, 
                      difficulty: float, skills: List[str]) -> TaskRepresentation:
    """创建示例任务"""
    return TaskRepresentation(
        task_id=task_id,
        category=category,
        difficulty=difficulty,
        required_skills=set(skills)
    )


def simulate_learning_session(learner: LifelongLearner, 
                             num_episodes: int = 100) -> Dict:
    """模拟学习会话"""
    results = []
    
    for i in range(num_episodes):
        # 生成随机输入输出
        inputs = [random.random() for _ in range(5)]
        outputs = [random.random() for _ in range(3)]
        reward = random.gauss(0.5, 0.2)
        
        # 模拟神经元活动
        activities = {f"n_{j}": random.random() for j in range(8)}
        
        result = learner.learn_from_experience(inputs, outputs, reward, activities)
        results.append(result)
        
        # 定期巩固
        if i % 20 == 0 and i > 0:
            learner.consolidate_knowledge()
    
    return {
        "episodes_learned": num_episodes,
        "final_buffer_size": len(learner.episodic_buffer.buffer),
        "average_learning_delta": sum(r["learning_delta"] for r in results) / num_episodes
    }
