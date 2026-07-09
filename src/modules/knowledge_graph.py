"""
Knowledge Graph Module v2.0
============================
第二阶段核心模块：实现真正的学习能力和知识图谱

核心特性：
1. 知识图谱构建：基于 UCR 层的符号节点构建关系图谱
2. 混合检索：结合图谱遍历和向量相似性搜索
3. 元学习机制：从成功/失败中学习策略调整
4. 假设生成与验证：主动推理能力
5. 知识融合：合并相似概念，消除冗余

Author: AI Assistant
Goal: 创造真正通用智慧认知引擎
"""

import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from collections import defaultdict, deque
import math

# Import UCR components
try:
    from ucr_layer import (
        CognitiveUnit, SymbolicNode, VectorEmbedding,
        EntityType, UnifiedRepresentationEngine, represent
    )
except ImportError:
    # Fallback for standalone testing
    class EntityType:
        CONCEPT = "concept"
        ACTION = "action"
        RELATION = "relation"
    
    class SymbolicNode:
        def __init__(self, id, entity_type, label, definition, relations=None):
            self.id = id
            self.entity_type = entity_type
            self.label = label
            self.definition = definition
            self.relations = relations or []

logger = logging.getLogger(__name__)


class RelationType(Enum):
    """关系类型枚举"""
    IS_A = "is_a"                    # 继承/分类关系
    PART_OF = "part_of"              # 组成关系
    CAUSES = "causes"                # 因果关系
    ENABLES = "enables"              # 使能关系
    CONSTRAINTS = "constraints"      # 约束关系
    SIMILAR_TO = "similar_to"        # 相似关系
    CONTRADICTS = "contradicts"      # 矛盾关系
    SUPPORTS = "supports"            # 支持关系
    DERIVED_FROM = "derived_from"    # 派生关系
    USED_IN = "used_in"              # 使用场景
    HYPOTHESIS_FOR = "hypothesis_for"  # 假设关系
    EVIDENCE_FOR = "evidence_for"    # 证据关系


@dataclass
class KnowledgeEdge:
    """知识图谱的边"""
    source_id: str
    target_id: str
    relation_type: RelationType
    weight: float = 1.0
    confidence: float = 0.8
    evidence: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_verified: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type.value,
            'weight': self.weight,
            'confidence': self.confidence,
            'evidence': self.evidence,
            'created_at': self.created_at,
            'last_verified': self.last_verified
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'KnowledgeEdge':
        data['relation_type'] = RelationType(data['relation_type'])
        return cls(**data)


@dataclass
class LearningStrategy:
    """学习策略：元学习的核心"""
    id: str
    name: str
    description: str
    domain: str
    success_count: int = 0
    failure_count: int = 0
    applicable_patterns: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.5
        return self.success_count / total
    
    def reinforce(self, success: bool):
        """强化学习策略"""
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LearningStrategy':
        return cls(**data)


@dataclass
class Hypothesis:
    """假设：主动推理的核心"""
    id: str
    description: str
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    confidence: float = 0.5
    status: str = "pending"  # pending, verified, refuted
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tested_count: int = 0
    
    def update_confidence(self, positive: bool, strength: float = 0.1):
        """更新假设置信度"""
        if positive:
            self.confidence = min(1.0, self.confidence + strength)
            if positive and self.confidence > 0.9:
                self.status = "verified"
        else:
            self.confidence = max(0.0, self.confidence - strength)
            if self.confidence < 0.2:
                self.status = "refuted"
        self.tested_count += 1
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Hypothesis':
        return cls(**data)


