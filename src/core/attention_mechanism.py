"""
Attention Mechanism Module v1.0
================================
基于认知科学的注意力机制实现

理论基础：
1. Baddeley 工作记忆模型中的中央执行系统
2. Treisman 的特征整合理论
3. Posner 的注意力定向理论
4. Global Workspace Theory (GWT)

Author: AI Assistant (Computer Scientist & AGI Researcher)
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import math
import random

from .advanced_types import (
    AttentionFocus,
    UCRTyped,
    WorkingMemoryItemTyped,
)
from .types import MAX_WORKING_MEMORY_ITEMS


@dataclass
class AttentionalResource:
    """注意力资源单元"""
    target_id: str
    relevance: float  # 相关性 0-1
    salience: float   # 显著性 0-1
    priority: float   # 优先级 0-1
    expected_value: float  # 期望价值
    cost: float       # 注意成本
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_attention_score(self, weights: Dict[str, float] = None) -> float:
        """计算注意力得分"""
        if weights is None:
            weights = {
                'relevance': 0.3,
                'salience': 0.2,
                'priority': 0.3,
                'expected_value': 0.2,
                'cost': -0.1
            }
        
        score = 0.0
        for key, weight in weights.items():
            if key == 'cost':
                score += weight * min(1.0, getattr(self, key, 0.0))
            else:
                score += weight * getattr(self, key, 0.0)
        
        return max(0.0, min(1.0, score))


@dataclass
class AttentionalBlink:
    """注意瞬脱现象模拟"""
    last_target_time: Optional[datetime] = None
    blink_duration_ms: float = 200.0  # 典型值 200-500ms
    recovery_rate: float = 0.01  # 恢复速率
    
    def is_in_blink(self) -> bool:
        """检查是否处于注意瞬脱期"""
        if self.last_target_time is None:
            return False
        
        elapsed = (datetime.now() - self.last_target_time).total_seconds() * 1000
        return elapsed < self.blink_duration_ms
    
    def get_effectiveness(self) -> float:
        """获取当前注意力有效性"""
        if self.last_target_time is None:
            return 1.0
        
        elapsed = (datetime.now() - self.last_target_time).total_seconds() * 1000
        
        if elapsed >= self.blink_duration_ms:
            return 1.0
        
        # 线性恢复
        return elapsed / self.blink_duration_ms
    
    def record_target(self):
        """记录目标出现"""
        self.last_target_time = datetime.now()


class AttentionMechanism:
    """
    注意力机制
    
    实现功能：
    1. 选择性注意 (Selective Attention)
    2. 分配性注意 (Divided Attention)
    3. 持续性注意 (Sustained Attention)
    4. 注意转移 (Attention Shifting)
    5. 注意瞬脱 (Attentional Blink)
    """
    
    def __init__(
        self,
        capacity: int = 4,  # 注意容量 (Cowan's K)
        decay_rate: float = 0.1
    ):
        # 注意容量限制
        self.capacity = min(capacity, MAX_WORKING_MEMORY_ITEMS)
        self.decay_rate = decay_rate
        
        # 当前注意焦点
        self.foci: List[AttentionalResource] = []
        
        # 注意历史
        self.history: List[Tuple[str, datetime]] = []
        
        # 注意瞬脱
        self.blink = AttentionalBlink()
        
        # 语境过滤器
        self.context_filter: Optional[Set[str]] = None
        
        # 显著性图 (用于视觉注意模拟)
        self.saliency_map: Dict[str, float] = {}
        
        # 任务集 (Task Set)
        self.task_set: Dict[str, float] = {}
    
    def select(
        self,
        candidates: List[UCRTyped],
        query: Optional[str] = None,
        top_k: Optional[int] = None
    ) -> List[AttentionFocus]:
        """
        选择性注意 - 从候选中选择注意焦点
        
        Args:
            candidates: 候选项目列表
            query: 查询/目标
            top_k: 返回数量限制
        
        Returns:
            选定的注意焦点列表
        """
        if not candidates:
            return []
        
        k = top_k or self.capacity
        
        # 检查注意瞬脱
        blink_factor = self.blink.get_effectiveness()
        
        # 计算每个候选的注意力得分
        resources = []
        for candidate in candidates:
            resource = self._compute_attention_resource(candidate, query)
            resources.append(resource)
        
        # 应用语境过滤
        if self.context_filter:
            resources = [
                r for r in resources 
                if r.target_id in self.context_filter
            ]
        
        # 按得分排序
        resources.sort(key=lambda r: -r.get_attention_score())
        
        # 选择 top-k
        selected = resources[:k]
        
        # 应用注意瞬脱效应
        for resource in selected:
            # 降低新目标的注意效果
            pass
        
        # 转换为 AttentionFocus
        foci = []
        for resource in selected:
            focus = AttentionFocus(
                target_id=resource.target_id,
                relevance_score=resource.relevance,
                priority=resource.priority,
                duration_ms=int(1000 / (1.0 - resource.get_attention_score() + 0.01))
            )
            foci.append(focus)
        
        # 更新当前焦点
        self.foci = selected
        
        # 记录历史
        for resource in selected:
            self.history.append((resource.target_id, datetime.now()))
        
        # 记录注意瞬脱
        if selected:
            self.blink.record_target()
        
        return foci
    
    def _compute_attention_resource(
        self,
        item: UCRTyped,
        query: Optional[str] = None
    ) -> AttentionalResource:
        """计算注意力资源"""
        item_id = item.get('symbol', str(item))
        
        # 基础显著性 (从内容提取)
        salience = self._compute_salience(item)
        
        # 相关性 (与查询匹配)
        relevance = self._compute_relevance(item, query) if query else 0.5
        
        # 优先级 (从元数据)
        metadata = item.get('metadata', {})
        priority = metadata.get('priority', 0.5)
        
        # 期望价值 (基于历史)
        expected_value = self._estimate_expected_value(item_id)
        
        # 注意成本 (新颖性越高成本越低)
        cost = self._compute_attention_cost(item_id)
        
        return AttentionalResource(
            target_id=item_id,
            relevance=relevance,
            salience=salience,
            priority=priority,
            expected_value=expected_value,
            cost=cost
        )
    
    def _compute_salience(self, item: UCRTyped) -> float:
        """计算显著性"""
        # 基于内容的显著性
        content = item.get('content', '')
        
        # 简化：长度、特殊字符等作为显著性指标
        length_factor = min(1.0, len(content) / 100.0)
        
        # 检查是否有高置信度
        metadata = item.get('metadata', {})
        confidence = metadata.get('confidence', 0.5)
        
        # 向量范数 (如果有)
        vector = item.get('vector')
        vector_norm = 0.0
        if vector:
            vector_norm = math.sqrt(sum(v**2 for v in vector)) / 10.0
            vector_norm = min(1.0, vector_norm)
        
        return 0.3 * length_factor + 0.4 * confidence + 0.3 * vector_norm
    
    def _compute_relevance(
        self,
        item: UCRTyped,
        query: Optional[str]
    ) -> float:
        """计算相关性"""
        if not query:
            return 0.5
        
        content = item.get('content', '').lower()
        symbol = item.get('symbol', '').lower()
        
        # 简单的词匹配
        query_words = set(query.lower().split())
        content_words = set(content.split())
        symbol_words = set(symbol.split())
        
        all_words = content_words | symbol_words
        
        if not all_words:
            return 0.0
        
        matches = len(query_words & all_words)
        return min(1.0, matches / len(query_words))
    
    def _estimate_expected_value(self, item_id: str) -> float:
        """估计期望价值"""
        # 基于历史访问频率
        visits = sum(1 for iid, _ in self.history if iid == item_id)
        
        if visits == 0:
            return 0.5
        
        # 最近访问更有价值
        recent_visits = sum(
            1 for iid, ts in self.history[-100:]
            if iid == item_id
        )
        
        return min(1.0, 0.5 + 0.1 * recent_visits)
    
    def _compute_attention_cost(self, item_id: str) -> float:
        """计算注意成本"""
        # 已注意过的项目成本更低
        visits = sum(1 for iid, _ in self.history if iid == item_id)
        
        if visits == 0:
            return 0.5  # 新项目中等成本
        
        return max(0.1, 0.5 - 0.1 * visits)
    
    def shift(self, new_focus: str) -> bool:
        """
        转移注意力到新焦点
        
        模拟注意转移成本
        """
        if not self.foci:
            # 没有当前焦点，直接设置
            self.foci = [AttentionalResource(target_id=new_focus, relevance=1.0, salience=1.0, priority=1.0, expected_value=1.0, cost=0.0)]
            self.history.append((new_focus, datetime.now()))
            self.blink.record_target()
            return True
        
        # 检查是否在注意瞬脱期
        if self.blink.is_in_blink():
            return False
        
        # 添加新焦点
        new_resource = AttentionalResource(
            target_id=new_focus,
            relevance=1.0,
            salience=1.0,
            priority=1.0,
            expected_value=1.0,
            cost=0.5  # 转移成本
        )
        
        # 替换最低优先级的焦点
        self.foci.sort(key=lambda r: r.get_attention_score())
        self.foci[0] = new_resource
        
        self.history.append((new_focus, datetime.now()))
        self.blink.record_target()
        
        return True
    
    def divide(
        self,
        targets: List[str],
        weights: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """
        分配性注意 - 同时注意多个目标
        
        注意资源有限，需要在目标间分配
        """
        if not targets:
            return {}
        
        n = len(targets)
        
        # 注意资源随目标数量递减 (Wickens 的多重资源理论)
        total_resource = 1.0 / (1.0 + 0.3 * (n - 1))
        
        if weights is None:
            weights = [1.0] * n
        
        # 归一化权重
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        # 分配资源
        allocation = {}
        for target, weight in zip(targets, normalized_weights):
            allocation[target] = total_resource * weight
        
        return allocation
    
    def sustain(self, duration_ms: float) -> float:
        """
        持续性注意 - 维持注意力一段时间
        
        返回注意力维持的有效性 (会随时间衰减)
        """
        # 警觉性衰减函数 (指数衰减)
        effectiveness = math.exp(-self.decay_rate * duration_ms / 1000.0)
        
        return max(0.1, effectiveness)
    
    def set_context(self, context_items: Set[str]):
        """设置语境过滤器"""
        self.context_filter = context_items
    
    def clear_context(self):
        """清除语境过滤器"""
        self.context_filter = None
    
    def update_saliency_map(self, updates: Dict[str, float]):
        """更新显著性图"""
        for key, value in updates.items():
            old = self.saliency_map.get(key, 0.0)
            # 指数移动平均
            self.saliency_map[key] = old + 0.1 * (value - old)
    
    def get_current_foci(self) -> List[str]:
        """获取当前注意焦点"""
        return [f.target_id for f in self.foci]
    
    def get_attention_state(self) -> Dict:
        """获取注意力状态"""
        return {
            'num_foci': len(self.foci),
            'capacity': self.capacity,
            'in_blink': self.blink.is_in_blink(),
            'blink_effectiveness': self.blink.get_effectiveness(),
            'has_context_filter': self.context_filter is not None,
            'history_length': len(self.history),
        }


# ============================================================================
# Global Workspace (全局工作空间)
# ============================================================================

class GlobalWorkspace:
    """
    全局工作空间实现
    
    基于 Baars 的 Global Workspace Theory (GWT)
    意识作为信息在全局工作空间中的广播
    """
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
        self.workspace: Dict[str, float] = {}
        self.broadcast_history: List[Tuple[str, float, datetime]] = []
        self.competitors: Dict[str, AttentionalResource] = {}
    
    def compete(
        self,
        candidates: List[AttentionalResource]
    ) -> Optional[str]:
        """
        竞争进入全局工作空间
        
        只有超过阈值的候选才能进入
        """
        if not candidates:
            return None
        
        # 找到最高分的候选
        best = max(candidates, key=lambda r: r.get_attention_score())
        
        if best.get_attention_score() >= self.threshold:
            # 进入工作空间
            self.workspace[best.target_id] = best.get_attention_score()
            self.broadcast_history.append(
                (best.target_id, best.get_attention_score(), datetime.now())
            )
            
            # 清理旧内容 (容量限制)
            if len(self.workspace) > 5:
                min_key = min(self.workspace, key=self.workspace.get)
                del self.workspace[min_key]
            
            return best.target_id
        
        return None
    
    def broadcast(self, content_id: str) -> bool:
        """广播内容到所有模块"""
        if content_id not in self.workspace:
            return False
        
        # 模拟广播 (实际应通知所有订阅模块)
        return True
    
    def get_conscious_content(self) -> List[Tuple[str, float]]:
        """获取当前意识内容"""
        items = list(self.workspace.items())
        items.sort(key=lambda x: -x[1])
        return items
