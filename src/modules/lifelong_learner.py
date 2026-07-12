"""
终身学习与自我进化系统 (Lifelong Learning & Self-Evolution System)

实现 AGI 从"预定义智者"向"成长学徒"的转变。
核心能力:
1. 动态概念图谱构建 (Dynamic Concept Graph)
2. 经验回放与记忆巩固 (Experience Replay & Consolidation)
3. 主动好奇驱动探索 (Active Curiosity-Driven Exploration)
4. 审美迭代进化 (Aesthetic Iterative Evolution)

理论基础:
- 互补学习系统理论 (Complementary Learning Systems Theory)
- 预测编码理论 (Predictive Coding Theory)
- 内在动机理论 (Intrinsic Motivation Theory)
"""

import time
import math
import random
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import deque
import heapq

# 引入现有的认知共鸣引擎
try:
    from src.modules.cognitive_resonance import (
        PhenomenologicalEngine,
        AestheticDiscriminator,
        WisdomSynthesizer,
        CulturalContextAwareness,
        CognitiveResonanceResult
    )
except ImportError:
    # 如果认知共鸣引擎不存在，使用占位类
    class PhenomenologicalEngine:
        def analyze(self, text: str) -> Dict: return {"dimensions": {}}
    
    class AestheticDiscriminator:
        def evaluate(self, content: str, content_type: str = "text") -> Dict: 
            return {"overall_score": 0.5}
    
    class WisdomSynthesizer:
        def analyze_dilemma(self, scenario: str) -> Dict: return {"recommendation": ""}
    
    class CulturalContextAwareness:
        def get_context(self, culture: str) -> Dict: return {}


@dataclass
class ConceptNode:
    """概念图谱节点"""
    concept_id: str
    label: str
    definition: str
    confidence: float = 0.5  # 置信度 0-1
    frequency: int = 1
    last_updated: float = field(default_factory=time.time)
    connections: Dict[str, float] = field(default_factory=dict)  # {connected_id: strength}
    tags: Set[str] = field(default_factory=set)
    source_examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "concept_id": self.concept_id,
            "label": self.label,
            "definition": self.definition,
            "confidence": self.confidence,
            "frequency": self.frequency,
            "connections": self.connections,
            "tags": list(self.tags),
            "example_count": len(self.source_examples)
        }


@dataclass
class ExperienceMemory:
    """经验记忆单元"""
    memory_id: str
    content: str
    context: Dict[str, Any]
    emotional_valence: float  # -1 to 1
    importance_score: float  # 0 to 1
    timestamp: float = field(default_factory=time.time)
    replay_count: int = 0
    consolidation_strength: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "memory_id": self.memory_id,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "emotional_valence": self.emotional_valence,
            "importance_score": self.importance_score,
            "replay_count": self.replay_count,
            "consolidation_strength": self.consolidation_strength
        }


@dataclass
class CuriosityQuery:
    """好奇驱动查询"""
    query_id: str
    question: str
    knowledge_gap: str
    urgency: float  # 0-1
    related_concepts: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, answered, dismissed
    answer: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "question": self.question,
            "knowledge_gap": self.knowledge_gap,
            "urgency": self.urgency,
            "related_concepts": self.related_concepts,
            "status": self.status,
            "answer": self.answer
        }
    

