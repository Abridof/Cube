"""
阶段 11: 概念抽象与零样本泛化模块

本模块实现概念抽象、类比推理和概念组合创造力功能，
使 AI 能够从具体经验中提炼抽象概念并跨领域迁移应用。

核心组件:
- MetaPatternRecognizer: 元模式识别器，从案例中提取抽象结构
- AnalogyEngine: 类比推理引擎，实现源域 - 目标域映射
- ConceptBlender: 概念组合模块，生成创造性概念
- ConceptHierarchyGraph: 概念层级图谱

作者：AGI 项目组
版本：v11.0
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
import copy
from enum import Enum


class PatternType(Enum):
    """模式类型枚举"""
    SEQUENTIAL = "sequential"  # 序列模式
    HIERARCHICAL = "hierarchical"  # 层级模式
    TRANSFORMATIONAL = "transformational"  # 转换模式
    CAUSAL = "causal"  # 因果模式
    ANALOGICAL = "analogical"  # 类比模式
    RECURSIVE = "recursive"  # 递归模式


@dataclass
class AbstractPattern:
    """抽象模式表示"""
    pattern_id: str
    pattern_type: PatternType
    structure: Dict[str, Any]
    variables: List[str]
    constraints: List[str]
    source_domains: List[str]
    confidence: float
    abstraction_level: int  # 1=具体，5=高度抽象
    
    def to_dict(self) -> Dict:
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type.value,
            'structure': self.structure,
            'variables': self.variables,
            'constraints': self.constraints,
            'source_domains': self.source_domains,
            'confidence': self.confidence,
            'abstraction_level': self.abstraction_level
        }


@dataclass
class Concept:
    """概念表示"""
    concept_id: str
    name: str
    attributes: Dict[str, Any]
    relations: List[Tuple[str, str, Any]]  # (relation_type, target_concept, weight)
    abstraction_level: int
    domain: str
    instances: List[str] = field(default_factory=list)
    
    def similarity(self, other: 'Concept') -> float:
        """计算两个概念的相似度"""
        if not isinstance(other, Concept):
            return 0.0
        
        # 属性相似度
        common_attrs = set(self.attributes.keys()) & set(other.attributes.keys())
        if common_attrs:
            attr_sim = sum(
                1.0 / (1.0 + abs(self.attributes[a] - other.attributes[a]))
                if isinstance(self.attributes[a], (int, float)) and isinstance(other.attributes[a], (int, float))
                else 1.0 if self.attributes[a] == other.attributes[a] else 0.0
                for a in common_attrs
            ) / len(common_attrs)
        else:
            attr_sim = 0.0
        
        # 领域相似度
        domain_sim = 1.0 if self.domain == other.domain else 0.3
        
        # 抽象层级相似度
        level_sim = 1.0 / (1.0 + abs(self.abstraction_level - other.abstraction_level))
        
        return 0.5 * attr_sim + 0.3 * domain_sim + 0.2 * level_sim


@dataclass
class Mapping:
    """源域到目标域的映射"""
    source_element: str
    target_element: str
    mapping_type: str  # 'structural', 'relational', 'attribute'
    confidence: float
    justification: str


@dataclass
class BlendedConcept:
    """混合概念"""
    concept_id: str
    name: str
    source_concepts: List[str]
    blended_attributes: Dict[str, Any]
    emergent_properties: List[str]  # 涌现属性
    creativity_score: float
    coherence_score: float
    usefulness_score: float
    
    def overall_creativity(self) -> float:
        """综合创造性评分"""
        return 0.4 * self.creativity_score + 0.3 * self.coherence_score + 0.3 * self.usefulness_score


class ConceptHierarchyGraph:
    """概念层级图谱"""
    
    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.parent_child_relations: Dict[str, List[str]] = defaultdict(list)
        self.instance_of_relations: Dict[str, str] = {}  # instance -> concept
        self.similarity_cache: Dict[Tuple[str, str], float] = {}
        
    def add_concept(self, concept: Concept) -> None:
        """添加概念到图谱"""
        self.concepts[concept.concept_id] = concept
        
    def add_parent_child(self, parent_id: str, child_id: str) -> None:
        """建立父子关系"""
        self.parent_child_relations[parent_id].append(child_id)
        
    def add_instance(self, instance_id: str, concept_id: str) -> None:
        """添加实例"""
        self.instance_of_relations[instance_id] = concept_id
        if concept_id in self.concepts:
            self.concepts[concept_id].instances.append(instance_id)
            
    def get_ancestors(self, concept_id: str) -> List[str]:
        """获取所有祖先概念"""
        ancestors = []
        for parent, children in self.parent_child_relations.items():
            if concept_id in children:
                ancestors.append(parent)
                ancestors.extend(self.get_ancestors(parent))
        return ancestors
    
    def get_descendants(self, concept_id: str) -> List[str]:
        """获取所有后代概念"""
        descendants = []
        if concept_id in self.parent_child_relations:
            for child in self.parent_child_relations[concept_id]:
                descendants.append(child)
                descendants.extend(self.get_descendants(child))
        return descendants
    
    def find_similar_concepts(self, concept_id: str, threshold: float = 0.5) -> List[Tuple[str, float]]:
        """查找相似概念"""
        if concept_id not in self.concepts:
            return []
        
        target = self.concepts[concept_id]
        similarities = []
        
        for cid, concept in self.concepts.items():
            if cid == concept_id:
                continue
            
            cache_key = tuple(sorted([concept_id, cid]))
            if cache_key in self.similarity_cache:
                sim = self.similarity_cache[cache_key]
            else:
                sim = target.similarity(concept)
                self.similarity_cache[cache_key] = sim
            
            if sim >= threshold:
                similarities.append((cid, sim))
        
        return sorted(similarities, key=lambda x: -x[1])
    
    def get_abstraction_path(self, concept_id: str) -> List[str]:
        """获取从具体到抽象的路径"""
        path = [concept_id]
        current = concept_id
        
        while True:
            found_parent = False
            for parent, children in self.parent_child_relations.items():
                if current in children:
                    path.append(parent)
                    current = parent
                    found_parent = True
                    break
            
            if not found_parent:
                break
        
        return path


class MetaPatternRecognizer:
    """
    元模式识别器
    
    从具体案例中提取抽象结构，识别跨领域的同构关系，
    构建概念层级图谱。
    """
    
    def __init__(self):
        self.patterns: Dict[str, AbstractPattern] = {}
        self.concept_graph = ConceptHierarchyGraph()
        self.extraction_history: List[Dict] = []
        
    def extract_pattern(self, 
                       case_data: Dict[str, Any],
                       domain: str,
                       pattern_type: PatternType) -> AbstractPattern:
        """从案例中提取抽象模式"""
        
        pattern_id = f"pattern_{len(self.patterns) + 1:04d}"
        
        # 根据模式类型提取不同结构
        if pattern_type == PatternType.SEQUENTIAL:
            structure = self._extract_sequential_structure(case_data)
        elif pattern_type == PatternType.HIERARCHICAL:
            structure = self._extract_hierarchical_structure(case_data)
        elif pattern_type == PatternType.TRANSFORMATIONAL:
            structure = self._extract_transformational_structure(case_data)
        elif pattern_type == PatternType.CAUSAL:
            structure = self._extract_causal_structure(case_data)
        elif pattern_type == PatternType.ANALOGICAL:
            structure = self._extract_analogical_structure(case_data)
        elif pattern_type == PatternType.RECURSIVE:
            structure = self._extract_recursive_structure(case_data)
        else:
            structure = {"raw": case_data}
        
        # 识别变量
        variables = self._identify_variables(structure)
        
        # 生成约束条件
        constraints = self._generate_constraints(structure, variables)
        
        # 计算抽象层级
        abstraction_level = self._calculate_abstraction_level(structure, variables)
        
        pattern = AbstractPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            structure=structure,
            variables=variables,
            constraints=constraints,
            source_domains=[domain],
            confidence=0.85,
            abstraction_level=abstraction_level
        )
        
        self.patterns[pattern_id] = pattern
        self.extraction_history.append({
            'pattern_id': pattern_id,
            'domain': domain,
            'timestamp': len(self.extraction_history)
        })
        
        return pattern
    
    def _extract_sequential_structure(self, data: Dict) -> Dict:
        """提取序列结构"""
        if 'sequence' in data:
            seq = data['sequence']
            return {
                'type': 'sequence',
                'length': len(seq),
                'elements': [str(e) for e in seq],
                'transitions': [(seq[i], seq[i+1]) for i in range(len(seq)-1)]
            }
        return {'type': 'sequence', 'raw': data}
    
    def _extract_hierarchical_structure(self, data: Dict) -> Dict:
        """提取层级结构"""
        def build_tree(node, depth=0):
            result = {'depth': depth, 'children': []}
            if 'children' in node:
                for child in node['children']:
                    result['children'].append(build_tree(child, depth + 1))
            if 'value' in node:
                result['value'] = node['value']
            return result
        
        if 'root' in data:
            return build_tree(data['root'])
        return {'type': 'hierarchy', 'raw': data}
    
    def _extract_transformational_structure(self, data: Dict) -> Dict:
        """提取转换结构"""
        if 'initial' in data and 'final' in data:
            return {
                'type': 'transformation',
                'initial_state': data['initial'],
                'final_state': data['final'],
                'operations': data.get('operations', [])
            }
        return {'type': 'transformation', 'raw': data}
    
    def _extract_causal_structure(self, data: Dict) -> Dict:
        """提取因果结构"""
        if 'causes' in data and 'effects' in data:
            return {
                'type': 'causal',
                'causes': data['causes'],
                'effects': data['effects'],
                'mechanism': data.get('mechanism', 'unknown')
            }
        return {'type': 'causal', 'raw': data}
    
    def _extract_analogical_structure(self, data: Dict) -> Dict:
        """提取类比结构"""
        if 'source' in data and 'target' in data:
            return {
                'type': 'analogical',
                'source_domain': data['source'],
                'target_domain': data['target'],
                'mappings': data.get('mappings', [])
            }
        return {'type': 'analogical', 'raw': data}
    
    def _extract_recursive_structure(self, data: Dict) -> Dict:
        """提取递归结构"""
        if 'base_case' in data and 'recursive_case' in data:
            return {
                'type': 'recursive',
                'base_case': data['base_case'],
                'recursive_case': data['recursive_case'],
                'termination_condition': data.get('termination', 'unknown')
            }
        return {'type': 'recursive', 'raw': data}
    
    def _identify_variables(self, structure: Dict) -> List[str]:
        """识别模式中的变量"""
        variables = []
        
        def find_vars(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ['type', 'raw']:
                        continue
                    find_vars(v, f"{path}.{k}" if path else k)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_vars(item, f"{path}[{i}]")
            elif isinstance(obj, str) and obj.startswith('$'):
                variables.append(obj)
        
        find_vars(structure)
        return list(set(variables))
    
    def _generate_constraints(self, structure: Dict, variables: List[str]) -> List[str]:
        """生成约束条件"""
        constraints = []
        
        if variables:
            constraints.append(f"Must have {len(variables)} variables bound")
        
        if structure.get('type') == 'sequence':
            constraints.append("Sequence elements must be ordered")
        elif structure.get('type') == 'hierarchy':
            constraints.append("No cycles allowed in hierarchy")
        elif structure.get('type') == 'causal':
            constraints.append("Cause must precede effect temporally")
        
        return constraints
    
    def _calculate_abstraction_level(self, structure: Dict, variables: List[str]) -> int:
        """计算抽象层级 (1-5)"""
        level = 1
        
        # 变量数量增加抽象度
        if len(variables) >= 3:
            level += 1
        if len(variables) >= 5:
            level += 1
        
        # 结构复杂度
        structure_str = str(structure)
        if len(structure_str) > 200:
            level += 1
        if len(structure_str) > 500:
            level += 1
        
        return min(level, 5)
    
    def find_isomorphic_patterns(self, domain1: str, domain2: str) -> List[Tuple[str, str, float]]:
        """查找两个领域之间的同构模式"""
        isomorphisms = []
        
        domain1_patterns = [
            p for p in self.patterns.values()
            if domain1 in p.source_domains
        ]
        domain2_patterns = [
            p for p in self.patterns.values()
            if domain2 in p.source_domains
        ]
        
        for p1 in domain1_patterns:
            for p2 in domain2_patterns:
                if p1.pattern_type != p2.pattern_type:
                    continue
                
                # 计算结构相似度
                similarity = self._calculate_structural_similarity(p1.structure, p2.structure)
                
                if similarity > 0.6:
                    isomorphisms.append((p1.pattern_id, p2.pattern_id, similarity))
        
        return sorted(isomorphisms, key=lambda x: -x[2])
    
    def _calculate_structural_similarity(self, s1: Dict, s2: Dict) -> float:
        """计算两个结构的相似度"""
        if type(s1) != type(s2):
            return 0.0
        
        if isinstance(s1, dict):
            common_keys = set(s1.keys()) & set(s2.keys())
            if not common_keys:
                return 0.0
            
            key_sim = len(common_keys) / max(len(s1), len(s2))
            
            value_sims = []
            for k in common_keys:
                if k in ['type', 'raw']:
                    value_sims.append(1.0 if s1[k] == s2[k] else 0.0)
                else:
                    value_sims.append(self._calculate_structural_similarity(s1[k], s2[k]))
            
            return 0.4 * key_sim + 0.6 * (sum(value_sims) / len(value_sims) if value_sims else 0)
        
        elif isinstance(s1, list):
            if len(s1) != len(s2):
                return 0.0
            
            sims = [self._calculate_structural_similarity(a, b) for a, b in zip(s1, s2)]
            return sum(sims) / len(sims) if sims else 0.0
        
        else:
            return 1.0 if s1 == s2 else 0.0
    
    def build_concept_hierarchy(self, concepts: List[Concept]) -> None:
        """构建概念层级图谱"""
        for concept in concepts:
            self.concept_graph.add_concept(concept)
        
        # 自动发现父子关系
        for c1 in concepts:
            for c2 in concepts:
                if c1.concept_id == c2.concept_id:
                    continue
                
                # 如果 c1 的属性是 c2 的子集且 c2 更抽象
                if (set(c1.attributes.keys()) >= set(c2.attributes.keys()) and
                    c1.abstraction_level < c2.abstraction_level):
                    self.concept_graph.add_parent_child(c2.concept_id, c1.concept_id)


class AnalogyEngine:
    """
    类比推理引擎
    
    实现源域到目标域的映射，支持结构映射理论 (Structure-Mapping Theory)，
    测试零样本迁移学习能力。
    """
    
    def __init__(self):
        self.mappings: List[Mapping] = []
        self.analogy_history: List[Dict] = []
        
    def create_analogy(self,
                      source_domain: Dict[str, Any],
                      target_domain: Dict[str, Any],
                      pattern: Optional[AbstractPattern] = None) -> Dict[str, Any]:
        """创建类比映射"""
        
        # 提取源域和目标域的结构
        source_elements = self._extract_elements(source_domain)
        target_elements = self._extract_elements(target_domain)
        
        # 生成候选映射
        candidate_mappings = self._generate_candidate_mappings(
            source_elements, target_elements
        )
        
        # 评估和选择最佳映射
        best_mappings = self._select_best_mappings(candidate_mappings)
        
        # 验证结构一致性
        consistent_mappings = self._verify_structural_consistency(
            best_mappings, source_domain, target_domain
        )
        
        self.mappings.extend(consistent_mappings)
        
        # 生成推理结果
        inference = self._generate_inference(
            consistent_mappings, source_domain, target_domain
        )
        
        self.analogy_history.append({
            'source': source_domain,
            'target': target_domain,
            'mappings': [m.__dict__ for m in consistent_mappings],
            'inference': inference
        })
        
        return {
            'mappings': consistent_mappings,
            'inference': inference,
            'confidence': self._calculate_confidence(consistent_mappings)
        }
    
    def _extract_elements(self, domain: Dict) -> Dict[str, Any]:
        """提取领域中的元素"""
        elements = {
            'objects': [],
            'attributes': {},
            'relations': [],
            'functions': []
        }
        
        if 'objects' in domain:
            elements['objects'] = domain['objects']
        
        if 'attributes' in domain:
            elements['attributes'] = domain['attributes']
        
        if 'relations' in domain:
            elements['relations'] = domain['relations']
        
        if 'functions' in domain:
            elements['functions'] = domain['functions']
        
        return elements
    
    def _generate_candidate_mappings(self,
                                    source: Dict,
                                    target: Dict) -> List[Mapping]:
        """生成候选映射"""
        candidates = []
        
        # 对象映射
        for src_obj in source.get('objects', []):
            for tgt_obj in target.get('objects', []):
                similarity = self._calculate_element_similarity(src_obj, tgt_obj)
                if similarity > 0.3:
                    candidates.append(Mapping(
                        source_element=str(src_obj),
                        target_element=str(tgt_obj),
                        mapping_type='structural',
                        confidence=similarity,
                        justification=f"Object similarity: {similarity:.2f}"
                    ))
        
        # 属性映射
        for src_attr, src_val in source.get('attributes', {}).items():
            for tgt_attr, tgt_val in target.get('attributes', {}).items():
                similarity = self._calculate_attribute_similarity(
                    src_attr, src_val, tgt_attr, tgt_val
                )
                if similarity > 0.3:
                    candidates.append(Mapping(
                        source_element=f"attr:{src_attr}",
                        target_element=f"attr:{tgt_attr}",
                        mapping_type='attribute',
                        confidence=similarity,
                        justification=f"Attribute mapping: {src_attr}->{tgt_attr}"
                    ))
        
        # 关系映射
        for src_rel in source.get('relations', []):
            for tgt_rel in target.get('relations', []):
                similarity = self._calculate_relation_similarity(src_rel, tgt_rel)
                if similarity > 0.3:
                    candidates.append(Mapping(
                        source_element=f"rel:{src_rel[0] if isinstance(src_rel, tuple) else src_rel}",
                        target_element=f"rel:{tgt_rel[0] if isinstance(tgt_rel, tuple) else tgt_rel}",
                        mapping_type='relational',
                        confidence=similarity,
                        justification=f"Relational correspondence"
                    ))
        
        return candidates
    
    def _calculate_element_similarity(self, elem1: Any, elem2: Any) -> float:
        """计算元素相似度"""
        str1, str2 = str(elem1), str(elem2)
        
        # 简单字符串相似度
        common_chars = set(str1) & set(str2)
        char_sim = len(common_chars) / max(len(str1), len(str2), 1)
        
        # 类型匹配
        type_sim = 1.0 if type(elem1) == type(elem2) else 0.3
        
        return 0.5 * char_sim + 0.5 * type_sim
    
    def _calculate_attribute_similarity(self,
                                       attr1: str, val1: Any,
                                       attr2: str, val2: Any) -> float:
        """计算属性相似度"""
        # 属性名相似度
        name_sim = self._calculate_element_similarity(attr1, attr2)
        
        # 值相似度
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            val_sim = 1.0 / (1.0 + abs(val1 - val2))
        else:
            val_sim = 1.0 if val1 == val2 else 0.3
        
        return 0.4 * name_sim + 0.6 * val_sim
    
    def _calculate_relation_similarity(self, rel1: Any, rel2: Any) -> float:
        """计算关系相似度"""
        str1 = str(rel1[0]) if isinstance(rel1, tuple) else str(rel1)
        str2 = str(rel2[0]) if isinstance(rel2, tuple) else str(rel2)
        
        return self._calculate_element_similarity(str1, str2)
    
    def _select_best_mappings(self,
                             candidates: List[Mapping],
                             max_mappings: int = 10) -> List[Mapping]:
        """选择最佳映射（一对一原则）"""
        selected = []
        used_sources = set()
        used_targets = set()
        
        # 按置信度排序
        sorted_candidates = sorted(candidates, key=lambda m: -m.confidence)
        
        for candidate in sorted_candidates:
            if (candidate.source_element not in used_sources and
                candidate.target_element not in used_targets):
                selected.append(candidate)
                used_sources.add(candidate.source_element)
                used_targets.add(candidate.target_element)
                
                if len(selected) >= max_mappings:
                    break
        
        return selected
    
    def _verify_structural_consistency(self,
                                      mappings: List[Mapping],
                                      source: Dict,
                                      target: Dict) -> List[Mapping]:
        """验证结构一致性（平行连接性原则）"""
        consistent = []
        
        for mapping in mappings:
            # 检查是否有相关关系也建立了映射
            is_consistent = True
            
            if mapping.mapping_type == 'structural':
                # 对于对象映射，检查其属性和关系是否也有对应映射
                related_mappings = [
                    m for m in mappings
                    if m.source_element.startswith(mapping.source_element) or
                       m.target_element.startswith(mapping.target_element)
                ]
                
                if len(related_mappings) < 2:
                    is_consistent = False
            
            if is_consistent:
                consistent.append(mapping)
        
        return consistent
    
    def _generate_inference(self,
                           mappings: List[Mapping],
                           source: Dict,
                           target: Dict) -> Dict[str, Any]:
        """基于类比生成推理"""
        inferences = {
            'predicted_attributes': {},
            'predicted_relations': [],
            'suggested_operations': []
        }
        
        # 从源域推断目标域可能缺少的属性
        source_attrs = source.get('attributes', {})
        target_attrs = target.get('attributes', {})
        
        for mapping in mappings:
            if mapping.mapping_type == 'attribute':
                src_attr = mapping.source_element.replace('attr:', '')
                tgt_attr = mapping.target_element.replace('attr:', '')
                
                if src_attr in source_attrs and tgt_attr not in target_attrs:
                    inferences['predicted_attributes'][tgt_attr] = source_attrs[src_attr]
        
        # 推断可能的关系
        source_rels = source.get('relations', [])
        target_rels = target.get('relations', [])
        
        for src_rel in source_rels:
            rel_name = src_rel[0] if isinstance(src_rel, tuple) else src_rel
            
            # 查找对应的关系映射
            rel_mapping = next(
                (m for m in mappings if m.source_element == f"rel:{rel_name}"),
                None
            )
            
            if rel_mapping and rel_mapping.target_element.replace('rel:', '') not in [
                r[0] if isinstance(r, tuple) else r for r in target_rels
            ]:
                inferences['predicted_relations'].append(rel_mapping.target_element)
        
        return inferences
    
    def _calculate_confidence(self, mappings: List[Mapping]) -> float:
        """计算整体类比置信度"""
        if not mappings:
            return 0.0
        
        avg_confidence = sum(m.confidence for m in mappings) / len(mappings)
        
        # 映射数量奖励
        quantity_bonus = min(len(mappings) / 10.0, 0.2)
        
        # 映射类型多样性奖励
        types_present = len(set(m.mapping_type for m in mappings))
        diversity_bonus = (types_present - 1) * 0.1
        
        return min(avg_confidence + quantity_bonus + diversity_bonus, 1.0)
    
    def zero_shot_transfer(self,
                          source_task: Dict,
                          target_task: Dict,
                          learned_solution: Any) -> Any:
        """零样本迁移学习"""
        
        # 创建类比
        analogy_result = self.create_analogy(
            source_task.get('domain', {}),
            target_task.get('domain', {})
        )
        
        if analogy_result['confidence'] < 0.5:
            return None  # 类比太弱，无法迁移
        
        # 根据映射转换解决方案
        transferred_solution = self._transform_solution(
            learned_solution,
            analogy_result['mappings']
        )
        
        return {
            'transferred_solution': transferred_solution,
            'confidence': analogy_result['confidence'],
            'mappings_used': len(analogy_result['mappings'])
        }
    
    def _transform_solution(self, solution: Any, mappings: List[Mapping]) -> Any:
        """根据映射转换解决方案"""
        if isinstance(solution, dict):
            transformed = {}
            for k, v in solution.items():
                new_k = k
                for m in mappings:
                    if m.source_element.endswith(k):
                        new_k = m.target_element.split(':')[-1]
                        break
                transformed[new_k] = self._transform_solution(v, mappings)
            return transformed
        elif isinstance(solution, list):
            return [self._transform_solution(item, mappings) for item in solution]
        else:
            transformed = solution
            for m in mappings:
                if str(solution) == m.source_element:
                    transformed = m.target_element
                    break
            return transformed


class ConceptBlender:
    """
    概念组合创造力模块
    
    实现概念混合 (Conceptual Blending)，生成新颖但有意义的组合概念，
    评估创造性输出的质量。
    """
    
    def __init__(self):
        self.blended_concepts: List[BlendedConcept] = []
        self.creativity_metrics: Dict[str, float] = {}
        
    def blend_concepts(self,
                      concept1: Concept,
                      concept2: Concept,
                      blend_type: str = 'fusion') -> BlendedConcept:
        """混合两个概念"""
        
        blend_id = f"blend_{len(self.blended_concepts) + 1:04d}"
        blend_name = f"{concept1.name}-{concept2.name}"
        
        # 根据混合类型执行不同策略
        if blend_type == 'fusion':
            blended_attrs = self._fusion_blend(concept1.attributes, concept2.attributes)
        elif blend_type == 'contrast':
            blended_attrs = self._contrast_blend(concept1.attributes, concept2.attributes)
        elif blend_type == 'metaphor':
            blended_attrs = self._metaphor_blend(concept1.attributes, concept2.attributes)
        else:
            blended_attrs = self._fusion_blend(concept1.attributes, concept2.attributes)
        
        # 识别涌现属性
        emergent_props = self._identify_emergent_properties(
            concept1, concept2, blended_attrs
        )
        
        # 评估创造性
        creativity_score = self._evaluate_creativity(
            concept1, concept2, blended_attrs, emergent_props
        )
        
        # 评估连贯性
        coherence_score = self._evaluate_coherence(
            concept1, concept2, blended_attrs
        )
        
        # 评估有用性
        usefulness_score = self._evaluate_usefulness(blended_attrs)
        
        blended = BlendedConcept(
            concept_id=blend_id,
            name=blend_name,
            source_concepts=[concept1.concept_id, concept2.concept_id],
            blended_attributes=blended_attrs,
            emergent_properties=emergent_props,
            creativity_score=creativity_score,
            coherence_score=coherence_score,
            usefulness_score=usefulness_score
        )
        
        self.blended_concepts.append(blended)
        
        return blended
    
    def _fusion_blend(self, attrs1: Dict, attrs2: Dict) -> Dict:
        """融合式混合：合并共同属性"""
        blended = {}
        
        all_keys = set(attrs1.keys()) | set(attrs2.keys())
        
        for key in all_keys:
            if key in attrs1 and key in attrs2:
                # 都有该属性，取平均值或合并
                if isinstance(attrs1[key], (int, float)) and isinstance(attrs2[key], (int, float)):
                    blended[key] = (attrs1[key] + attrs2[key]) / 2
                elif attrs1[key] == attrs2[key]:
                    blended[key] = attrs1[key]
                else:
                    blended[key] = f"{attrs1[key]}-{attrs2[key]}"
            elif key in attrs1:
                blended[key] = attrs1[key]
            else:
                blended[key] = attrs2[key]
        
        return blended
    
    def _contrast_blend(self, attrs1: Dict, attrs2: Dict) -> Dict:
        """对比式混合：强调差异"""
        blended = {}
        
        for key, val1 in attrs1.items():
            if key in attrs2:
                val2 = attrs2[key]
                if val1 != val2:
                    blended[f"{key}_contrast"] = f"{val1}_vs_{val2}"
        
        return blended
    
    def _metaphor_blend(self, attrs1: Dict, attrs2: Dict) -> Dict:
        """隐喻式混合：将一个概念的属性映射到另一个"""
        blended = dict(attrs1)  # 以 concept1 为基础
        
        # 选择性添加 concept2 的属性
        for key, val in attrs2.items():
            if key not in blended:
                blended[f"metaphor_{key}"] = val
        
        return blended
    
    def _identify_emergent_properties(self,
                                     c1: Concept,
                                     c2: Concept,
                                     blended_attrs: Dict) -> List[str]:
        """识别涌现属性"""
        emergent = []
        
        # 检查是否有新的属性组合产生新含义
        if 'speed' in blended_attrs and 'size' in blended_attrs:
            if isinstance(blended_attrs['speed'], (int, float)) and blended_attrs['speed'] > 5:
                if isinstance(blended_attrs['size'], (int, float)) and blended_attrs['size'] < 3:
                    emergent.append("high_speed_small_form_factor")
        
        # 检查概念领域的交叉
        if c1.domain != c2.domain:
            emergent.append(f"cross_domain_{c1.domain}_{c2.domain}")
        
        # 检查抽象层级的变化
        avg_level = (c1.abstraction_level + c2.abstraction_level) / 2
        if avg_level > 3:
            emergent.append("high_abstraction_synthesis")
        
        return emergent
    
    def _evaluate_creativity(self,
                            c1: Concept,
                            c2: Concept,
                            attrs: Dict,
                            emergent: List[str]) -> float:
        """评估创造性分数"""
        score = 0.0
        
        # 新颖性：概念来自不同领域
        if c1.domain != c2.domain:
            score += 0.3
        
        # 稀有性：属性组合不常见
        unique_attrs = set(attrs.keys()) - set(c1.attributes.keys()) - set(c2.attributes.keys())
        score += min(len(unique_attrs) * 0.05, 0.3)
        
        # 涌现性：有涌现属性
        score += min(len(emergent) * 0.1, 0.4)
        
        return min(score, 1.0)
    
    def _evaluate_coherence(self,
                           c1: Concept,
                           c2: Concept,
                           attrs: Dict) -> float:
        """评估连贯性分数"""
        score = 0.5  # 基础分
        
        # 属性一致性检查
        numeric_attrs = [k for k, v in attrs.items() if isinstance(v, (int, float))]
        
        if len(numeric_attrs) >= 2:
            values = [attrs[k] for k in numeric_attrs]
            variance = np.var(values) if values else 0
            if variance < 10:
                score += 0.3
        
        # 领域兼容性
        compatible_domains = {
            ('physics', 'engineering'),
            ('biology', 'chemistry'),
            ('math', 'logic'),
            ('art', 'design')
        }
        
        if (c1.domain, c2.domain) in compatible_domains or \
           (c2.domain, c1.domain) in compatible_domains:
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_usefulness(self, attrs: Dict) -> float:
        """评估有用性分数"""
        score = 0.5  # 基础分
        
        # 属性数量适中
        if 3 <= len(attrs) <= 10:
            score += 0.2
        
        # 包含关键属性
        useful_keywords = ['efficiency', 'performance', 'capability', 'function', 'utility']
        for key in attrs.keys():
            if any(kw in key.lower() for kw in useful_keywords):
                score += 0.1
                break
        
        return min(score, 1.0)
    
    def generate_creative_variants(self,
                                  base_concept: Concept,
                                  num_variants: int = 5) -> List[BlendedConcept]:
        """生成创造性变体"""
        variants = []
        
        # 创建一些原型概念用于混合
        prototype_attrs = [
            {'efficiency': 9, 'speed': 8, 'cost': 3},
            {'flexibility': 8, 'adaptability': 9, 'complexity': 6},
            {'reliability': 9, 'durability': 8, 'maintenance': 2},
            {'innovation': 9, 'novelty': 8, 'risk': 5},
            {'simplicity': 8, 'elegance': 7, 'usability': 9}
        ]
        
        for i in range(num_variants):
            prototype = Concept(
                concept_id=f"prototype_{i}",
                name=f"Prototype_{i}",
                attributes=prototype_attrs[i % len(prototype_attrs)],
                relations=[],
                abstraction_level=2,
                domain="general"
            )
            
            variant = self.blend_concepts(base_concept, prototype, 'fusion')
            variants.append(variant)
        
        return variants
    
    def get_top_creative_blends(self, top_n: int = 5) -> List[BlendedConcept]:
        """获取最有创造性的混合概念"""
        sorted_blends = sorted(
            self.blended_concepts,
            key=lambda b: b.overall_creativity(),
            reverse=True
        )
        return sorted_blends[:top_n]


# 统一的阶段 11 主引擎
class ConceptAbstractionEngine:
    """
    概念抽象与零样本泛化引擎
    
    整合元模式识别、类比推理和概念组合功能，
    提供统一的概念抽象接口。
    """
    
    def __init__(self):
        self.pattern_recognizer = MetaPatternRecognizer()
        self.analogy_engine = AnalogyEngine()
        self.concept_blender = ConceptBlender()
        self.concept_registry: Dict[str, Concept] = {}
        
    def register_concept(self, concept: Concept) -> None:
        """注册概念"""
        self.concept_registry[concept.concept_id] = concept
        
    def abstract_from_cases(self,
                           cases: List[Dict[str, Any]],
                           domains: List[str]) -> List[AbstractPattern]:
        """从多个案例中抽象模式"""
        patterns = []
        
        for i, case in enumerate(cases):
            domain = domains[i % len(domains)]
            
            # 尝试不同类型的模式
            for pattern_type in PatternType:
                pattern = self.pattern_recognizer.extract_pattern(
                    case, domain, pattern_type
                )
                patterns.append(pattern)
        
        return patterns
    
    def find_cross_domain_analogies(self,
                                   domain1: str,
                                   domain2: str) -> Dict[str, Any]:
        """发现跨领域类比"""
        
        # 查找同构模式
        isomorphisms = self.pattern_recognizer.find_isomorphic_patterns(
            domain1, domain2
        )
        
        if not isomorphisms:
            return {'analogies': [], 'confidence': 0.0}
        
        # 为每个同构对创建详细类比
        analogies = []
        for p1_id, p2_id, similarity in isomorphisms:
            p1 = self.pattern_recognizer.patterns[p1_id]
            p2 = self.pattern_recognizer.patterns[p2_id]
            
            analogy = self.analogy_engine.create_analogy(
                p1.structure,
                p2.structure,
                p1
            )
            
            analogies.append({
                'pattern_pair': (p1_id, p2_id),
                'similarity': similarity,
                'analogy_details': analogy
            })
        
        return {
            'analogies': analogies,
            'confidence': sum(a['similarity'] for a in analogies) / len(analogies)
        }
    
    def perform_zero_shot_transfer(self,
                                  source_problem: Dict,
                                  target_problem: Dict,
                                  source_solution: Any) -> Dict[str, Any]:
        """执行零样本迁移"""
        
        result = self.analogy_engine.zero_shot_transfer(
            source_problem,
            target_problem,
            source_solution
        )
        
        return {
            'success': result is not None,
            'result': result,
            'source_problem': source_problem,
            'target_problem': target_problem
        }
    
    def create_creative_concept(self,
                               concept_ids: List[str],
                               blend_type: str = 'fusion') -> Optional[BlendedConcept]:
        """创建创造性概念"""
        
        if len(concept_ids) < 2:
            return None
        
        concepts = [self.concept_registry[cid] for cid in concept_ids if cid in self.concept_registry]
        
        if len(concepts) < 2:
            return None
        
        # 两两混合
        blended = self.concept_blender.blend_concepts(
            concepts[0],
            concepts[1],
            blend_type
        )
        
        # 如果有更多概念，继续混合
        for i in range(2, len(concepts)):
            blended = self.concept_blender.blend_concepts(
                Concept(
                    concept_id=blended.concept_id,
                    name=blended.name,
                    attributes=blended.blended_attributes,
                    relations=[],
                    abstraction_level=4,
                    domain="blended"
                ),
                concepts[i],
                blend_type
            )
        
        return blended
    
    def build_complete_hierarchy(self) -> ConceptHierarchyGraph:
        """构建完整的概念层级"""
        
        concepts = list(self.concept_registry.values())
        self.pattern_recognizer.build_concept_hierarchy(concepts)
        
        return self.pattern_recognizer.concept_graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'registered_concepts': len(self.concept_registry),
            'recognized_patterns': len(self.pattern_recognizer.patterns),
            'analogies_created': len(self.analogy_engine.analogy_history),
            'concepts_blended': len(self.concept_blender.blended_concepts),
            'avg_pattern_abstraction': np.mean([
                p.abstraction_level for p in self.pattern_recognizer.patterns.values()
            ]) if self.pattern_recognizer.patterns else 0.0
        }


# 导出主要类和函数
__all__ = [
    'PatternType',
    'AbstractPattern',
    'Concept',
    'ConceptHierarchyGraph',
    'MetaPatternRecognizer',
    'AnalogyEngine',
    'ConceptBlender',
    'ConceptAbstractionEngine',
    'Mapping',
    'BlendedConcept'
]
