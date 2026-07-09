"""
阶段 11: 概念抽象与零样本泛化
模块：元模式识别器 (Meta-Pattern Recognizer)

功能：
- 从具体案例中提取抽象结构
- 识别跨领域的同构关系
- 构建概念层级图谱
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import numpy as np
from enum import Enum


class PatternType(Enum):
    """模式类型枚举"""
    SEQUENTIAL = "sequential"  # 序列模式
    HIERARCHICAL = "hierarchical"  # 层级模式
    NETWORK = "network"  # 网络模式
    CYCLICAL = "cyclical"  # 循环模式
    CAUSAL = "causal"  # 因果模式
    ANALOGICAL = "analogical"  # 类比模式
    TRANSFORMATION = "transformation"  # 转换模式
    RECURSIVE = "recursive"  # 递归模式


@dataclass
class AbstractStructure:
    """抽象结构表示"""
    name: str
    pattern_type: PatternType
    elements: List[str]
    relations: List[Tuple[str, str, str]]  # (source, relation_type, target)
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "pattern_type": self.pattern_type.value,
            "elements": self.elements,
            "relations": [(s, r, t) for s, r, t in self.relations],
            "constraints": self.constraints,
            "metadata": self.metadata
        }


@dataclass
class ConcreteCase:
    """具体案例表示"""
    domain: str
    name: str
    entities: List[str]
    relationships: List[Tuple[str, str, str]]  # (entity1, relation, entity2)
    attributes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    context: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "domain": self.domain,
            "name": self.name,
            "entities": self.entities,
            "relationships": [(e1, r, e2) for e1, r, e2 in self.relationships],
            "attributes": self.attributes,
            "context": self.context
        }


@dataclass
class Isomorphism:
    """同构关系表示"""
    source_case: str
    target_case: str
    mapping: Dict[str, str]  # source_entity -> target_entity
    structural_similarity: float
    preserved_relations: List[Tuple[str, str, str]]
    confidence: float


class ConceptHierarchy:
    """概念层级图谱"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}  # concept_id -> {name, level, parent, children, properties}
        self.edges: Dict[str, List[str]] = defaultdict(list)  # parent_id -> [child_ids]
        self.root_concepts: Set[str] = set()
        
    def add_concept(self, concept_id: str, name: str, level: int = 0, 
                    parent_id: Optional[str] = None, properties: Optional[Dict] = None):
        """添加概念节点"""
        self.nodes[concept_id] = {
            "name": name,
            "level": level,
            "parent": parent_id,
            "children": [],
            "properties": properties or {}
        }
        
        if parent_id:
            self.edges[parent_id].append(concept_id)
            if parent_id in self.nodes:
                self.nodes[parent_id]["children"].append(concept_id)
        else:
            self.root_concepts.add(concept_id)
            
    def get_path_to_root(self, concept_id: str) -> List[str]:
        """获取概念到根节点的路径"""
        path = []
        current = concept_id
        while current:
            path.append(current)
            current = self.nodes.get(current, {}).get("parent")
        return list(reversed(path))
    
    def find_lowest_common_ancestor(self, concept1: str, concept2: str) -> Optional[str]:
        """查找两个概念的最低公共祖先"""
        path1 = set(self.get_path_to_root(concept1))
        path2 = self.get_path_to_root(concept2)
        
        for node in reversed(path2):
            if node in path1:
                return node
        return None
    
    def get_subtree(self, concept_id: str) -> List[str]:
        """获取概念的所有后代节点"""
        subtree = []
        stack = [concept_id]
        while stack:
            node = stack.pop()
            subtree.append(node)
            stack.extend(self.edges.get(node, []))
        return subtree
    
    def to_dict(self) -> Dict:
        return {
            "nodes": self.nodes,
            "edges": dict(self.edges),
            "root_concepts": list(self.root_concepts)
        }