class DynamicConceptGraph:
    """动态概念图谱"""
    
    def __init__(self, max_nodes: int = 10000):
        self.nodes: Dict[str, ConceptNode] = {}
        self.max_nodes = max_nodes
        self.semantic_cache: Dict[str, str] = {}  # 简单语义缓存
        
    def add_or_update_concept(self, label: str, definition: str, 
                             context: Optional[Dict] = None) -> ConceptNode:
        """添加或更新概念节点"""
        concept_id = self._generate_concept_id(label)
        
        if concept_id in self.nodes:
            node = self.nodes[concept_id]
            node.frequency += 1
            node.last_updated = time.time()
            node.definition = self._merge_definitions(node.definition, definition)
            node.confidence = min(1.0, node.confidence + 0.1)
            if context and "tags" in context:
                node.tags.update(context.get("tags", []))
            if context and "example" in context:
                node.source_examples.append(context["example"])
        else:
            node = ConceptNode(
                concept_id=concept_id,
                label=label,
                definition=definition,
                tags=set(context.get("tags", [])) if context else set(),
                source_examples=[context["example"]] if context and "example" in context else []
            )
            self.nodes[concept_id] = node
            
            # 自动发现关联
            self._discover_connections(node)
        
        # 内存管理
        if len(self.nodes) > self.max_nodes:
            self._prune_low_confidence_nodes()
            
        return node
    
    def _generate_concept_id(self, label: str) -> str:
        """生成概念 ID"""
        return label.lower().replace(" ", "_").replace("-", "_")
    
    def _merge_definitions(self, existing: str, new: str) -> str:
        """合并定义（简化版）"""
        if len(new) > len(existing):
            return new
        return existing
    
    def _discover_connections(self, node: ConceptNode):
        """自动发现概念间的关联"""
        for other_id, other_node in self.nodes.items():
            if other_id == node.concept_id:
                continue
                
            # 基于标签重叠计算关联强度
            shared_tags = node.tags.intersection(other_node.tags)
            if shared_tags:
                strength = len(shared_tags) / max(len(node.tags), len(other_node.tags), 1)
                node.connections[other_id] = strength
                other_node.connections[node.concept_id] = strength
            
            # 基于定义文本相似度（简化版）
            similarity = self._text_similarity(node.definition, other_node.definition)
            if similarity > 0.3:
                existing_strength = node.connections.get(other_id, 0)
                node.connections[other_id] = max(existing_strength, similarity)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """简单文本相似度计算"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0.0
    
    def _prune_low_confidence_nodes(self):
        """剪枝低置信度节点"""
        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda x: (x[1].confidence, x[1].frequency)
        )
        # 移除最弱的 10%
        remove_count = max(1, len(self.nodes) // 10)
        for concept_id, _ in sorted_nodes[:remove_count]:
            del self.nodes[concept_id]
    
    def get_related_concepts(self, concept_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """获取相关概念"""
        if concept_id not in self.nodes:
            return []
        
        connections = self.nodes[concept_id].connections
        sorted_connections = sorted(
            connections.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_connections[:top_k]
    
    def extract_concepts_from_text(self, text: str, context: Optional[Dict] = None) -> List[ConceptNode]:
        """从文本中提取概念（简化版 NER）"""
        # 实际应用中应使用 NLP 模型
        words = text.split()
        extracted = []
        
        # 提取可能的多词概念
        for i in range(len(words)):
            for length in [1, 2, 3]:  # 1-3 词概念
                if i + length > len(words):
                    break
                phrase = " ".join(words[i:i+length])
                if len(phrase) > 3 and phrase.isalpha():  # 简单过滤
                    concept = self.add_or_update_concept(
                        label=phrase,
                        definition=f"Extracted from: {text[:100]}",
                        context=context
                    )
                    extracted.append(concept)
        
        return extracted
    
    def to_dict(self) -> Dict:
        return {
            "node_count": len(self.nodes),
            "nodes": [node.to_dict() for node in list(self.nodes.values())[:20]]  # 限制返回数量
        }


class ExperienceReplaySystem:
    """经验回放与记忆巩固系统"""
    
    def __init__(self, short_term_capacity: int = 100, 
                 long_term_capacity: int = 1000):
        self.short_term_memory: deque = deque(maxlen=short_term_capacity)
        self.long_term_memory: List[ExperienceMemory] = []
        self.long_term_capacity = long_term_capacity
        self.consolidation_threshold = 0.7
        
    def add_experience(self, content: str, context: Dict, 
                      emotional_valence: float = 0.0) -> ExperienceMemory:
        """添加新经验"""
        memory = ExperienceMemory(
            memory_id=f"mem_{int(time.time() * 1000)}",
            content=content,
            context=context,
            emotional_valence=emotional_valence,
            importance_score=self._calculate_importance(emotional_valence, context)
        )
        self.short_term_memory.append(memory)
        return memory
    
    def _calculate_importance(self, emotional_valence: float, context: Dict) -> float:
        """计算经验重要性"""
        # 情绪强烈 + 新颖性高 = 重要性高
        emotion_weight = abs(emotional_valence)
        novelty = context.get("novelty", 0.5)
        return min(1.0, 0.4 * emotion_weight + 0.6 * novelty)
    
    def consolidate_memories(self, batch_size: int = 10) -> List[ExperienceMemory]:
        """巩固短期记忆到长期记忆（模拟睡眠过程）"""
        consolidated = []
        
        # 按重要性排序
        memories = sorted(
            self.short_term_memory,
            key=lambda m: m.importance_score,
            reverse=True
        )
        
        for memory in memories[:batch_size]:
            if memory.importance_score >= self.consolidation_threshold:
                memory.consolidation_strength = min(1.0, memory.consolidation_strength + 0.2)
                memory.replay_count += 1
                
                if memory.consolidation_strength >= 0.8:
                    # 转移到长期记忆
                    self.long_term_memory.append(memory)
                    consolidated.append(memory)
                    
                    if len(self.long_term_memory) > self.long_term_capacity:
                        self._prune_long_term_memory()
        
        return consolidated
    
    def _prune_long_term_memory(self):
        """剪枝长期记忆"""
        # 保留最重要的 80%
        self.long_term_memory.sort(key=lambda m: m.consolidation_strength, reverse=True)
        keep_count = int(self.long_term_capacity * 0.8)
        self.long_term_memory = self.long_term_memory[:keep_count]
    
    def replay_for_learning(self, sample_size: int = 5) -> List[ExperienceMemory]:
        """随机采样经验用于学习（防止灾难性遗忘）"""
        if not self.long_term_memory:
            return []
        
        # 优先回放近期和高重要性记忆
        weights = [m.importance_score for m in self.long_term_memory]
        total_weight = sum(weights)
        if total_weight == 0:
            return random.sample(self.long_term_memory, min(sample_size, len(self.long_term_memory)))
        
        # 加权采样
        selected = []
        for _ in range(sample_size):
            r = random.random() * total_weight
            cumulative = 0
            for memory in self.long_term_memory:
                cumulative += memory.importance_score
                if r <= cumulative:
                    selected.append(memory)
                    break
        
        return selected
    
    def get_memory_stats(self) -> Dict:
        return {
            "short_term_count": len(self.short_term_memory),
            "long_term_count": len(self.long_term_memory),
            "avg_consolidation": sum(m.consolidation_strength for m in self.long_term_memory) / max(1, len(self.long_term_memory))
        }


class ActiveCuriosityEngine:
    """主动好奇驱动引擎"""
    
    def __init__(self, curiosity_threshold: float = 0.3):
        self.curiosity_threshold = curiosity_threshold
        self.pending_queries: List[CuriosityQuery] = []
        self.knowledge_gaps: Dict[str, float] = {}  # {topic: uncertainty}
        
    def detect_knowledge_gap(self, input_text: str, 
                            confidence: float, 
                            context: Optional[Dict] = None) -> Optional[CuriosityQuery]:
        """检测知识盲区"""
        if confidence >= 1.0 - self.curiosity_threshold:
            return None
        
        urgency = 1.0 - confidence
        gap_description = self._identify_gap(input_text, context)
        
        query = CuriosityQuery(
            query_id=f"query_{int(time.time() * 1000)}",
            question=self._generate_question(gap_description),
            knowledge_gap=gap_description,
            urgency=urgency,
            related_concepts=context.get("concepts", []) if context else []
        )
        
        self.pending_queries.append(query)
        self.knowledge_gaps[gap_description] = urgency
        
        return query
    
    def _identify_gap(self, text: str, context: Optional[Dict]) -> str:
        """识别具体知识缺口"""
        # 简化实现：提取不熟悉的术语
        words = text.split()
        unfamiliar = [w for w in words if len(w) > 5 and w.isalpha()]
        if unfamiliar:
            return f"Understanding of: {', '.join(unfamiliar[:3])}"
        return "General conceptual uncertainty"
    
    def _generate_question(self, gap: str) -> str:
        """生成探索性问题"""
        templates = [
            f"Could you explain more about {gap}?",
            f"What is the relationship between {gap} and known concepts?",
            f"How does {gap} fit into the broader context?",
            f"Can you provide examples of {gap}?"
        ]
        return random.choice(templates)
    
    def answer_query(self, query_id: str, answer: str) -> bool:
        """回答好奇查询"""
        for query in self.pending_queries:
            if query.query_id == query_id:
                query.answer = answer
                query.status = "answered"
                
                # 降低对应知识缺口的不确定性
                if query.knowledge_gap in self.knowledge_gaps:
                    self.knowledge_gaps[query.knowledge_gap] *= 0.5
                
                return True
        return False
    
    def get_most_urgent_query(self) -> Optional[CuriosityQuery]:
        """获取最紧急的查询"""
        if not self.pending_queries:
            return None
        
        pending = [q for q in self.pending_queries if q.status == "pending"]
        if not pending:
            return None
        
        return max(pending, key=lambda q: q.urgency)
    
    def get_curiosity_stats(self) -> Dict:
        pending_count = len([q for q in self.pending_queries if q.status == "pending"])
        return {
            "total_queries": len(self.pending_queries),
            "pending_queries": pending_count,
            "answered_queries": len(self.pending_queries) - pending_count,
            "knowledge_gaps": len(self.knowledge_gaps),
            "avg_urgency": sum(q.urgency for q in self.pending_queries) / max(1, len(self.pending_queries))
        }


class AestheticEvolutionModule:
    """审美迭代进化模块"""
    
    def __init__(self, discriminator: Optional[AestheticDiscriminator] = None):
        self.discriminator = discriminator or AestheticDiscriminator()
        self.feedback_history: List[Dict] = []
        self.aesthetic_parameters: Dict[str, float] = {
            "complexity_weight": 0.3,
            "symmetry_weight": 0.3,
            "novelty_weight": 0.2,
            "harmony_weight": 0.2
        }
        self.cultural_bias: Dict[str, float] = {}
        
    def receive_feedback(self, content: str, evaluation: Dict, 
                        user_feedback: float, cultural_context: str = "western"):
        """接收用户反馈以调整审美参数"""
        feedback_entry = {
            "content": content,
            "initial_evaluation": evaluation,
            "user_feedback": user_feedback,  # -1 to 1
            "cultural_context": cultural_context,
            "timestamp": time.time()
        }
        self.feedback_history.append(feedback_entry)
        
        # 根据反馈调整参数
        self._update_parameters(user_feedback, evaluation, cultural_context)
    
    def _update_parameters(self, user_feedback: float, evaluation: Dict, culture: str):
        """根据反馈更新审美参数"""
        if len(self.feedback_history) < 5:
            return  # 需要足够样本
        
        # 计算差异
        predicted_score = evaluation.get("overall_score", 0.5)
        actual_score = (user_feedback + 1) / 2  # 转换到 0-1
        
        error = actual_score - predicted_score
        learning_rate = 0.05
        
        # 调整权重
        if abs(error) > 0.1:
            if "complexity" in evaluation:
                direction = 1 if error > 0 else -1
                self.aesthetic_parameters["complexity_weight"] += direction * learning_rate
            
            if "symmetry" in evaluation:
                direction = 1 if error > 0 else -1
                self.aesthetic_parameters["symmetry_weight"] += direction * learning_rate
        
        # 文化特定调整
        if culture not in self.cultural_bias:
            self.cultural_bias[culture] = 0.0
        self.cultural_bias[culture] += error * learning_rate
        
        # 归一化权重
        total = sum(self.aesthetic_parameters.values())
        if total > 0:
            for key in self.aesthetic_parameters:
                self.aesthetic_parameters[key] /= total
    
    def evaluate_with_evolved_aesthetics(self, content: str, 
                                        content_type: str = "text",
                                        cultural_context: str = "western") -> Dict:
        """使用进化后的审美观进行评估"""
        base_evaluation = self.discriminator.evaluate(content, content_type)
        
        # 应用文化偏差
        cultural_adjustment = self.cultural_bias.get(cultural_context, 0.0)
        
        # 重新计算综合评分
        adjusted_score = (
            base_evaluation.get("complexity", 0.5) * self.aesthetic_parameters["complexity_weight"] +
            base_evaluation.get("symmetry", 0.5) * self.aesthetic_parameters["symmetry_weight"] +
            base_evaluation.get("novelty", 0.5) * self.aesthetic_parameters["novelty_weight"] +
            base_evaluation.get("harmony", 0.5) * self.aesthetic_parameters["harmony_weight"] +
            cultural_adjustment
        )
        
        base_evaluation["overall_score"] = max(0, min(1, adjusted_score))
        base_evaluation["evolved"] = True
        base_evaluation["parameters_used"] = self.aesthetic_parameters.copy()
        
        return base_evaluation
    
    def get_evolution_stats(self) -> Dict:
        return {
            "feedback_count": len(self.feedback_history),
            "current_parameters": self.aesthetic_parameters,
            "cultural_biases": self.cultural_bias,
            "avg_feedback": sum(f["user_feedback"] for f in self.feedback_history) / max(1, len(self.feedback_history))
        }


class LifelongLearner:
    """终身学习者主类"""
    
    def __init__(self, enable_cognitive_resonance: bool = True):
        self.concept_graph = DynamicConceptGraph()
        self.memory_system = ExperienceReplaySystem()
        self.curiosity_engine = ActiveCuriosityEngine()
        self.aesthetic_module = AestheticEvolutionModule()
        
        if enable_cognitive_resonance:
            try:
                self.phenomenology = PhenomenologicalEngine()
                self.aesthetic_discriminator = AestheticDiscriminator()
                self.wisdom_synthesizer = WisdomSynthesizer()
                self.cultural_context = CulturalContextAwareness()
            except:
                self.phenomenology = None
                self.aesthetic_discriminator = None
                self.wisdom_synthesizer = None
                self.cultural_context = None
        else:
            self.phenomenology = None
            self.aesthetic_discriminator = None
            self.wisdom_synthesizer = None
            self.cultural_context = None
        
        self.interaction_count = 0
        self.learning_rate = 0.1
        
    def process_input(self, text: str, context: Optional[Dict] = None,
                     user_feedback: Optional[float] = None) -> Dict:
        """处理输入并学习"""
        self.interaction_count += 1
        
        # 1. 提取概念
        extracted_concepts = self.concept_graph.extract_concepts_from_text(
            text, 
            context={"tags": context.get("tags", []) if context else [], "example": text}
        )
        
        # 2. 情感分析
        emotional_valence = 0.0
        if self.phenomenology:
            qualia = self.phenomenology.analyze(text)
            dimensions = qualia.get("dimensions", {})
            emotional_valence = dimensions.get("valence", 0.0)
        
        # 3. 添加到记忆
        memory = self.memory_system.add_experience(
            text,
            context=context or {},
            emotional_valence=emotional_valence
        )
        
        # 4. 检测知识缺口
        confidence = self._estimate_confidence(text, context)
        curiosity_query = self.curiosity_engine.detect_knowledge_gap(
            text, confidence, 
            context={"concepts": [c.label for c in extracted_concepts]}
        )
        
        # 5. 如果有反馈，更新审美
        if user_feedback is not None and self.aesthetic_discriminator:
            evaluation = self.aesthetic_discriminator.evaluate(text)
            culture = context.get("culture", "western") if context else "western"
            self.aesthetic_module.receive_feedback(text, evaluation, user_feedback, culture)
        
        # 6. 定期巩固记忆
        if self.interaction_count % 10 == 0:
            self.consolidate()
        
        result = {
            "concepts_extracted": len(extracted_concepts),
            "emotional_valence": emotional_valence,
            "memory_importance": memory.importance_score,
            "curiosity_triggered": curiosity_query is not None,
            "curiosity_query": curiosity_query.to_dict() if curiosity_query else None,
            "confidence_estimate": confidence
        }
        
        if curiosity_query:
            result["suggested_question"] = curiosity_query.question
        
        return result
    
    def _estimate_confidence(self, text: str, context: Optional[Dict]) -> float:
        """估计对输入的理解置信度"""
        # 简化实现：基于已知概念覆盖率
        words = set(text.lower().split())
        known_words = set()
        
        for node in self.concept_graph.nodes.values():
            known_words.update(node.label.lower().split())
            known_words.update(node.tags)
        
        if not words:
            return 0.5
        
        overlap = words.intersection(known_words)
        coverage = len(overlap) / len(words)
        
        # 基础置信度 + 覆盖度调整
        return min(0.9, 0.5 + 0.4 * coverage)
    
    def consolidate(self) -> Dict:
        """执行记忆巩固"""
        consolidated = self.memory_system.consolidate_memories()
        replay_samples = self.memory_system.replay_for_learning()
        
        return {
            "consolidated_count": len(consolidated),
            "replay_samples": len(replay_samples),
            "memory_stats": self.memory_system.get_memory_stats()
        }
    
    def answer_curiosity(self, query_id: str, answer: str) -> bool:
        """回答好奇心查询"""
        success = self.curiosity_engine.answer_query(query_id, answer)
        
        if success:
            # 将答案作为新知识学习
            self.process_input(answer, {"source": "curiosity_answer"})
        
        return success
    
    def get_learning_state(self) -> Dict:
        """获取当前学习状态"""
        return {
            "interaction_count": self.interaction_count,
            "concept_graph": self.concept_graph.to_dict(),
            "memory_stats": self.memory_system.get_memory_stats(),
            "curiosity_stats": self.curiosity_engine.get_curiosity_stats(),
            "aesthetic_evolution": self.aesthetic_module.get_evolution_stats()
        }
    
    def evolve_aesthetic(self, content: str, user_rating: float, 
                        culture: str = "western") -> Dict:
        """显式进化审美"""
        evaluation = self.aesthetic_discriminator.evaluate(content) if self.aesthetic_discriminator else {}
        self.aesthetic_module.receive_feedback(content, evaluation, user_rating, culture)
        
        return {
            "updated_parameters": self.aesthetic_module.aesthetic_parameters,
            "cultural_bias": self.aesthetic_module.cultural_bias.get(culture, 0.0)
        }


# 全局实例
_lifelong_learner_instance: Optional[LifelongLearner] = None


def get_lifelong_learner(enable_cognitive_resonance: bool = True) -> LifelongLearner:
    """获取终身学习者实例"""
    global _lifelong_learner_instance
    if _lifelong_learner_instance is None:
        _lifelong_learner_instance = LifelongLearner(enable_cognitive_resonance)
    return _lifelong_learner_instance


def reset_lifelong_learner():
    """重置终身学习者实例"""
    global _lifelong_learner_instance
    _lifelong_learner_instance = None