class KnowledgeGraph:
    """
    知识图谱：存储和管理概念之间的关系
    
    特点：
    1. 基于 UCR 的认知单元作为节点
    2. 支持多种关系类型
    3. 带权重的边，支持置信度传播
    """
    
    def __init__(self):
        self.nodes: Dict[str, CognitiveUnit] = {}
        self.edges: Dict[str, List[KnowledgeEdge]] = defaultdict(list)
        self.reverse_edges: Dict[str, List[KnowledgeEdge]] = defaultdict(list)
        self.edge_index: Dict[str, KnowledgeEdge] = {}
        
    def add_node(self, unit: CognitiveUnit):
        """添加认知单元节点"""
        self.nodes[unit.id] = unit
        logger.debug(f"Added node: {unit.id}")
    
    def get_node(self, node_id: str) -> Optional[CognitiveUnit]:
        """获取节点"""
        return self.nodes.get(node_id)
    
    def add_edge(self, source_id: str, target_id: str, 
                 relation_type: RelationType, 
                 weight: float = 1.0,
                 confidence: float = 0.8,
                 evidence: Optional[List[str]] = None) -> KnowledgeEdge:
        """添加边"""
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.warning(f"Cannot add edge: nodes not found ({source_id} -> {target_id})")
            return None
        
        edge = KnowledgeEdge(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            weight=weight,
            confidence=confidence,
            evidence=evidence or []
        )
        
        edge_key = f"{source_id}_{target_id}_{relation_type.value}"
        self.edges[source_id].append(edge)
        self.reverse_edges[target_id].append(edge)
        self.edge_index[edge_key] = edge
        
        # 同步更新认知单元中的关系
        if source_id in self.nodes:
            self.nodes[source_id].symbolic.relations.append((relation_type.value, target_id))
        
        logger.debug(f"Added edge: {source_id} -[{relation_type.value}]-> {target_id}")
        return edge
    
    def get_neighbors(self, node_id: str, 
                      relation_types: Optional[List[RelationType]] = None,
                      direction: str = "outgoing") -> List[Tuple[CognitiveUnit, KnowledgeEdge]]:
        """获取邻居节点"""
        neighbors = []
        
        if direction == "outgoing":
            edges = self.edges.get(node_id, [])
        elif direction == "incoming":
            edges = self.reverse_edges.get(node_id, [])
        else:
            edges = self.edges.get(node_id, []) + self.reverse_edges.get(node_id, [])
        
        for edge in edges:
            if relation_types and edge.relation_type not in relation_types:
                continue
            
            target_id = edge.target_id if direction == "outgoing" else edge.source_id
            if target_id in self.nodes:
                neighbors.append((self.nodes[target_id], edge))
        
        return neighbors
    
    def find_path(self, start_id: str, end_id: str, 
                  max_depth: int = 5) -> List[List[Tuple[str, RelationType, str]]]:
        """查找两个节点之间的所有路径（BFS）"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        
        paths = []
        queue = deque([(start_id, [])])
        visited = set()
        
        while queue:
            current_id, path = queue.popleft()
            
            if current_id == end_id and path:
                paths.append(path)
                continue
            
            if current_id in visited or len(path) >= max_depth:
                continue
            
            visited.add(current_id)
            
            for edge in self.edges.get(current_id, []):
                new_path = path + [(current_id, edge.relation_type, edge.target_id)]
                queue.append((edge.target_id, new_path))
        
        return paths
    
    def get_subgraph(self, center_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """获取以某节点为中心的子图"""
        if center_id not in self.nodes:
            return {"nodes": {}, "edges": []}
        
        visited = {center_id}
        nodes_to_include = {center_id}
        edges_to_include = []
        
        queue = deque([(center_id, 0)])
        
        while queue:
            current_id, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
            
            for edge in self.edges.get(current_id, []) + self.reverse_edges.get(current_id, []):
                edges_to_include.append(edge.to_dict())
                
                neighbor_id = edge.target_id if edge.source_id == current_id else edge.source_id
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    nodes_to_include.add(neighbor_id)
                    queue.append((neighbor_id, depth + 1))
        
        subgraph_nodes = {
            nid: self.nodes[nid].to_dict() 
            for nid in nodes_to_include if nid in self.nodes
        }
        
        return {"nodes": subgraph_nodes, "edges": edges_to_include}
    
    def export_to_dict(self) -> Dict:
        """导出图谱"""
        return {
            'nodes': {nid: unit.to_dict() for nid, unit in self.nodes.items()},
            'edges': [edge.to_dict() for edges in self.edges.values() for edge in edges],
            'metadata': {
                'node_count': len(self.nodes),
                'edge_count': sum(len(e) for e in self.edges.values()),
                'exported_at': datetime.now().isoformat()
            }
        }
    
    def import_from_dict(self, data: Dict):
        """导入图谱"""
        # 先导入节点
        for nid, node_data in data.get('nodes', {}).items():
            unit = CognitiveUnit.from_dict(node_data)
            self.nodes[nid] = unit
        
        # 再导入边
        for edge_data in data.get('edges', []):
            edge = KnowledgeEdge.from_dict(edge_data)
            self.edges[edge.source_id].append(edge)
            self.reverse_edges[edge.target_id].append(edge)
            edge_key = f"{edge.source_id}_{edge.target_id}_{edge.relation_type.value}"
            self.edge_index[edge_key] = edge
        
        logger.info(f"Imported graph with {len(self.nodes)} nodes and {len(self.edge_index)} edges")


class HybridRetriever:
    """
    混合检索器：结合图谱遍历和向量相似性
    
    优势：
    1. 精确查询：通过图谱关系找到确切相关概念
    2. 模糊匹配：通过向量相似性找到语义相关概念
    3. 排序融合：综合两种信号进行排序
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph, ucr_engine: UnifiedRepresentationEngine):
        self.graph = knowledge_graph
        self.ucr = ucr_engine
    
    def retrieve(self, query: str, 
                 top_k: int = 10,
                 use_graph: bool = True,
                 use_vector: bool = True,
                 alpha: float = 0.5) -> List[Tuple[CognitiveUnit, float]]:
        """
        混合检索
        
        Args:
            query: 查询文本
            top_k: 返回数量
            use_graph: 是否使用图谱检索
            use_vector: 是否使用向量检索
            alpha: 图谱权重 (0-1)，1-alpha 为向量权重
        
        Returns:
            List of (CognitiveUnit, combined_score)
        """
        scores: Dict[str, float] = defaultdict(float)
        
        # 1. 图谱检索
        if use_graph:
            graph_results = self._graph_retrieve(query, top_k * 2)
            for unit, score in graph_results:
                scores[unit.id] += alpha * score
        
        # 2. 向量检索
        if use_vector:
            vector_results = self.ucr.search_by_similarity(query, threshold=0.0, limit=top_k * 2)
            for unit, score in vector_results:
                scores[unit.id] += (1 - alpha) * score
        
        # 3. 排序
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 4. 返回 top_k
        results = []
        for unit_id, score in sorted_results[:top_k]:
            if unit_id in self.graph.nodes:
                results.append((self.graph.nodes[unit_id], score))
        
        return results
    
    def _graph_retrieve(self, query: str, limit: int) -> List[Tuple[CognitiveUnit, float]]:
        """图谱检索：基于关键词匹配节点标签和定义"""
        query_lower = query.lower()
        results = []
        
        for unit in self.graph.nodes.values():
            score = 0.0
            
            # 匹配标签
            if query_lower in unit.symbolic.label.lower():
                score += 0.5
            
            # 匹配定义
            if query_lower in unit.symbolic.definition.lower():
                score += 0.3
            
            # 匹配属性
            for attr_value in unit.symbolic.attributes.values():
                if isinstance(attr_value, str) and query_lower in attr_value.lower():
                    score += 0.2
            
            if score > 0:
                results.append((unit, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]


class MetaLearner:
    """
    元学习器：学习如何学习
    
    功能：
    1. 跟踪不同学习策略的效果
    2. 根据情境选择最优策略
    3. 自动生成和验证假设
    4. 知识融合：识别并合并重复概念
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.graph = knowledge_graph
        self.strategies: Dict[str, LearningStrategy] = {}
        self.hypotheses: Dict[str, Hypothesis] = {}
        self._initialize_default_strategies()
    
    def _initialize_default_strategies(self):
        """初始化默认学习策略"""
        default_strategies = [
            LearningStrategy(
                id="strategy_pattern_matching",
                name="Pattern Matching",
                description="Learn by identifying recurring patterns in problems",
                domain="general",
                applicable_patterns=["recurring_error", "similar_structure"]
            ),
            LearningStrategy(
                id="strategy_first_principles",
                name="First Principles",
                description="Break down problems to fundamental truths",
                domain="reasoning",
                applicable_patterns=["complex_problem", "novel_situation"]
            ),
            LearningStrategy(
                id="strategy_analogical",
                name="Analogical Reasoning",
                description="Transfer knowledge from similar domains",
                domain="transfer",
                applicable_patterns=["cross_domain", "structural_similarity"]
            ),
            LearningStrategy(
                id="strategy_experimental",
                name="Experimental Learning",
                description="Learn through hypothesis testing and experimentation",
                domain="discovery",
                applicable_patterns=["unknown_territory", "multiple_hypotheses"]
            )
        ]
        
        for strategy in default_strategies:
            self.strategies[strategy.id] = strategy
    
    def select_strategy(self, problem_description: str, 
                        domain: str,
                        context: Optional[Dict] = None) -> LearningStrategy:
        """根据问题选择最优学习策略"""
        # 简单实现：基于领域匹配
        best_strategy = None
        best_score = -1
        
        for strategy in self.strategies.values():
            score = 0.0
            
            # 领域匹配
            if strategy.domain == domain:
                score += 0.5
            
            # 模式匹配
            if context:
                for pattern in context.get('patterns', []):
                    if pattern in strategy.applicable_patterns:
                        score += 0.3
            
            # 历史成功率
            score += 0.2 * strategy.success_rate
            
            if score > best_score:
                best_score = score
                best_strategy = strategy
        
        return best_strategy or list(self.strategies.values())[0]
    
    def reinforce_strategy(self, strategy_id: str, success: bool):
        """强化学习策略"""
        if strategy_id in self.strategies:
            self.strategies[strategy_id].reinforce(success)
            logger.info(f"Strategy {strategy_id} reinforced: {'success' if success else 'failure'}")
    
    def generate_hypothesis(self, observation: str, 
                           related_concepts: List[str]) -> Hypothesis:
        """基于观察生成假设"""
        hypothesis_id = f"hyp_{hashlib.md5(observation.encode()).hexdigest()[:12]}"
        
        hypothesis = Hypothesis(
            id=hypothesis_id,
            description=observation,
            supporting_evidence=related_concepts[:3] if related_concepts else []
        )
        
        self.hypotheses[hypothesis_id] = hypothesis
        logger.info(f"Generated hypothesis: {hypothesis_id}")
        return hypothesis
    
    def test_hypothesis(self, hypothesis_id: str, 
                       evidence: str, 
                       supports: bool) -> Hypothesis:
        """测试假设"""
        if hypothesis_id not in self.hypotheses:
            return None
        
        hypothesis = self.hypotheses[hypothesis_id]
        
        if supports:
            hypothesis.supporting_evidence.append(evidence)
        else:
            hypothesis.contradicting_evidence.append(evidence)
        
        hypothesis.update_confidence(supports)
        
        logger.info(f"Tested hypothesis {hypothesis_id}: {'supported' if supports else 'contradicted'}")
        return hypothesis
    
    def merge_similar_concepts(self, threshold: float = 0.9) -> List[Tuple[str, str]]:
        """合并相似概念"""
        merged_pairs = []
        node_ids = list(self.graph.nodes.keys())
        
        for i, id1 in enumerate(node_ids):
            for id2 in node_ids[i+1:]:
                unit1 = self.graph.nodes[id1]
                unit2 = self.graph.nodes[id2]
                
                # 检查向量相似性
                if unit1.vector and unit2.vector:
                    similarity = unit1.vector.similarity(unit2.vector)
                    
                    if similarity >= threshold:
                        # 合并：保留第一个，删除第二个
                        merged_pairs.append((id1, id2))
                        logger.info(f"Merged similar concepts: {id2} -> {id1} (similarity: {similarity:.3f})")
        
        return merged_pairs
    
    def get_strategy_stats(self) -> Dict[str, Any]:
        """获取策略统计"""
        return {
            sid: {
                'name': s.name,
                'success_rate': s.success_rate,
                'success_count': s.success_count,
                'failure_count': s.failure_count
            }
            for sid, s in self.strategies.items()
        }


class EnhancedMemoryBank:
    """
    增强记忆银行：整合知识图谱和向量检索
    
    相比第一阶段的改进：
    1. 使用知识图谱存储关系
    2. 支持混合检索
    3. 集成元学习能力
    """
    
    def __init__(self, storage_path: str = "memory_bank.json",
                 graph_storage_path: str = "knowledge_graph.json"):
        self.storage_path = storage_path
        self.graph_storage_path = graph_storage_path
        
        # 初始化 UCR 引擎
        self.ucr_engine = UnifiedRepresentationEngine()
        
        # 初始化知识图谱
        self.knowledge_graph = KnowledgeGraph()
        
        # 初始化混合检索器
        self.retriever = HybridRetriever(self.knowledge_graph, self.ucr_engine)
        
        # 初始化元学习器
        self.meta_learner = MetaLearner(self.knowledge_graph)
        
        # 加载持久化数据
        self._load()
    
    def _load(self):
        """加载记忆和图谱"""
        # 加载传统记忆银行（向后兼容）
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} knowledge nodes from memory bank")
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No existing memory bank found. Starting fresh.")
        
        # 加载知识图谱
        try:
            with open(self.graph_storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.knowledge_graph.import_from_dict(data)
                logger.info(f"Loaded knowledge graph with {len(self.knowledge_graph.nodes)} nodes")
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No existing knowledge graph found. Starting fresh.")
    
    def save(self):
        """保存记忆和图谱"""
        # 保存知识图谱
        with open(self.graph_storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_graph.export_to_dict(), f, indent=2)
        logger.debug("Knowledge graph saved.")
    
    def add_knowledge(self, content: Any, 
                     content_type: str = "text",
                     domain: str = "general",
                     tags: Optional[Set[str]] = None,
                     relations: Optional[List[Tuple[str, RelationType, str]]] = None) -> CognitiveUnit:
        """
        添加知识到记忆银行
        
        Args:
            content: 知识内容
            content_type: 内容类型 ('code', 'text', 'data')
            domain: 领域标签
            tags: 附加标签
            relations: 与其他知识的关系列表 [(target_id, relation_type, evidence)]
        
        Returns:
            CognitiveUnit: 创建的认知单元
        """
        # 1. 创建认知单元
        unit = self.ucr_engine.create_unit(
            content, 
            content_type=content_type,
            domain=domain,
            tags=tags
        )
        
        # 2. 添加到知识图谱
        self.knowledge_graph.add_node(unit)
        
        # 3. 建立关系
        if relations:
            for target_id, relation_type, evidence in relations:
                if target_id in self.knowledge_graph.nodes:
                    self.knowledge_graph.add_edge(
                        unit.id, target_id, relation_type,
                        evidence=[evidence] if isinstance(evidence, str) else evidence
                    )
        
        # 4. 自动发现相似概念并建立关系
        similar_units = self.ucr_engine.search_by_similarity(
            unit.symbolic.definition, 
            threshold=0.3, 
            limit=5
        )
        for similar_unit, score in similar_units:
            if similar_unit.id != unit.id and similar_unit.id in self.knowledge_graph.nodes:
                relation_type = RelationType.SIMILAR_TO
                self.knowledge_graph.add_edge(
                    unit.id, similar_unit.id, relation_type,
                    weight=score,
                    evidence=[f"Vector similarity: {score:.3f}"]
                )
        
        # 5. 保存
        self.save()
        
        logger.info(f"Added knowledge: {unit.id} in domain {domain}")
        return unit
    
    def retrieve(self, query: str, 
                top_k: int = 5,
                use_mixed_retrieval: bool = True,
                domain_filter: Optional[str] = None) -> List[Tuple[CognitiveUnit, float]]:
        """
        检索知识
        
        Args:
            query: 查询文本
            top_k: 返回数量
            use_mixed_retrieval: 是否使用混合检索
            domain_filter: 领域过滤
        
        Returns:
            List of (CognitiveUnit, score)
        """
        if use_mixed_retrieval:
            results = self.retriever.retrieve(query, top_k=top_k * 2)
        else:
            # 仅向量检索
            vector_results = self.ucr_engine.search_by_similarity(query, limit=top_k * 2)
            results = [(unit, score) for unit, score in vector_results]
        
        # 领域过滤
        if domain_filter:
            results = [
                (unit, score) for unit, score in results
                if domain_filter in unit.tags
            ]
        
        return results[:top_k]
    
    def learn_from_interaction(self, problem: str, 
                               solution: str,
                               success: bool,
                               domain: str = "general") -> Dict[str, Any]:
        """
        从交互中学习
        
        Args:
            problem: 问题描述
            solution: 解决方案
            success: 是否成功
            domain: 领域
        
        Returns:
            学习摘要
        """
        # 1. 添加问题和解决方案到知识库
        problem_unit = self.add_knowledge(
            problem, 
            content_type='text',
            domain=domain,
            tags={'problem', domain}
        )
        
        solution_unit = self.add_knowledge(
            solution,
            content_type='text',
            domain=domain,
            tags={'solution', domain}
        )
        
        # 2. 建立问题 - 解决方案关系
        relation_type = RelationType.SUPPORTS if success else RelationType.CONTRADICTS
        self.knowledge_graph.add_edge(
            problem_unit.id,
            solution_unit.id,
            relation_type,
            confidence=0.9 if success else 0.5,
            evidence=["Interaction outcome"]
        )
        
        # 3. 选择并强化学习策略
        strategy = self.meta_learner.select_strategy(problem, domain)
        self.meta_learner.reinforce_strategy(strategy.id, success)
        
        # 4. 生成假设（如果是新领域或失败情况）
        if not success or domain not in ['coding', 'logic']:
            hypothesis = self.meta_learner.generate_hypothesis(
                f"Solution approach may need adjustment for {domain}",
                [problem_unit.id, solution_unit.id]
            )
        
        # 5. 定期合并相似概念
        merged = self.meta_learner.merge_similar_concepts(threshold=0.95)
        
        learning_summary = {
            'problem_id': problem_unit.id,
            'solution_id': solution_unit.id,
            'strategy_used': strategy.id,
            'strategy_success_rate': strategy.success_rate,
            'hypothesis_generated': hypothesis.id if not success else None,
            'concepts_merged': len(merged),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Learning complete: {learning_summary}")
        return learning_summary
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识统计"""
        return {
            'total_units': len(self.knowledge_graph.nodes),
            'total_edges': len(self.knowledge_graph.edge_index),
            'entity_types': {
                et.value: len(self.ucr_engine.index_by_type.get(et, set()))
                for et in EntityType
            },
            'strategy_stats': self.meta_learner.get_strategy_stats(),
            'active_hypotheses': len([
                h for h in self.meta_learner.hypotheses.values()
                if h.status == 'pending'
            ])
        }


# 便捷函数
_default_memory: Optional[EnhancedMemoryBank] = None


def get_memory_bank() -> EnhancedMemoryBank:
    """获取或创建默认记忆银行"""
    global _default_memory
    if _default_memory is None:
        _default_memory = EnhancedMemoryBank()
    return _default_memory


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=== Testing Enhanced Memory Bank v2.0 ===\n")
    
    # 创建记忆银行
    memory = EnhancedMemoryBank()
    
    # 测试 1: 添加知识
    print("--- Test 1: Adding Knowledge ---")
    unit1 = memory.add_knowledge(
        "A function is a reusable block of code that performs a specific task",
        content_type='text',
        domain='programming',
        tags={'fundamental', 'function'}
    )
    print(f"Added: {unit1.id} - {unit1.symbolic.label}")
    
    unit2 = memory.add_knowledge(
        "A class is a blueprint for creating objects with attributes and methods",
        content_type='text',
        domain='programming',
        tags={'fundamental', 'class'}
    )
    print(f"Added: {unit2.id} - {unit2.symbolic.label}")
    
    # 测试 2: 建立关系
    print("\n--- Test 2: Building Relations ---")
    memory.knowledge_graph.add_edge(
        unit1.id, unit2.id, RelationType.USED_IN,
        evidence=["Functions are used within classes as methods"]
    )
    print(f"Created relation: {unit1.id} -> {unit2.id}")
    
    # 测试 3: 混合检索
    print("\n--- Test 3: Hybrid Retrieval ---")
    results = memory.retrieve("code organization and structure", top_k=3)
    print(f"Found {len(results)} relevant units:")
    for unit, score in results:
        print(f"  - {unit.symbolic.label} (score: {score:.3f})")
    
    # 测试 4: 从交互学习
    print("\n--- Test 4: Learning from Interaction ---")
    learning_result = memory.learn_from_interaction(
        problem="How to fix an infinite loop?",
        solution="Add a proper termination condition to the loop",
        success=True,
        domain='coding'
    )
    print(f"Learning result: {json.dumps(learning_result, indent=2)}")
    
    # 测试 5: 知识统计
    print("\n--- Test 5: Knowledge Statistics ---")
    stats = memory.get_knowledge_stats()
    print(f"Total units: {stats['total_units']}")
    print(f"Total edges: {stats['total_edges']}")
    print(f"Strategy stats: {json.dumps(stats['strategy_stats'], indent=2)}")
    
    # 测试 6: 假设生成和测试
    print("\n--- Test 6: Hypothesis Generation and Testing ---")
    hyp = memory.meta_learner.generate_hypothesis(
        "Using meaningful variable names improves code readability",
        [unit1.id]
    )
    print(f"Generated hypothesis: {hyp.id}")
    
    # 测试假设
    memory.meta_learner.test_hypothesis(hyp.id, "Code review feedback", True)
    memory.meta_learner.test_hypothesis(hyp.id, "Team survey results", True)
    print(f"Hypothesis confidence after testing: {hyp.confidence:.3f}")
    print(f"Hypothesis status: {hyp.status}")
    
    print("\n=== All Tests Complete ===")