class MetaPatternRecognizer:
    """
    元模式识别器
    
    核心功能：
    1. 从具体案例中提取抽象模式
    2. 识别跨领域的结构同构
    3. 构建和维护概念层级
    """
    
    def __init__(self):
        self.cases: Dict[str, ConcreteCase] = {}
        self.abstract_structures: Dict[str, AbstractStructure] = {}
        self.isomorphisms: List[Isomorphism] = []
        self.concept_hierarchy = ConceptHierarchy()
        self.pattern_templates: Dict[PatternType, Dict] = self._init_pattern_templates()
        
    def _init_pattern_templates(self) -> Dict[PatternType, Dict]:
        """初始化模式模板库"""
        return {
            PatternType.SEQUENTIAL: {
                "description": "线性顺序关系",
                "min_elements": 2,
                "required_relations": ["precedes", "follows"],
                "constraints": ["acyclic", "connected"]
            },
            PatternType.HIERARCHICAL: {
                "description": "树状层级结构",
                "min_elements": 3,
                "required_relations": ["contains", "belongs_to", "is_a"],
                "constraints": ["single_parent", "no_cycles"]
            },
            PatternType.NETWORK: {
                "description": "网状连接结构",
                "min_elements": 3,
                "required_relations": ["connected_to", "interacts_with"],
                "constraints": ["multi_connections"]
            },
            PatternType.CYCLICAL: {
                "description": "循环反馈结构",
                "min_elements": 2,
                "required_relations": ["leads_to", "feeds_back"],
                "constraints": ["has_cycle"]
            },
            PatternType.CAUSAL: {
                "description": "因果关系链",
                "min_elements": 2,
                "required_relations": ["causes", "enables", "prevents"],
                "constraints": ["directional", "temporal_order"]
            },
            PatternType.ANALOGICAL: {
                "description": "类比映射结构",
                "min_elements": 4,
                "required_relations": ["similar_to", "maps_to"],
                "constraints": ["structural_preservation"]
            },
            PatternType.TRANSFORMATION: {
                "description": "状态转换模式",
                "min_elements": 2,
                "required_relations": ["transforms_to", "becomes"],
                "constraints": ["state_change"]
            },
            PatternType.RECURSIVE: {
                "description": "自相似递归结构",
                "min_elements": 1,
                "required_relations": ["contains_self", "self_similar"],
                "constraints": ["fractal_property"]
            }
        }
    
    def add_case(self, case: ConcreteCase) -> str:
        """添加具体案例"""
        case_id = f"{case.domain}_{case.name}"
        self.cases[case_id] = case
        return case_id
    
    def extract_abstract_structure(self, case_id: str) -> Optional[AbstractStructure]:
        """从具体案例中提取抽象结构"""
        if case_id not in self.cases:
            return None
            
        case = self.cases[case_id]
        
        # 识别主导模式类型
        pattern_type = self._identify_pattern_type(case)
        
        # 提取抽象元素（去除领域特定信息）
        abstract_elements = self._abstract_entities(case.entities)
        
        # 提取抽象关系
        abstract_relations = self._abstract_relations(case.relationships)
        
        # 识别约束条件
        constraints = self._identify_constraints(case, pattern_type)
        
        # 创建抽象结构
        structure = AbstractStructure(
            name=f"abstract_{pattern_type.value}_{len(self.abstract_structures)}",
            pattern_type=pattern_type,
            elements=abstract_elements,
            relations=abstract_relations,
            constraints=constraints,
            metadata={
                "source_case": case_id,
                "domain": case.domain,
                "original_elements_count": len(case.entities),
                "original_relations_count": len(case.relationships)
            }
        )
        
        self.abstract_structures[structure.name] = structure
        
        # 更新概念层级
        self._update_concept_hierarchy(structure, case)
        
        return structure
    
    def _identify_pattern_type(self, case: ConcreteCase) -> PatternType:
        """识别案例的主导模式类型"""
        relation_types = set(rel[1] for rel in case.relationships)
        
        # 检查是否存在循环
        has_cycle = self._detect_cycle(case)
        
        # 检查层级特征
        is_hierarchical = self._check_hierarchical(case)
        
        # 检查因果特征
        is_causal = any(r in relation_types for r in ["causes", "enables", "prevents"])
        
        # 基于特征判断模式类型
        if is_causal:
            return PatternType.CAUSAL
        elif has_cycle:
            return PatternType.CYCLICAL
        elif is_hierarchical:
            return PatternType.HIERARCHICAL
        elif len(case.entities) > 5 and len(case.relationships) > len(case.entities):
            return PatternType.NETWORK
        else:
            return PatternType.SEQUENTIAL
    
    def _detect_cycle(self, case: ConcreteCase) -> bool:
        """检测图中是否存在环"""
        # 构建邻接表
        graph = defaultdict(list)
        for src, rel, tgt in case.relationships:
            graph[src].append(tgt)
        
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in case.entities:
            if node not in visited:
                if dfs(node):
                    return True
        return False
    
    def _check_hierarchical(self, case: ConcreteCase) -> bool:
        """检查是否为层级结构"""
        # 统计每个节点的入度
        in_degree = defaultdict(int)
        for src, rel, tgt in case.relationships:
            if rel in ["contains", "is_a", "belongs_to"]:
                in_degree[tgt] += 1
        
        # 层级结构通常只有一个根节点（入度为 0）
        roots = [e for e in case.entities if in_degree[e] == 0]
        return len(roots) == 1 and len(roots) < len(case.entities) / 2
    
    def _abstract_entities(self, entities: List[str]) -> List[str]:
        """抽象化实体名称"""
        # 将具体实体名转换为通用角色名
        abstracted = []
        for i, entity in enumerate(entities):
            abstracted.append(f"E{i}")  # E0, E1, E2...
        return abstracted
    
    def _abstract_relations(self, relations: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
        """抽象化关系"""
        # 创建实体映射
        entity_map = {e: f"E{i}" for i, e in enumerate(set(e for rel in relations for e in [rel[0], rel[2]]))}
        
        abstracted = []
        for src, rel_type, tgt in relations:
            abs_src = entity_map.get(src, src)
            abs_tgt = entity_map.get(tgt, tgt)
            abs_rel = self._abstract_relation_type(rel_type)
            abstracted.append((abs_src, abs_rel, abs_tgt))
        
        return abstracted
    
    def _abstract_relation_type(self, relation: str) -> str:
        """抽象化关系类型"""
        # 将具体关系映射到通用关系类别
        relation_categories = {
            "precedes": "SEQ",
            "follows": "SEQ",
            "contains": "HIER",
            "belongs_to": "HIER",
            "is_a": "HIER",
            "connected_to": "NET",
            "interacts_with": "NET",
            "leads_to": "CYC",
            "feeds_back": "CYC",
            "causes": "CAUS",
            "enables": "CAUS",
            "prevents": "CAUS",
            "similar_to": "ANAL",
            "maps_to": "ANAL",
            "transforms_to": "TRANS",
            "becomes": "TRANS"
        }
        return relation_categories.get(relation, "GEN")
    
    def _identify_constraints(self, case: ConcreteCase, pattern_type: PatternType) -> List[str]:
        """识别结构约束"""
        constraints = []
        template = self.pattern_templates[pattern_type]
        
        # 检查模板定义的约束
        if "acyclic" in template.get("constraints", []) and not self._detect_cycle(case):
            constraints.append("acyclic")
        if "has_cycle" in template.get("constraints", []) and self._detect_cycle(case):
            constraints.append("has_cycle")
        if "single_parent" in template.get("constraints", []) and self._check_hierarchical(case):
            constraints.append("single_parent")
        
        # 添加连通性约束
        if len(case.relationships) >= len(case.entities) - 1:
            constraints.append("connected")
        
        return constraints
    
    def _update_concept_hierarchy(self, structure: AbstractStructure, case: ConcreteCase):
        """更新概念层级图谱"""
        # 添加模式类型作为高层概念
        pattern_key = structure.pattern_type.value
        if pattern_key not in self.concept_hierarchy.nodes:
            self.concept_hierarchy.add_concept(
                pattern_key,
                structure.pattern_type.value.upper(),
                level=0,
                properties={"type": "pattern_category"}
            )
        
        # 添加抽象结构作为子概念
        structure_key = structure.name
        self.concept_hierarchy.add_concept(
            structure_key,
            structure.name,
            level=1,
            parent_id=pattern_key,
            properties={"source_domain": case.domain}
        )
        
        # 添加元素和关系作为更底层概念
        for i, elem in enumerate(structure.elements):
            elem_key = f"{structure_key}_elem_{i}"
            self.concept_hierarchy.add_concept(
                elem_key,
                elem,
                level=2,
                parent_id=structure_key,
                properties={"type": "element"}
            )
    
    def find_isomorphism(self, case1_id: str, case2_id: str) -> Optional[Isomorphism]:
        """查找两个案例之间的结构同构"""
        if case1_id not in self.cases or case2_id not in self.cases:
            return None
        
        case1 = self.cases[case1_id]
        case2 = self.cases[case2_id]
        
        # 尝试构建实体映射
        mapping, similarity = self._graph_match(case1, case2)
        
        if not mapping or similarity < 0.3:  # 相似度阈值
            return None
        
        # 找出保持的关系
        preserved_relations = []
        for src, rel, tgt in case1.relationships:
            if src in mapping and tgt in mapping:
                mapped_src = mapping[src]
                mapped_tgt = mapping[tgt]
                # 检查映射后的关系是否存在
                for m_src, m_rel, m_tgt in case2.relationships:
                    if m_src == mapped_src and m_tgt == mapped_tgt:
                        preserved_relations.append((src, rel, tgt))
                        break
        
        isomorphism = Isomorphism(
            source_case=case1_id,
            target_case=case2_id,
            mapping=mapping,
            structural_similarity=similarity,
            preserved_relations=preserved_relations,
            confidence=self._calculate_confidence(mapping, preserved_relations, case1, case2)
        )
        
        self.isomorphisms.append(isomorphism)
        return isomorphism
    
    def _graph_match(self, case1: ConcreteCase, case2: ConcreteCase) -> Tuple[Dict[str, str], float]:
        """图匹配算法，寻找最佳实体映射"""
        # 简化的图匹配：基于度和关系类型的启发式匹配
        mapping = {}
        
        # 计算每个实体的度
        degree1 = self._calculate_degrees(case1)
        degree2 = self._calculate_degrees(case2)
        
        # 按度排序实体
        sorted1 = sorted(case1.entities, key=lambda e: degree1.get(e, 0), reverse=True)
        sorted2 = sorted(case2.entities, key=lambda e: degree2.get(e, 0), reverse=True)
        
        # 贪心匹配
        used2 = set()
        for e1 in sorted1:
            best_match = None
            best_score = -1
            
            for e2 in sorted2:
                if e2 in used2:
                    continue
                
                # 计算匹配分数
                score = self._match_score(e1, e2, case1, case2, degree1, degree2)
                if score > best_score:
                    best_score = score
                    best_match = e2
            
            if best_match and best_score > 0.5:
                mapping[e1] = best_match
                used2.add(best_match)
        
        # 计算整体相似度
        similarity = len(mapping) / max(len(case1.entities), len(case2.entities))
        
        return mapping, similarity
    
    def _calculate_degrees(self, case: ConcreteCase) -> Dict[str, int]:
        """计算每个实体的度"""
        degrees = defaultdict(int)
        for src, rel, tgt in case.relationships:
            degrees[src] += 1
            degrees[tgt] += 1
        return dict(degrees)
    
    def _match_score(self, e1: str, e2: str, case1: ConcreteCase, case2: ConcreteCase,
                     degree1: Dict, degree2: Dict) -> float:
        """计算两个实体的匹配分数"""
        score = 0.0
        
        # 度相似性
        d1 = degree1.get(e1, 0)
        d2 = degree2.get(e2, 0)
        if d1 > 0 and d2 > 0:
            degree_sim = min(d1, d2) / max(d1, d2)
            score += 0.4 * degree_sim
        
        # 关系类型相似性
        rels1 = set(rel[1] for rel in case1.relationships if rel[0] == e1 or rel[2] == e1)
        rels2 = set(rel[1] for rel in case2.relationships if rel[0] == e2 or rel[2] == e2)
        if rels1 and rels2:
            rel_sim = len(rels1 & rels2) / len(rels1 | rels2)
            score += 0.6 * rel_sim
        
        return score
    
    def _calculate_confidence(self, mapping: Dict[str, str], preserved_relations: List,
                              case1: ConcreteCase, case2: ConcreteCase) -> float:
        """计算同构映射的置信度"""
        if not mapping:
            return 0.0
        
        # 基于映射覆盖率
        coverage = len(mapping) / max(len(case1.entities), len(case2.entities))
        
        # 基于关系保持率
        relation_preservation = len(preserved_relations) / max(len(case1.relationships), 1)
        
        # 加权平均
        confidence = 0.5 * coverage + 0.5 * relation_preservation
        return min(confidence, 1.0)
    
    def discover_cross_domain_patterns(self, domains: Optional[List[str]] = None) -> List[Dict]:
        """发现跨领域模式"""
        if domains:
            cases_to_compare = [cid for cid in self.cases if self.cases[cid].domain in domains]
        else:
            cases_to_compare = list(self.cases.keys())
        
        patterns = []
        
        # 两两比较案例
        for i, case1_id in enumerate(cases_to_compare):
            for case2_id in cases_to_compare[i+1:]:
                case1 = self.cases[case1_id]
                case2 = self.cases[case2_id]
                
                # 只比较不同领域的案例
                if case1.domain == case2.domain:
                    continue
                
                isomorphism = self.find_isomorphism(case1_id, case2_id)
                if isomorphism and isomorphism.confidence > 0.5:
                    patterns.append({
                        "pattern_type": self._identify_pattern_type(case1).value,
                        "domain1": case1.domain,
                        "domain2": case2.domain,
                        "similarity": isomorphism.structural_similarity,
                        "confidence": isomorphism.confidence,
                        "mapping_size": len(isomorphism.mapping)
                    })
        
        # 按相似度排序
        patterns.sort(key=lambda x: x["similarity"], reverse=True)
        return patterns
    
    def get_concept_hierarchy(self) -> Dict:
        """获取概念层级图谱"""
        return self.concept_hierarchy.to_dict()
    
    def query_similar_structures(self, query_case: ConcreteCase, top_k: int = 5) -> List[Dict]:
        """查询与给定案例相似的结构"""
        similarities = []
        
        for case_id, stored_case in self.cases.items():
            _, sim = self._graph_match(query_case, stored_case)
            if sim > 0.3:
                similarities.append({
                    "case_id": case_id,
                    "domain": stored_case.domain,
                    "similarity": sim,
                    "pattern_type": self._identify_pattern_type(stored_case).value
                })
        
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]


# 便捷函数
def create_case(domain: str, name: str, entities: List[str], 
                relationships: List[Tuple[str, str, str]], 
                attributes: Optional[Dict] = None, context: str = "") -> ConcreteCase:
    """创建具体案例的便捷函数"""
    return ConcreteCase(
        domain=domain,
        name=name,
        entities=entities,
        relationships=relationships,
        attributes=attributes or {},
        context=context
    )
