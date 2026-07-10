"""
Symbol Grounding Engine v1.0
=============================
符号接地系统 - 解决符号与感知的连接问题

理论基础：
1. Harnad 的符号接地问题
2. Steels 的接地语言游戏
3. 感觉运动理论 (Sensorimotor Theory)
4. 具身认知 (Embodied Cognition)

Author: AI Assistant (Computer Scientist & AGI Researcher)
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import math
import random

from .advanced_types import (
    GroundingLink,
    SensorimotorSchema,
    UCRTyped,
    ModalityType,
)


@dataclass
class PerceptualAnchor:
    """感知锚点 - 符号与感知经验的连接点"""
    symbol: str
    perceptual_features: Dict[str, float]
    modality: str
    confidence: float = 0.5
    instances: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update(self, features: Dict[str, float], learning_rate: float = 0.1):
        """更新感知特征"""
        for feat, value in features.items():
            if feat in self.perceptual_features:
                # 指数移动平均
                old = self.perceptual_features[feat]
                self.perceptual_features[feat] = old + learning_rate * (value - old)
            else:
                self.perceptual_features[feat] = value
        
        self.instances += 1
        self.last_updated = datetime.now()
        self.confidence = min(1.0, self.instances / 10.0)


@dataclass
class ActionEffectPair:
    """动作 - 效果对"""
    action: str
    expected_effect: Dict[str, float]
    actual_effect: Optional[Dict[str, float]] = None
    prediction_error: float = 0.0
    
    def compute_error(self):
        """计算预测误差"""
        if self.actual_effect is None:
            return
        
        total_error = 0.0
        count = 0
        
        for key, expected in self.expected_effect.items():
            if key in self.actual_effect:
                total_error += abs(expected - self.actual_effect[key])
                count += 1
        
        self.prediction_error = total_error / count if count > 0 else 0.0


class GroundingEngine:
    """
    符号接地引擎
    
    实现机制：
    1. 感知锚定 (Perceptual Anchoring)
    2. 感觉运动学习 (Sensorimotor Learning)
    3. 跨模态关联 (Cross-modal Association)
    4. 语境依赖激活 (Context-dependent Activation)
    """
    
    def __init__(self):
        # 符号到感知锚点的映射
        self.anchors: Dict[str, PerceptualAnchor] = {}
        
        # 感觉运动模式库
        self.sensorimotor_schemas: List[SensorimotorSchema] = []
        
        # 动作 - 效果关联
        self.action_effects: Dict[str, List[ActionEffectPair]] = {}
        
        # 跨模态关联矩阵
        self.cross_modal_weights: Dict[Tuple[str, str], float] = {}
        
        # 语境模型
        self.context_vectors: Dict[str, Dict[str, float]] = {}
    
    def ground_symbol(
        self,
        symbol: str,
        perceptual_input: Dict[str, float],
        modality: str,
        context: Optional[str] = None
    ) -> GroundingLink:
        """
        将符号接地到感知输入
        
        Args:
            symbol: 符号名称
            perceptual_input: 感知特征向量
            modality: 模态类型
            context: 语境信息
        
        Returns:
            GroundingLink: 接地链接
        """
        if symbol not in self.anchors:
            # 创建新的感知锚点
            self.anchors[symbol] = PerceptualAnchor(
                symbol=symbol,
                perceptual_features=perceptual_input.copy(),
                modality=modality
            )
        else:
            # 更新现有锚点
            self.anchors[symbol].update(perceptual_input)
        
        # 计算关联强度
        anchor = self.anchors[symbol]
        association_strength = self._compute_association_strength(
            perceptual_input,
            anchor.perceptual_features
        )
        
        # 考虑语境影响
        if context and context in self.context_vectors:
            context_mod = self._context_modulation(context, symbol)
            association_strength *= context_mod
        
        return GroundingLink(
            symbol=symbol,
            percept=f"{modality}:{anchor.instances}",
            association_strength=association_strength,
            context=context or "none",
            learned_at=datetime.now().isoformat()
        )
    
    def _compute_association_strength(
        self,
        input_features: Dict[str, float],
        anchor_features: Dict[str, float]
    ) -> float:
        """计算关联强度 (基于余弦相似度)"""
        # 找到共同特征
        common_features = set(input_features.keys()) & set(anchor_features.keys())
        
        if not common_features:
            return 0.0
        
        # 计算余弦相似度
        dot_product = sum(
            input_features[f] * anchor_features[f]
            for f in common_features
        )
        
        norm_input = math.sqrt(sum(v**2 for v in input_features.values()))
        norm_anchor = math.sqrt(sum(v**2 for v in anchor_features.values()))
        
        if norm_input < 1e-10 or norm_anchor < 1e-10:
            return 0.0
        
        return dot_product / (norm_input * norm_anchor)
    
    def _context_modulation(self, context: str, symbol: str) -> float:
        """语境调制因子"""
        if context not in self.context_vectors:
            return 1.0
        
        context_vec = self.context_vectors[context]
        
        # 简化：如果符号在语境中有高权重，增强关联
        return context_vec.get(symbol, 1.0)
    
    def learn_sensorimotor_schema(
        self,
        action: str,
        sensory_prediction: Dict[str, float],
        actual_sensation: Dict[str, float]
    ) -> SensorimotorSchema:
        """
        学习感觉运动模式
        
        基于预测误差进行学习和更新
        """
        # 计算预测误差
        error = self._compute_prediction_error(
            sensory_prediction,
            actual_sensation
        )
        
        schema = SensorimotorSchema(
            action=action,
            sensory_prediction=str(sensory_prediction),
            actual_sensation=str(actual_sensation),
            prediction_error=error
        )
        
        self.sensorimotor_schemas.append(schema)
        
        # 更新动作 - 效果关联
        self._update_action_effect(action, sensory_prediction, actual_sensation)
        
        return schema
    
    def _compute_prediction_error(
        self,
        prediction: Dict[str, float],
        actual: Dict[str, float]
    ) -> float:
        """计算预测误差 (MSE)"""
        all_keys = set(prediction.keys()) | set(actual.keys())
        
        if not all_keys:
            return 0.0
        
        squared_errors = []
        for key in all_keys:
            pred_val = prediction.get(key, 0.0)
            actual_val = actual.get(key, 0.0)
            squared_errors.append((pred_val - actual_val) ** 2)
        
        return sum(squared_errors) / len(squared_errors)
    
    def _update_action_effect(
        self,
        action: str,
        prediction: Dict[str, float],
        actual: Dict[str, float]
    ):
        """更新动作 - 效果关联"""
        pair = ActionEffectPair(
            action=action,
            expected_effect=prediction,
            actual_effect=actual
        )
        pair.compute_error()
        
        if action not in self.action_effects:
            self.action_effects[action] = []
        
        self.action_effects[action].append(pair)
        
        # 限制历史记录大小
        if len(self.action_effects[action]) > 100:
            self.action_effects[action] = self.action_effects[action][-100:]
    
    def predict_effect(self, action: str) -> Dict[str, float]:
        """预测动作效果"""
        if action not in self.action_effects:
            return {}
        
        pairs = self.action_effects[action]
        if not pairs:
            return {}
        
        # 使用最近的效应预测 (加权平均)
        weights = []
        effects = []
        
        for i, pair in enumerate(reversed(pairs[-10:])):
            weight = 1.0 / (1.0 + pair.prediction_error)
            weights.append(weight)
            effects.append(pair.expected_effect)
        
        if not weights:
            return {}
        
        # 加权平均
        result: Dict[str, float] = {}
        total_weight = sum(weights)
        
        for effect, weight in zip(effects, weights):
            for key, value in effect.items():
                if key not in result:
                    result[key] = 0.0
                result[key] += weight * value / total_weight
        
        return result
    
    def establish_cross_modal_link(
        self,
        modality1: str,
        feature1: str,
        modality2: str,
        feature2: str,
        strength: float
    ):
        """建立跨模态链接"""
        key = (f"{modality1}:{feature1}", f"{modality2}:{feature2}")
        
        if key not in self.cross_modal_weights:
            self.cross_modal_weights[key] = 0.0
        
        # 增量学习
        old = self.cross_modal_weights[key]
        self.cross_modal_weights[key] = old + 0.1 * (strength - old)
    
    def get_grounding_confidence(self, symbol: str, context: Optional[str] = None) -> float:
        """获取符号接地的置信度"""
        if symbol not in self.anchors:
            return 0.0
        
        anchor = self.anchors[symbol]
        base_confidence = anchor.confidence
        
        # 语境调制
        if context and context in self.context_vectors:
            context_mod = self._context_modulation(context, symbol)
            base_confidence *= context_mod
        
        return min(1.0, base_confidence)
    
    def simulate_perception(
        self,
        symbol: str,
        context: Optional[str] = None
    ) -> Optional[Dict[str, float]]:
        """
        模拟感知 - 给定符号，生成预期的感知特征
        
        这是接地问题的逆向过程
        """
        if symbol not in self.anchors:
            return None
        
        anchor = self.anchors[symbol]
        features = anchor.perceptual_features.copy()
        
        # 根据语境调整
        if context and context in self.context_vectors:
            context_vec = self.context_vectors[context]
            for feat in features:
                context_key = f"{symbol}:{feat}"
                if context_key in context_vec:
                    features[feat] *= context_vec[context_key]
        
        return features


# ============================================================================
# 语境学习器
# ============================================================================

class ContextLearner:
    """
    语境学习器
    
    学习不同语境下符号的含义变化
    """
    
    def __init__(self, embedding_dim: int = 50):
        self.embedding_dim = embedding_dim
        self.context_embeddings: Dict[str, Dict[str, float]] = {}
        self.symbol_contexts: Dict[str, Set[str]] = {}
    
    def learn_context(
        self,
        context_id: str,
        co_occurrences: Dict[str, int]
    ):
        """
        学习语境表示
        
        Args:
            context_id: 语境标识
            co_occurrences: 符号共现计数
        """
        # 简单的 TF-IDF 风格权重
        total = sum(co_occurrences.values())
        
        if total == 0:
            return
        
        weights: Dict[str, float] = {}
        for symbol, count in co_occurrences.items():
            # 频率权重
            tf = count / total
            weights[symbol] = tf
            
            # 更新符号 - 语境关联
            if symbol not in self.symbol_contexts:
                self.symbol_contexts[symbol] = set()
            self.symbol_contexts[symbol].add(context_id)
        
        self.context_embeddings[context_id] = weights
    
    def get_context_similarity(
        self,
        context1: str,
        context2: str
    ) -> float:
        """计算语境相似度"""
        if context1 not in self.context_embeddings or \
           context2 not in self.context_embeddings:
            return 0.0
        
        vec1 = self.context_embeddings[context1]
        vec2 = self.context_embeddings[context2]
        
        # 余弦相似度
        all_symbols = set(vec1.keys()) | set(vec2.keys())
        
        dot = sum(vec1.get(s, 0) * vec2.get(s, 0) for s in all_symbols)
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if norm1 < 1e-10 or norm2 < 1e-10:
            return 0.0
        
        return dot / (norm1 * norm2)
    
    def find_relevant_contexts(
        self,
        symbol: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """找到与符号最相关的语境"""
        if symbol not in self.symbol_contexts:
            return []
        
        contexts = self.symbol_contexts[symbol]
        scores = []
        
        for ctx in contexts:
            score = self.context_embeddings.get(ctx, {}).get(symbol, 0.0)
            scores.append((ctx, score))
        
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]
