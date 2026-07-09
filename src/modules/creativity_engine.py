"""
阶段 13: 概念组合创造力模块

实现创造性思维的核心机制：
1. 概念组合引擎 - 将不同概念进行创新性组合
2. 新颖性评估器 - 评估创意的新颖程度
3. 实用性筛选器 - 筛选具有实用价值的创意
4. 创意生成器 - 生成完整的创意方案
5. 创造力评估系统 - 综合评估创造力水平

核心算法：
- 概念空间探索算法
- 远距离联想机制
- 约束满足优化
- 创意演化算法
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional, Any
from enum import Enum
import random
import math
from collections import defaultdict
import heapq


class CreativityType(Enum):
    """创造力类型"""
    COMBINATORIAL = "combinatorial"  # 组合式创造
    EXPLORATORY = "exploratory"  # 探索式创造
    TRANSFORMATIONAL = "transformational"  # 转换式创造
    ANALOGICAL = "analogical"  # 类比式创造
    EMERGENT = "emergent"  # 涌现式创造


class NoveltyLevel(Enum):
    """新颖性等级"""
    ORDINARY = 1  # 普通
    UNCOMMON = 2  # 不常见
    NOVEL = 3  # 新颖
    INNOVATIVE = 4  # 创新
    GROUNDBREAKING = 5  # 突破性


@dataclass
class Concept:
    """概念表示"""
    name: str
    category: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    relations: List[Tuple[str, str]] = field(default_factory=list)  # (relation_type, target)
    constraints: List[str] = field(default_factory=list)
    activation_level: float = 0.5  # 激活程度 0-1
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if isinstance(other, Concept):
            return self.name == other.name
        return False


@dataclass
class CreativeIdea:
    """创意想法"""
    id: str
    title: str
    description: str
    combined_concepts: List[Concept]
    creativity_type: CreativityType
    novelty_score: float  # 0-1
    utility_score: float  # 0-1
    feasibility_score: float  # 0-1
    overall_creativity_score: float  # 0-1
    emergence_properties: List[str] = field(default_factory=list)
    potential_applications: List[str] = field(default_factory=list)
    constraints_violated: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'combined_concepts': [c.name for c in self.combined_concepts],
            'creativity_type': self.creativity_type.value,
            'novelty_score': self.novelty_score,
            'utility_score': self.utility_score,
            'feasibility_score': self.feasibility_score,
            'overall_creativity_score': self.overall_creativity_score,
            'emergence_properties': self.emergence_properties,
            'potential_applications': self.potential_applications
        }


@dataclass
class ConceptSpace:
    """概念空间"""
    concepts: Dict[str, Concept] = field(default_factory=dict)
    semantic_distances: Dict[Tuple[str, str], float] = field(default_factory=dict)
    association_strengths: Dict[Tuple[str, str], float] = field(default_factory=dict)
    
    def add_concept(self, concept: Concept):
        """添加概念到概念空间"""
        self.concepts[concept.name] = concept
    
    def get_concept(self, name: str) -> Optional[Concept]:
        """获取概念"""
        return self.concepts.get(name)
    
    def compute_semantic_distance(self, concept1: str, concept2: str) -> float:
        """计算两个概念之间的语义距离（0-1，越大越远）"""
        if (concept1, concept2) in self.semantic_distances:
            return self.semantic_distances[(concept1, concept2)]
        
        c1 = self.get_concept(concept1)
        c2 = self.get_concept(concept2)
        
        if not c1 or not c2:
            return 1.0
        
        # 基于类别和属性的相似度计算
        if c1.category == c2.category:
            base_distance = 0.3
        else:
            base_distance = 0.7
        
        # 属性重叠度
        common_attrs = set(c1.attributes.keys()) & set(c2.attributes.keys())
        total_attrs = set(c1.attributes.keys()) | set(c2.attributes.keys())
        
        if total_attrs:
            attr_similarity = len(common_attrs) / len(total_attrs)
        else:
            attr_similarity = 0
        
        distance = base_distance * (1 - attr_similarity * 0.5)
        self.semantic_distances[(concept1, concept2)] = distance
        self.semantic_distances[(concept2, concept1)] = distance
        
        return distance
    
    def compute_association_strength(self, concept1: str, concept2: str) -> float:
        """计算两个概念之间的关联强度（0-1，越大越强）"""
        if (concept1, concept2) in self.association_strengths:
            return self.association_strengths[(concept1, concept2)]
        
        c1 = self.get_concept(concept1)
        c2 = self.get_concept(concept2)
        
        if not c1 or not c2:
            return 0.0
        
        # 基于关系的关联
        relation_count = 0
        for rel_type, target in c1.relations:
            if target == concept2:
                relation_count += 1
        
        for rel_type, target in c2.relations:
            if target == concept1:
                relation_count += 1
        
        # 基于语义距离的关联（距离越远，关联强度越低，但创造性潜力越高）
        semantic_dist = self.compute_semantic_distance(concept1, concept2)
        
        # 综合关联强度
        strength = (relation_count * 0.3 + (1 - semantic_dist) * 0.7)
        strength = min(1.0, max(0.0, strength))
        
        self.association_strengths[(concept1, concept2)] = strength
        self.association_strengths[(concept2, concept1)] = strength
        
        return strength


class ConceptCombiner:
    """概念组合引擎"""
    
    def __init__(self, concept_space: ConceptSpace):
        self.concept_space = concept_space
        self.combination_history: List[Tuple[str, str]] = []
    
    def combine_two_concepts(self, concept1_name: str, concept2_name: str, 
                            combination_type: str = "fusion") -> Optional[CreativeIdea]:
        """组合两个概念"""
        c1 = self.concept_space.get_concept(concept1_name)
        c2 = self.concept_space.get_concept(concept2_name)
        
        if not c1 or not c2:
            return None
        
        # 检查是否已经组合过
        if (concept1_name, concept2_name) in self.combination_history or \
           (concept2_name, concept1_name) in self.combination_history:
            pass  # 允许重复组合，但可以记录
        
        # 根据组合类型生成不同的创意
        if combination_type == "fusion":
            idea = self._fusion_combine(c1, c2)
        elif combination_type == "juxtaposition":
            idea = self._juxtaposition_combine(c1, c2)
        elif combination_type == "modification":
            idea = self._modification_combine(c1, c2)
        else:
            idea = self._fusion_combine(c1, c2)
        
        if idea:
            self.combination_history.append((concept1_name, concept2_name))
        
        return idea
    
    def _fusion_combine(self, c1: Concept, c2: Concept) -> CreativeIdea:
        """融合式组合：合并两个概念的核心特征"""
        merged_attrs = {**c1.attributes, **c2.attributes}
        
        # 处理冲突属性
        for key in set(c1.attributes.keys()) & set(c2.attributes.keys()):
            if c1.attributes[key] != c2.attributes[key]:
                # 创建混合值
                merged_attrs[key] = f"{c1.attributes[key]}-{c2.attributes[key]}"
        
        merged_relations = list(set(c1.relations + c2.relations))
        
        # 生成涌现属性
        emergence_props = self._generate_emergence_properties(c1, c2, "fusion")
        
        idea_id = f"fusion_{c1.name}_{c2.name}"
        title = f"{c1.name}-{c2.name} Fusion"
        description = f"A creative fusion of {c1.name} and {c2.name}, combining their core features."
        
        return CreativeIdea(
            id=idea_id,
            title=title,
            description=description,
            combined_concepts=[c1, c2],
            creativity_type=CreativityType.COMBINATORIAL,
            novelty_score=self._calculate_novelty(c1, c2),
            utility_score=self._calculate_utility(c1, c2, merged_attrs),
            feasibility_score=self._calculate_feasibility(c1, c2, merged_attrs),
            overall_creativity_score=0.0,  # Will be calculated later
            emergence_properties=emergence_props
        )
    
    def _juxtaposition_combine(self, c1: Concept, c2: Concept) -> CreativeIdea:
        """并置式组合：将两个概念放在一起产生新意义"""
        emergence_props = self._generate_emergence_properties(c1, c2, "juxtaposition")
        
        idea_id = f"juxta_{c1.name}_{c2.name}"
        title = f"{c1.name} meets {c2.name}"
        description = f"An innovative juxtaposition of {c1.name} with {c2.name}, creating new contextual meaning."
        
        return CreativeIdea(
            id=idea_id,
            title=title,
            description=description,
            combined_concepts=[c1, c2],
            creativity_type=CreativityType.EXPLORATORY,
            novelty_score=self._calculate_novelty(c1, c2, bonus=0.2),
            utility_score=self._calculate_utility(c1, c2, c1.attributes),
            feasibility_score=self._calculate_feasibility(c1, c2, c1.attributes),
            overall_creativity_score=0.0,
            emergence_properties=emergence_props
        )
    
    def _modification_combine(self, c1: Concept, c2: Concept) -> CreativeIdea:
        """修改式组合：用一个概念修改另一个概念"""
        modified_attrs = c1.attributes.copy()
        
        # 用 c2 的属性修改 c1
        for key, value in c2.attributes.items():
            if key in modified_attrs:
                modified_attrs[key] = value
            else:
                modified_attrs[key] = value
        
        emergence_props = self._generate_emergence_properties(c1, c2, "modification")
        
        idea_id = f"modify_{c1.name}_by_{c2.name}"
        title = f"{c2.name}-modified {c1.name}"
        description = f"{c1.name} modified by incorporating characteristics of {c2.name}."
        
        return CreativeIdea(
            id=idea_id,
            title=title,
            description=description,
            combined_concepts=[c1, c2],
            creativity_type=CreativityType.TRANSFORMATIONAL,
            novelty_score=self._calculate_novelty(c1, c2, bonus=0.15),
            utility_score=self._calculate_utility(c1, c2, modified_attrs),
            feasibility_score=self._calculate_feasibility(c1, c2, modified_attrs),
            overall_creativity_score=0.0,
            emergence_properties=emergence_props
        )
    
    def _generate_emergence_properties(self, c1: Concept, c2: Concept, 
                                       combo_type: str) -> List[str]:
        """生成涌现属性"""
        emergence = []
        
        # 基于类别组合生成涌现属性
        categories = {c1.category, c2.category}
        
        if 'technology' in categories and 'nature' in categories:
            emergence.append("bio-inspired design")
            emergence.append("sustainable innovation")
        
        if 'art' in categories and 'science' in categories:
            emergence.append("aesthetic functionality")
            emergence.append("visualized data")
        
        if 'communication' in categories and 'transportation' in categories:
            emergence.append("mobile connectivity")
            emergence.append("distributed interaction")
        
        # 基于组合类型
        if combo_type == "fusion":
            emergence.append("hybrid capabilities")
        elif combo_type == "juxtaposition":
            emergence.append("contextual synergy")
        elif combo_type == "modification":
            emergence.append("enhanced properties")
        
        # 随机生成一些额外的涌现属性
        possible_props = [
            "unexpected efficiency",
            "novel user experience",
            "emergent behavior",
            "cross-domain applicability",
            "scalable solution"
        ]
        
        additional = random.sample(possible_props, min(2, len(possible_props)))
        emergence.extend(additional)
        
        return list(set(emergence))
    
    def _calculate_novelty(self, c1: Concept, c2: Concept, bonus: float = 0.0) -> float:
        """计算新颖性分数"""
        # 语义距离越远，新颖性越高
        semantic_dist = self.concept_space.compute_semantic_distance(c1.name, c2.name)
        
        # 关联强度越弱，新颖性越高（远距离联想）
        assoc_strength = self.concept_space.compute_association_strength(c1.name, c2.name)
        
        novelty = semantic_dist * 0.6 + (1 - assoc_strength) * 0.4 + bonus
        return min(1.0, max(0.0, novelty))
    
    def _calculate_utility(self, c1: Concept, c2: Concept, 
                          combined_attrs: Dict) -> float:
        """计算实用性分数"""
        # 基于属性数量和多样性
        attr_count_score = min(1.0, len(combined_attrs) / 10.0)
        
        # 基于约束满足
        constraint_score = 1.0
        total_constraints = len(c1.constraints) + len(c2.constraints)
        if total_constraints > 0:
            # 简化：假设部分约束被满足
            constraint_score = 0.7 + random.random() * 0.3
        
        # 基于类别互补性
        complement_bonus = 0.0
        complementary_pairs = [
            ('hardware', 'software'),
            ('input', 'output'),
            ('storage', 'processing'),
            ('creation', 'distribution')
        ]
        for pair in complementary_pairs:
            if (c1.category in pair and c2.category in pair and c1.category != c2.category):
                complement_bonus = 0.2
                break
        
        utility = (attr_count_score * 0.4 + constraint_score * 0.4 + complement_bonus * 0.2)
        return min(1.0, max(0.0, utility))
    
    def _calculate_feasibility(self, c1: Concept, c2: Concept, 
                              combined_attrs: Dict) -> float:
        """计算可行性分数"""
        # 基于概念本身的可行性
        base_feasibility = (c1.activation_level + c2.activation_level) / 2
        
        # 基于技术成熟度（简化：使用属性数量作为代理）
        tech_maturity = min(1.0, len(combined_attrs) / 15.0)
        
        # 基于资源需求（简化：随机因素）
        resource_factor = 0.6 + random.random() * 0.4
        
        feasibility = base_feasibility * 0.4 + tech_maturity * 0.3 + resource_factor * 0.3
        return min(1.0, max(0.0, feasibility))


class NoveltyEvaluator:
    """新颖性评估器"""
    
    def __init__(self, concept_space: ConceptSpace, known_ideas: List[CreativeIdea] = None):
        self.concept_space = concept_space
        self.known_ideas = known_ideas or []
    
    def evaluate_novelty(self, idea: CreativeIdea) -> Tuple[float, NoveltyLevel]:
        """评估创意的新颖性"""
        # 与已知创意的相似度
        similarity_to_known = self._compute_similarity_to_known(idea)
        
        # 概念组合的罕见性
        combination_rarity = self._compute_combination_rarity(idea)
        
        # 涌现属性的独特性
        emergence_uniqueness = self._compute_emergence_uniqueness(idea)
        
        # 综合新颖性分数
        novelty_score = (
            (1 - similarity_to_known) * 0.4 +
            combination_rarity * 0.35 +
            emergence_uniqueness * 0.25
        )
        
        # 确定新颖性等级
        if novelty_score >= 0.9:
            level = NoveltyLevel.GROUNDBREAKING
        elif novelty_score >= 0.75:
            level = NoveltyLevel.INNOVATIVE
        elif novelty_score >= 0.5:
            level = NoveltyLevel.NOVEL
        elif novelty_score >= 0.3:
            level = NoveltyLevel.UNCOMMON
        else:
            level = NoveltyLevel.ORDINARY
        
        return novelty_score, level
    
    def _compute_similarity_to_known(self, idea: CreativeIdea) -> float:
        """计算与已知创意的相似度"""
        if not self.known_ideas:
            return 0.0
        
        max_similarity = 0.0
        idea_concepts = set(c.name for c in idea.combined_concepts)
        
        for known in self.known_ideas:
            known_concepts = set(c.name for c in known.combined_concepts)
            
            # Jaccard 相似度
            intersection = len(idea_concepts & known_concepts)
            union = len(idea_concepts | known_concepts)
            
            if union > 0:
                similarity = intersection / union
                max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _compute_combination_rarity(self, idea: CreativeIdea) -> float:
        """计算概念组合的罕见性"""
        if len(idea.combined_concepts) < 2:
            return 0.5
        
        # 计算所有概念对之间的平均关联强度
        total_rarity = 0.0
        count = 0
        
        for i, c1 in enumerate(idea.combined_concepts):
            for c2 in idea.combined_concepts[i+1:]:
                assoc = self.concept_space.compute_association_strength(c1.name, c2.name)
                rarity = 1 - assoc  # 关联越弱，组合越罕见
                total_rarity += rarity
                count += 1
        
        if count > 0:
            return total_rarity / count
        return 0.5
    
    def _compute_emergence_uniqueness(self, idea: CreativeIdea) -> float:
        """计算涌现属性的独特性"""
        if not idea.emergence_properties:
            return 0.3
        
        # 统计所有已知创意中的涌现属性
        all_known_props = set()
        for known in self.known_ideas:
            all_known_props.update(known.emergence_properties)
        
        # 计算独特属性比例
        unique_props = set(idea.emergence_properties) - all_known_props
        uniqueness_ratio = len(unique_props) / len(idea.emergence_properties)
        
        return uniqueness_ratio


class UtilityFilter:
    """实用性筛选器"""
    
    def __init__(self, domain_constraints: List[str] = None):
        self.domain_constraints = domain_constraints or []
        self.evaluation_criteria = {
            'market_potential': 0.25,
            'technical_feasibility': 0.25,
            'user_value': 0.25,
            'resource_efficiency': 0.25
        }
    
    def filter_ideas(self, ideas: List[CreativeIdea], 
                    min_utility: float = 0.5,
                    min_feasibility: float = 0.4) -> List[CreativeIdea]:
        """筛选出具有实用价值的创意"""
        filtered = []
        
        for idea in ideas:
            # 检查基本阈值
            if idea.utility_score < min_utility:
                continue
            if idea.feasibility_score < min_feasibility:
                continue
            
            # 检查领域约束
            if not self._check_domain_constraints(idea):
                continue
            
            # 重新计算综合实用性分数
            idea.utility_score = self._recalculate_utility(idea)
            
            filtered.append(idea)
        
        # 按实用性分数排序
        filtered.sort(key=lambda x: x.utility_score, reverse=True)
        
        return filtered
    
    def _check_domain_constraints(self, idea: CreativeIdea) -> bool:
        """检查领域约束"""
        if not self.domain_constraints:
            return True
        
        # 简化：检查是否有严重违反约束的情况
        for constraint in self.domain_constraints:
            if constraint in idea.constraints_violated:
                return False
        
        return True
    
    def _recalculate_utility(self, idea: CreativeIdea) -> float:
        """重新计算实用性分数"""
        # 基于多个维度重新评估
        market_score = self._evaluate_market_potential(idea)
        technical_score = idea.feasibility_score
        user_value_score = self._evaluate_user_value(idea)
        resource_score = self._evaluate_resource_efficiency(idea)
        
        utility = (
            market_score * self.evaluation_criteria['market_potential'] +
            technical_score * self.evaluation_criteria['technical_feasibility'] +
            user_value_score * self.evaluation_criteria['user_value'] +
            resource_score * self.evaluation_criteria['resource_efficiency']
        )
        
        return min(1.0, max(0.0, utility))
    
    def _evaluate_market_potential(self, idea: CreativeIdea) -> float:
        """评估市场潜力"""
        # 基于应用场景数量
        app_count_score = min(1.0, len(idea.potential_applications) / 5.0)
        
        # 基于涌现属性带来的差异化
        emergence_score = min(1.0, len(idea.emergence_properties) / 4.0)
        
        return (app_count_score * 0.5 + emergence_score * 0.5)
    
    def _evaluate_user_value(self, idea: CreativeIdea) -> float:
        """评估用户价值"""
        # 基于解决的问题数量（简化：使用涌现属性作为代理）
        problem_solving_score = min(1.0, len(idea.emergence_properties) / 3.0)
        
        # 基于新颖性带来的吸引力
        novelty_bonus = idea.novelty_score * 0.3
        
        return min(1.0, problem_solving_score + novelty_bonus)
    
    def _evaluate_resource_efficiency(self, idea: CreativeIdea) -> float:
        """评估资源效率"""
        # 简化：基于可行性分数的函数
        base_efficiency = idea.feasibility_score
        
        # 概念越少，通常资源需求越低
        concept_penalty = (len(idea.combined_concepts) - 2) * 0.05
        
        return max(0.0, base_efficiency - concept_penalty)


class CreativityGenerator:
    """创意生成器"""
    
    def __init__(self, concept_space: ConceptSpace):
        self.concept_space = concept_space
        self.combiner = ConceptCombiner(concept_space)
        self.novelty_evaluator = NoveltyEvaluator(concept_space)
        self.utility_filter = UtilityFilter()
        self.generated_ideas: List[CreativeIdea] = []
    
    def generate_ideas(self, seed_concepts: List[str] = None,
                      num_ideas: int = 10,
                      creativity_types: List[CreativityType] = None,
                      strategy: str = "divergent") -> List[CreativeIdea]:
        """生成创意"""
        ideas = []
        
        if strategy == "divergent":
            ideas = self._divergent_generation(seed_concepts, num_ideas, creativity_types)
        elif strategy == "focused":
            ideas = self._focused_generation(seed_concepts, num_ideas, creativity_types)
        elif strategy == "evolutionary":
            ideas = self._evolutionary_generation(seed_concepts, num_ideas, creativity_types)
        else:
            ideas = self._divergent_generation(seed_concepts, num_ideas, creativity_types)
        
        # 评估每个创意的新颖性
        for idea in ideas:
            novelty_score, novelty_level = self.novelty_evaluator.evaluate_novelty(idea)
            idea.novelty_score = novelty_score
            
            # 计算综合创造力分数
            idea.overall_creativity_score = self._calculate_overall_score(idea)
        
        # 筛选高实用性创意
        filtered_ideas = self.utility_filter.filter_ideas(ideas)
        
        self.generated_ideas.extend(filtered_ideas)
        
        # 更新新颖性评估器的已知创意库
        self.novelty_evaluator.known_ideas = self.generated_ideas
        
        return filtered_ideas
    
    def _divergent_generation(self, seed_concepts: List[str], 
                             num_ideas: int,
                             creativity_types: List[CreativityType]) -> List[CreativeIdea]:
        """发散式生成：广泛探索概念空间"""
        ideas = []
        
        # 检查概念空间是否为空
        if not self.concept_space.concepts:
            return ideas
        
        # 如果没有种子概念，随机选择
        if not seed_concepts:
            available_concepts = list(self.concept_space.concepts.keys())
            if not available_concepts:
                return ideas
            seed_concepts = random.sample(available_concepts, 
                                         min(5, len(available_concepts)))
        
        available_types = creativity_types or list(CreativityType)
        combination_types = ["fusion", "juxtaposition", "modification"]
        
        attempts = 0
        max_attempts = num_ideas * 5
        
        while len(ideas) < num_ideas and attempts < max_attempts:
            attempts += 1
            
            # 随机选择两个概念
            c1_name = random.choice(seed_concepts)
            c2_name = random.choice(list(self.concept_space.concepts.keys()))
            
            if c1_name == c2_name:
                continue
            
            # 随机选择组合类型和创造力类型
            combo_type = random.choice(combination_types)
            creativity_type = random.choice(available_types)
            
            idea = self.combiner.combine_two_concepts(c1_name, c2_name, combo_type)
            
            if idea:
                idea.creativity_type = creativity_type
                ideas.append(idea)
        
        return ideas
    
    def _focused_generation(self, seed_concepts: List[str],
                           num_ideas: int,
                           creativity_types: List[CreativityType]) -> List[CreativeIdea]:
        """聚焦式生成：围绕种子概念深入探索"""
        ideas = []
        
        if not seed_concepts:
            return ideas
        
        available_types = creativity_types or [CreativityType.COMBINATORIAL]
        combination_types = ["fusion", "modification"]
        
        for seed in seed_concepts[:min(3, len(seed_concepts))]:
            # 找到与种子概念相关的概念
            related_concepts = self._find_related_concepts(seed, top_k=5)
            
            for related in related_concepts:
                for combo_type in combination_types:
                    idea = self.combiner.combine_two_concepts(seed, related, combo_type)
                    
                    if idea and len(ideas) < num_ideas:
                        idea.creativity_type = random.choice(available_types)
                        ideas.append(idea)
        
        return ideas
    
    def _evolutionary_generation(self, seed_concepts: List[str],
                                num_ideas: int,
                                creativity_types: List[CreativityType]) -> List[CreativeIdea]:
        """演化式生成：通过变异和重组产生新创意"""
        ideas = []
        
        # 初始种群
        initial_ideas = self._divergent_generation(seed_concepts, num_ideas // 2, creativity_types)
        ideas.extend(initial_ideas)
        
        # 演化迭代
        generations = 3
        for gen in range(generations):
            if len(ideas) >= num_ideas:
                break
            
            # 选择优秀的创意进行变异
            top_ideas = sorted(ideas, key=lambda x: x.overall_creativity_score, reverse=True)[:3]
            
            for parent in top_ideas:
                # 变异：替换其中一个概念
                if len(parent.combined_concepts) >= 2:
                    for i, concept in enumerate(parent.combined_concepts):
                        alternatives = self._find_similar_concepts(concept.name, top_k=2)
                        
                        for alt_name in alternatives:
                            if alt_name != concept.name:
                                new_concepts = parent.combined_concepts.copy()
                                new_concepts[i] = self.concept_space.get_concept(alt_name)
                                
                                # 创建变异后的创意
                                mutated_idea = CreativeIdea(
                                    id=f"mutant_{parent.id}_{gen}",
                                    title=f"Mutant: {parent.title}",
                                    description=f"Evolved from: {parent.description}",
                                    combined_concepts=new_concepts,
                                    creativity_type=CreativityType.TRANSFORMATIONAL,
                                    novelty_score=parent.novelty_score * 1.1,  # 略微提升新颖性
                                    utility_score=parent.utility_score * 0.95,  # 略微降低实用性
                                    feasibility_score=parent.feasibility_score * 0.9,
                                    overall_creativity_score=0.0,
                                    emergence_properties=parent.emergence_properties.copy(),
                                    potential_applications=parent.potential_applications.copy()
                                )
                                
                                ideas.append(mutated_idea)
                                
                                if len(ideas) >= num_ideas:
                                    break
                        
                        if len(ideas) >= num_ideas:
                            break
                
                if len(ideas) >= num_ideas:
                    break
        
        return ideas[:num_ideas]
    
    def _find_related_concepts(self, concept_name: str, top_k: int = 5) -> List[str]:
        """查找相关概念"""
        concept = self.concept_space.get_concept(concept_name)
        if not concept:
            return []
        
        # 基于关系和类别查找
        related = []
        
        # 直接相关的概念
        for rel_type, target in concept.relations:
            if target in self.concept_space.concepts:
                related.append((target, 0.9))
        
        # 同类别的概念
        for name, c in self.concept_space.concepts.items():
            if name != concept_name and c.category == concept.category:
                related.append((name, 0.6))
        
        # 排序并返回
        related.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in related[:top_k]]
    
    def _find_similar_concepts(self, concept_name: str, top_k: int = 3) -> List[str]:
        """查找相似概念"""
        concept = self.concept_space.get_concept(concept_name)
        if not concept:
            return []
        
        similarities = []
        
        for name, c in self.concept_space.concepts.items():
            if name == concept_name:
                continue
            
            # 语义距离越小越相似
            distance = self.concept_space.compute_semantic_distance(concept_name, name)
            similarity = 1 - distance
            
            similarities.append((name, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in similarities[:top_k]]
    
    def _calculate_overall_score(self, idea: CreativeIdea) -> float:
        """计算综合创造力分数"""
        # 综合新颖性、实用性和可行性
        weights = {
            'novelty': 0.4,
            'utility': 0.35,
            'feasibility': 0.25
        }
        
        score = (
            idea.novelty_score * weights['novelty'] +
            idea.utility_score * weights['utility'] +
            idea.feasibility_score * weights['feasibility']
        )
        
        # 涌现属性奖励
        emergence_bonus = min(0.1, len(idea.emergence_properties) * 0.02)
        
        return min(1.0, max(0.0, score + emergence_bonus))


class CreativityAssessmentSystem:
    """创造力评估系统"""
    
    def __init__(self):
        self.assessment_history: List[Dict] = []
    
    def assess_creativity(self, ideas: List[CreativeIdea], 
                         context: str = "") -> Dict:
        """评估整体创造力水平"""
        if not ideas:
            return {
                'overall_score': 0.0,
                'novelty_avg': 0.0,
                'utility_avg': 0.0,
                'diversity_score': 0.0,
                'creativity_distribution': {},
                'recommendations': [],
                'total_ideas': 0,
                'high_creativity_count': 0,
                'context': context
            }
        
        # 计算各项指标
        novelty_scores = [i.novelty_score for i in ideas]
        utility_scores = [i.utility_score for i in ideas]
        creativity_scores = [i.overall_creativity_score for i in ideas]
        
        novelty_avg = sum(novelty_scores) / len(novelty_scores)
        utility_avg = sum(utility_scores) / len(utility_scores)
        creativity_avg = sum(creativity_scores) / len(creativity_scores)
        
        # 计算多样性分数
        diversity_score = self._calculate_diversity(ideas)
        
        # 创造力类型分布
        type_distribution = defaultdict(int)
        for idea in ideas:
            type_distribution[idea.creativity_type.value] += 1
        
        # 生成建议
        recommendations = self._generate_recommendations(
            novelty_avg, utility_avg, diversity_score, type_distribution
        )
        
        assessment = {
            'overall_score': creativity_avg,
            'novelty_avg': novelty_avg,
            'utility_avg': utility_avg,
            'diversity_score': diversity_score,
            'creativity_distribution': dict(type_distribution),
            'recommendations': recommendations,
            'total_ideas': len(ideas),
            'high_creativity_count': len([i for i in ideas if i.overall_creativity_score >= 0.7]),
            'context': context
        }
        
        self.assessment_history.append(assessment)
        
        return assessment
    
    def _calculate_diversity(self, ideas: List[CreativeIdea]) -> float:
        """计算创意多样性"""
        if len(ideas) < 2:
            return 0.0
        
        # 基于概念组合的多样性
        concept_sets = [frozenset(c.name for c in idea.combined_concepts) 
                       for idea in ideas]
        
        unique_sets = len(set(concept_sets))
        diversity = unique_sets / len(ideas)
        
        # 基于创造力类型的多样性
        types = [idea.creativity_type for idea in ideas]
        unique_types = len(set(types))
        type_diversity = unique_types / len(CreativityType)
        
        return (diversity * 0.6 + type_diversity * 0.4)
    
    def _generate_recommendations(self, novelty_avg: float, utility_avg: float,
                                 diversity_score: float,
                                 type_distribution: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if novelty_avg < 0.5:
            recommendations.append(
                "Consider exploring more distant concept combinations to increase novelty."
            )
        
        if utility_avg < 0.5:
            recommendations.append(
                "Focus on practical applications and feasibility to improve utility."
            )
        
        if diversity_score < 0.5:
            recommendations.append(
                "Diversify your concept exploration strategy to generate more varied ideas."
            )
        
        # 检查创造力类型平衡
        if type_distribution:
            dominant_type = max(type_distribution, key=type_distribution.get)
            dominant_ratio = type_distribution[dominant_type] / sum(type_distribution.values())
            
            if dominant_ratio > 0.6:
                recommendations.append(
                    f"Try to balance different creativity types. Currently dominated by {dominant_type}."
                )
        
        if not recommendations:
            recommendations.append(
                "Excellent creative performance! Continue exploring and refining ideas."
            )
        
        return recommendations


# 主类：概念组合创造力引擎
class ConceptCombinationCreativityEngine:
    """
    概念组合创造力引擎
    
    整合所有组件，提供完整的创造力生成和评估功能
    """
    
    def __init__(self):
        self.concept_space = ConceptSpace()
        self.generator = CreativityGenerator(self.concept_space)
        self.assessment_system = CreativityAssessmentSystem()
    
    def initialize_concept_space(self, concepts: List[Concept]):
        """初始化概念空间"""
        for concept in concepts:
            self.concept_space.add_concept(concept)
    
    def generate_creative_ideas(self, 
                               seed_concepts: List[str] = None,
                               num_ideas: int = 10,
                               creativity_types: List[CreativityType] = None,
                               strategy: str = "divergent") -> List[CreativeIdea]:
        """生成创意想法"""
        return self.generator.generate_ideas(
            seed_concepts=seed_concepts,
            num_ideas=num_ideas,
            creativity_types=creativity_types,
            strategy=strategy
        )
    
    def assess_creativity(self, ideas: List[CreativeIdea], 
                         context: str = "") -> Dict:
        """评估创造力"""
        return self.assessment_system.assess_creativity(ideas, context)
    
    def get_top_ideas(self, ideas: List[CreativeIdea], 
                     top_k: int = 5,
                     criterion: str = "overall") -> List[CreativeIdea]:
        """获取顶级创意"""
        if criterion == "overall":
            sorted_ideas = sorted(ideas, key=lambda x: x.overall_creativity_score, reverse=True)
        elif criterion == "novelty":
            sorted_ideas = sorted(ideas, key=lambda x: x.novelty_score, reverse=True)
        elif criterion == "utility":
            sorted_ideas = sorted(ideas, key=lambda x: x.utility_score, reverse=True)
        else:
            sorted_ideas = sorted(ideas, key=lambda x: x.overall_creativity_score, reverse=True)
        
        return sorted_ideas[:top_k]
    
    def export_idea_report(self, ideas: List[CreativeIdea], 
                          format: str = "text") -> str:
        """导出创意报告"""
        if format == "text":
            report = "=== Creative Ideas Report ===\n\n"
            
            for i, idea in enumerate(ideas, 1):
                report += f"[{i}] {idea.title}\n"
                report += f"    ID: {idea.id}\n"
                report += f"    Type: {idea.creativity_type.value}\n"
                report += f"    Description: {idea.description}\n"
                report += f"    Concepts: {', '.join(c.name for c in idea.combined_concepts)}\n"
                report += f"    Scores: Novelty={idea.novelty_score:.2f}, "
                report += f"Utility={idea.utility_score:.2f}, "
                report += f"Feasibility={idea.feasibility_score:.2f}, "
                report += f"Overall={idea.overall_creativity_score:.2f}\n"
                
                if idea.emergence_properties:
                    report += f"    Emergent Properties: {', '.join(idea.emergence_properties)}\n"
                
                if idea.potential_applications:
                    report += f"    Applications: {', '.join(idea.potential_applications)}\n"
                
                report += "\n"
            
            return report
        
        elif format == "json":
            import json
            return json.dumps([idea.to_dict() for idea in ideas], indent=2)
        
        return ""
