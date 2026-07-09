"""
阶段 12: 类比推理引擎
模块：类比映射与迁移学习 (Analogy Mapper)

功能：
- 跨领域结构映射
- 类比推理生成
- 知识迁移应用
- 创造性类比发现
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import numpy as np
from enum import Enum


class AnalogyType(Enum):
    """类比类型枚举"""
    STRUCTURAL = "structural"  # 结构类比
    FUNCTIONAL = "functional"  # 功能类比
    RELATIONAL = "relational"  # 关系类比
    ATTRIBUTIONAL = "attributional"  # 属性类比
    CAUSAL = "causal"  # 因果类比
    PROCEDURAL = "procedural"  # 过程类比


@dataclass
class MappingHypothesis:
    """映射假设"""
    source_element: str
    target_element: str
    relation_type: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "source": self.source_element,
            "target": self.target_element,
            "relation": self.relation_type,
            "confidence": self.confidence,
            "evidence": self.evidence
        }


@dataclass
class AnalogyMapping:
    """类比映射结果"""
    source_domain: str
    target_domain: str
    analogy_type: AnalogyType
    mappings: List[MappingHypothesis]
    structural_alignments: List[Tuple[str, str]]  # (source_structure, target_structure)
    transferable_knowledge: List[Dict[str, Any]]
    overall_confidence: float
    creativity_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "analogy_type": self.analogy_type.value,
            "mappings": [m.to_dict() for m in self.mappings],
            "structural_alignments": self.structural_alignments,
            "transferable_knowledge": self.transferable_knowledge,
            "overall_confidence": self.overall_confidence,
            "creativity_score": self.creativity_score,
            "metadata": self.metadata
        }


class StructureAligner:
    """
    结构对齐器
    识别两个领域之间的结构相似性
    """
    
    def __init__(self, similarity_threshold: float = 0.6):
        self.similarity_threshold = similarity_threshold
        self.structure_weights = {
            "hierarchical": 0.3,
            "sequential": 0.2,
            "network": 0.25,
            "cyclical": 0.15,
            "causal": 0.1
        }
    
    def align_structures(
        self,
        source_relations: List[Tuple[str, str, str]],
        target_relations: List[Tuple[str, str, str]]
    ) -> List[Tuple[str, str]]:
        """
        对齐两个领域的结构关系
        
        Args:
            source_relations: 源领域的关系列表 [(source, relation, target), ...]
            target_relations: 目标领域的关系列表
        
        Returns:
            结构对齐列表 [(source_structure, target_structure), ...]
        """
        alignments = []
        
        # 构建关系图
        source_graph = self._build_relation_graph(source_relations)
        target_graph = self._build_relation_graph(target_relations)
        
        # 寻找同构子结构
        for src_rel in source_relations:
            best_match = None
            best_similarity = 0.0
            
            for tgt_rel in target_relations:
                similarity = self._compute_relation_similarity(src_rel, tgt_rel)
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = tgt_rel
            
            if best_match:
                src_structure = f"{src_rel[0]}-{src_rel[1]}-{src_rel[2]}"
                tgt_structure = f"{best_match[0]}-{best_match[1]}-{best_match[2]}"
                alignments.append((src_structure, tgt_structure))
        
        return alignments
    
    def _build_relation_graph(
        self, 
        relations: List[Tuple[str, str, str]]
    ) -> Dict[str, Set[str]]:
        """构建关系图"""
        graph = defaultdict(set)
        for src, rel, tgt in relations:
            graph[src].add(tgt)
            graph[tgt].add(src)  # 无向图
        return dict(graph)
    
    def _compute_relation_similarity(
        self,
        rel1: Tuple[str, str, str],
        rel2: Tuple[str, str, str]
    ) -> float:
        """计算两个关系的相似度"""
        # 关系类型相似度
        type_sim = 1.0 if rel1[1] == rel2[1] else 0.5
        
        # 结构角色相似度（基于连接度）
        role_sim = 0.5  # 默认值
        
        # 综合相似度
        return 0.7 * type_sim + 0.3 * role_sim


class AnalogyGenerator:
    """
    类比生成器
    基于结构映射理论生成类比推理
    """
    
    def __init__(self):
        self.aligner = StructureAligner()
        self.analogy_templates = {
            "part_whole": ("部分是整体的组成", "组件是系统的组成"),
            "cause_effect": ("A 导致 B", "X 导致 Y"),
            "means_end": ("通过 A 实现 B", "通过 X 实现 Y"),
            "similarity": ("A 类似于 B", "X 类似于 Y"),
            "contrast": ("A 不同于 B", "X 不同于 Y")
        }
    
    def generate_analogy(
        self,
        source_domain: str,
        target_domain: str,
        source_relations: List[Tuple[str, str, str]],
        target_relations: List[Tuple[str, str, str]],
        analogy_type: AnalogyType = AnalogyType.STRUCTURAL
    ) -> Optional[AnalogyMapping]:
        """
        生成类比映射
        
        Args:
            source_domain: 源领域名称
            target_domain: 目标领域名称
            source_relations: 源领域关系
            target_relations: 目标领域关系
            analogy_type: 类比类型
        
        Returns:
            AnalogyMapping 对象，如果无法生成则返回 None
        """
        # 结构对齐
        alignments = self.aligner.align_structures(
            source_relations, 
            target_relations
        )
        
        if not alignments:
            return None
        
        # 生成映射假设
        mappings = self._generate_mappings(
            source_relations,
            target_relations,
            alignments
        )
        
        if not mappings:
            return None
        
        # 计算整体置信度
        avg_confidence = sum(m.confidence for m in mappings) / len(mappings)
        
        # 计算创造性分数
        creativity_score = self._compute_creativity(
            source_domain,
            target_domain,
            analogy_type
        )
        
        # 提取可迁移知识
        transferable = self._extract_transferable_knowledge(
            mappings,
            analogy_type
        )
        
        return AnalogyMapping(
            source_domain=source_domain,
            target_domain=target_domain,
            analogy_type=analogy_type,
            mappings=mappings,
            structural_alignments=alignments,
            transferable_knowledge=transferable,
            overall_confidence=avg_confidence,
            creativity_score=creativity_score
        )
    
    def _generate_mappings(
        self,
        source_relations: List[Tuple[str, str, str]],
        target_relations: List[Tuple[str, str, str]],
        alignments: List[Tuple[str, str]]
    ) -> List[MappingHypothesis]:
        """生成元素映射假设"""
        mappings = []
        
        # 从对齐中提取元素映射
        for src_struct, tgt_struct in alignments:
            src_parts = src_struct.split('-')
            tgt_parts = tgt_struct.split('-')
            
            if len(src_parts) >= 3 and len(tgt_parts) >= 3:
                # 映射源元素到目标元素
                mappings.append(MappingHypothesis(
                    source_element=src_parts[0],
                    target_element=tgt_parts[0],
                    relation_type=src_parts[1],
                    confidence=0.8,
                    evidence=[f"结构对齐：{src_struct} ~ {tgt_struct}"]
                ))
                
                mappings.append(MappingHypothesis(
                    source_element=src_parts[2],
                    target_element=tgt_parts[2],
                    relation_type=src_parts[1],
                    confidence=0.75,
                    evidence=[f"结构对齐：{src_struct} ~ {tgt_struct}"]
                ))
        
        return mappings
    
    def _compute_creativity(
        self,
        source_domain: str,
        target_domain: str,
        analogy_type: AnalogyType
    ) -> float:
        """计算类比的创造性分数"""
        # 基于领域距离和类比类型的创造性评估
        domain_distance = self._estimate_domain_distance(
            source_domain, 
            target_domain
        )
        
        type_weight = {
            AnalogyType.STRUCTURAL: 0.7,
            AnalogyType.FUNCTIONAL: 0.8,
            AnalogyType.RELATIONAL: 0.75,
            AnalogyType.ATTRIBUTIONAL: 0.6,
            AnalogyType.CAUSAL: 0.85,
            AnalogyType.PROCEDURAL: 0.7
        }.get(analogy_type, 0.5)
        
        # 创造性 = 领域距离 × 类型权重
        creativity = min(1.0, domain_distance * type_weight)
        return creativity
    
    def _estimate_domain_distance(
        self,
        source: str,
        target: str
    ) -> float:
        """估计两个领域之间的距离（0-1）"""
        # 简化实现：基于字符串相似度
        common_words = set(source) & set(target)
        total_words = set(source) | set(target)
        
        if not total_words:
            return 0.5
        
        similarity = len(common_words) / len(total_words)
        distance = 1.0 - similarity
        
        return min(1.0, max(0.0, distance))
    
    def _extract_transferable_knowledge(
        self,
        mappings: List[MappingHypothesis],
        analogy_type: AnalogyType
    ) -> List[Dict[str, Any]]:
        """提取可迁移的知识"""
        transferable = []
        
        for mapping in mappings:
            knowledge = {
                "principle": f"{mapping.relation_type}关系可从{mapping.source_element}迁移到{mapping.target_element}",
                "confidence": mapping.confidence,
                "type": analogy_type.value,
                "application_context": f"在{mapping.target_element}的上下文中应用{mapping.source_element}的原理"
            }
            transferable.append(knowledge)
        
        return transferable


class KnowledgeTransferEngine:
    """
    知识迁移引擎
    将源领域的知识应用到目标领域
    """
    
    def __init__(self):
        self.transfer_strategies = [
            "direct_mapping",      # 直接映射
            "adaptation",          # 适应性调整
            "generalization",      # 泛化
            "specialization"       # 特化
        ]
    
    def transfer_knowledge(
        self,
        analogy: AnalogyMapping,
        source_knowledge: Dict[str, Any],
        target_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行知识迁移
        
        Args:
            analogy: 类比映射
            source_knowledge: 源领域知识
            target_context: 目标领域上下文
        
        Returns:
            迁移后的知识
        """
        transferred = {}
        
        # 对每个映射假设应用知识迁移
        for mapping in analogy.mappings:
            if mapping.source_element in source_knowledge:
                strategy = self._select_transfer_strategy(
                    mapping,
                    source_knowledge[mapping.source_element],
                    target_context
                )
                
                transferred[mapping.target_element] = self._apply_transfer(
                    source_knowledge[mapping.source_element],
                    mapping,
                    strategy,
                    target_context
                )
        
        return transferred
    
    def _select_transfer_strategy(
        self,
        mapping: MappingHypothesis,
        knowledge: Any,
        context: Dict[str, Any]
    ) -> str:
        """选择最佳迁移策略"""
        # 简化实现：基于置信度选择策略
        if mapping.confidence > 0.9:
            return "direct_mapping"
        elif mapping.confidence > 0.7:
            return "adaptation"
        elif mapping.confidence > 0.5:
            return "generalization"
        else:
            return "specialization"
    
    def _apply_transfer(
        self,
        source_knowledge: Any,
        mapping: MappingHypothesis,
        strategy: str,
        target_context: Dict[str, Any]
    ) -> Any:
        """应用知识迁移"""
        if strategy == "direct_mapping":
            return source_knowledge
        elif strategy == "adaptation":
            # 适应性调整：根据目标上下文微调
            return self._adapt_knowledge(
                source_knowledge, 
                mapping, 
                target_context
            )
        elif strategy == "generalization":
            # 泛化：提取通用原理
            return self._generalize_knowledge(source_knowledge)
        else:  # specialization
            # 特化：应用于具体场景
            return self._specialize_knowledge(
                source_knowledge, 
                target_context
            )
    
    def _adapt_knowledge(
        self,
        knowledge: Any,
        mapping: MappingHypothesis,
        context: Dict[str, Any]
    ) -> Any:
        """适应性调整知识"""
        # 简化实现
        if isinstance(knowledge, dict):
            adapted = knowledge.copy()
            adapted["_adapted_for"] = mapping.target_element
            return adapted
        return knowledge
    
    def _generalize_knowledge(self, knowledge: Any) -> Any:
        """泛化知识"""
        # 简化实现：提取核心原理
        if isinstance(knowledge, dict):
            return {
                "_generalized": True,
                "core_principle": str(knowledge)
            }
        return {"_generalized": True, "core_principle": str(knowledge)}
    
    def _specialize_knowledge(
        self,
        knowledge: Any,
        context: Dict[str, Any]
    ) -> Any:
        """特化知识"""
        # 简化实现：应用具体上下文
        if isinstance(knowledge, dict):
            specialized = knowledge.copy()
            specialized["_context"] = context
            return specialized
        return {"_specialized": True, "value": knowledge, "_context": context}


class AnalogyReasoningEngine:
    """
    类比推理引擎
    整合结构对齐、类比生成和知识迁移
    """
    
    def __init__(self):
        self.generator = AnalogyGenerator()
        self.transfer_engine = KnowledgeTransferEngine()
        self.analogy_history: List[AnalogyMapping] = []
    
    def reason_by_analogy(
        self,
        source_domain: str,
        target_domain: str,
        source_structure: Dict[str, Any],
        target_structure: Dict[str, Any],
        analogy_type: AnalogyType = AnalogyType.STRUCTURAL
    ) -> Optional[Dict[str, Any]]:
        """
        执行类比推理
        
        Args:
            source_domain: 源领域
            target_domain: 目标领域
            source_structure: 源领域结构（包含 elements 和 relations）
            target_structure: 目标领域结构
            analogy_type: 类比类型
        
        Returns:
            推理结果字典
        """
        # 提取关系
        source_relations = source_structure.get("relations", [])
        target_relations = target_structure.get("relations", [])
        
        # 生成类比映射
        analogy = self.generator.generate_analogy(
            source_domain,
            target_domain,
            source_relations,
            target_relations,
            analogy_type
        )
        
        if not analogy:
            return None
        
        # 记录历史
        self.analogy_history.append(analogy)
        
        # 执行知识迁移
        source_knowledge = source_structure.get("knowledge", {})
        target_context = target_structure.get("context", {})
        
        transferred_knowledge = self.transfer_engine.transfer_knowledge(
            analogy,
            source_knowledge,
            target_context
        )
        
        # 生成推理结论
        conclusion = self._generate_conclusion(
            analogy,
            transferred_knowledge
        )
        
        return {
            "analogy": analogy.to_dict(),
            "transferred_knowledge": transferred_knowledge,
            "conclusion": conclusion,
            "insights": self._extract_insights(analogy)
        }
    
    def _generate_conclusion(
        self,
        analogy: AnalogyMapping,
        transferred_knowledge: Dict[str, Any]
    ) -> str:
        """生成推理结论"""
        source = analogy.source_domain
        target = analogy.target_domain
        confidence = analogy.overall_confidence
        
        num_mappings = len(analogy.mappings)
        
        conclusion = (
            f"通过{analogy.analogy_type.value}类比，"
            f"从'{source}'到'{target}'建立了{num_mappings}个映射关系。"
            f"推理置信度：{confidence:.2f}。"
            f"创造性分数：{analogy.creativity_score:.2f}。"
        )
        
        if transferred_knowledge:
            conclusion += f"成功迁移{len(transferred_knowledge)}项知识。"
        
        return conclusion
    
    def _extract_insights(
        self,
        analogy: AnalogyMapping
    ) -> List[str]:
        """提取洞察"""
        insights = []
        
        # 高创造性类比产生更多洞察
        if analogy.creativity_score > 0.7:
            insights.append(
                f"发现跨领域创新连接：{analogy.source_domain} ↔ {analogy.target_domain}"
            )
        
        # 高置信度映射提供可靠洞见
        high_conf_mappings = [
            m for m in analogy.mappings if m.confidence > 0.8
        ]
        if high_conf_mappings:
            insights.append(
                f"识别{len(high_conf_mappings)}个高置信度映射关系"
            )
        
        # 结构对齐洞察
        if len(analogy.structural_alignments) > 2:
            insights.append(
                "发现深层结构相似性"
            )
        
        return insights
    
    def find_creative_analogies(
        self,
        domains: List[Tuple[str, Dict[str, Any]]],
        min_creativity: float = 0.6
    ) -> List[AnalogyMapping]:
        """
        在多个领域间寻找创造性类比
        
        Args:
            domains: 领域列表 [(domain_name, structure), ...]
            min_creativity: 最小创造性分数阈值
        
        Returns:
            创造性类比列表
        """
        creative_analogies = []
        
        # 两两比较所有领域
        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                source_name, source_struct = domains[i]
                target_name, target_struct = domains[j]
                
                # 尝试不同类型的类比
                for analogy_type in [
                    AnalogyType.STRUCTURAL,
                    AnalogyType.FUNCTIONAL,
                    AnalogyType.CAUSAL
                ]:
                    result = self.reason_by_analogy(
                        source_name,
                        target_name,
                        source_struct,
                        target_struct,
                        analogy_type
                    )
                    
                    if result and result["analogy"]["creativity_score"] >= min_creativity:
                        # 从结果中重建 AnalogyMapping
                        analogy_data = result["analogy"]
                        creative_analogies.append(
                            self._dict_to_analogy(analogy_data)
                        )
        
        # 按创造性分数排序
        creative_analogies.sort(
            key=lambda a: a.creativity_score, 
            reverse=True
        )
        
        return creative_analogies
    
    def _dict_to_analogy(self, data: Dict) -> AnalogyMapping:
        """将字典转换回 AnalogyMapping 对象"""
        mappings = [
            MappingHypothesis(
                source_element=m["source"],
                target_element=m["target"],
                relation_type=m["relation"],
                confidence=m["confidence"],
                evidence=m.get("evidence", [])
            )
            for m in data["mappings"]
        ]
        
        return AnalogyMapping(
            source_domain=data["source_domain"],
            target_domain=data["target_domain"],
            analogy_type=AnalogyType(data["analogy_type"]),
            mappings=mappings,
            structural_alignments=data["structural_alignments"],
            transferable_knowledge=data["transferable_knowledge"],
            overall_confidence=data["overall_confidence"],
            creativity_score=data["creativity_score"],
            metadata=data.get("metadata", {})
        )
    
    def get_analogy_patterns(self) -> Dict[str, int]:
        """获取类比模式统计"""
        patterns = defaultdict(int)
        for analogy in self.analogy_history:
            key = f"{analogy.source_domain}->{analogy.target_domain}"
            patterns[key] += 1
        return dict(patterns)


# 便捷函数
def create_analogy_engine() -> AnalogyReasoningEngine:
    """创建类比推理引擎实例"""
    return AnalogyReasoningEngine()


def demonstrate_analogy():
    """演示类比推理功能"""
    print("=" * 60)
    print("类比推理引擎演示")
    print("=" * 60)
    
    engine = create_analogy_engine()
    
    # 示例 1：水流电路类比
    print("\n【示例 1】水流→电路类比")
    print("-" * 40)
    
    water_domain = {
        "relations": [
            ("水泵", "驱动", "水流"),
            ("水管", "传输", "水流"),
            ("阀门", "控制", "水流"),
            ("水压", "推动", "水流")
        ],
        "knowledge": {
            "水泵": "提供动力源",
            "阀门": "调节流量",
            "水压": "压力差产生流动"
        }
    }
    
    circuit_domain = {
        "relations": [
            ("电池", "驱动", "电流"),
            ("导线", "传输", "电流"),
            ("开关", "控制", "电流"),
            ("电压", "推动", "电流")
        ],
        "context": {"application": "电路设计"}
    }
    
    result = engine.reason_by_analogy(
        "水力学系统",
        "电路系统",
        water_domain,
        circuit_domain,
        AnalogyType.STRUCTURAL
    )
    
    if result:
        print(f"结论：{result['conclusion']}")
        print(f"迁移知识：{result['transferred_knowledge']}")
        print(f"洞察：{result['insights']}")
    
    # 示例 2：生物进化→算法优化类比
    print("\n【示例 2】生物进化→遗传算法类比")
    print("-" * 40)
    
    evolution_domain = {
        "relations": [
            ("个体", "具有", "基因"),
            ("环境", "选择", "个体"),
            ("繁殖", "传递", "基因"),
            ("变异", "改变", "基因"),
            ("适应", "提高", "生存率")
        ],
        "knowledge": {
            "自然选择": "适者生存",
            "变异": "引入多样性",
            "繁殖": "优势基因传递"
        }
    }
    
    algorithm_domain = {
        "relations": [
            ("解", "具有", "参数"),
            ("适应度函数", "选择", "解"),
            ("交叉", "组合", "参数"),
            ("突变", "改变", "参数"),
            ("迭代", "提高", "解质量")
        ],
        "context": {"problem": "优化问题求解"}
    }
    
    result = engine.reason_by_analogy(
        "生物进化",
        "遗传算法",
        evolution_domain,
        algorithm_domain,
        AnalogyType.PROCEDURAL
    )
    
    if result:
        print(f"结论：{result['conclusion']}")
        print(f"创造性分数：{result['analogy']['creativity_score']:.2f}")
        print(f"洞察：{result['insights']}")
    
    # 示例 3：多领域创造性类比发现
    print("\n【示例 3】多领域创造性类比发现")
    print("-" * 40)
    
    domains = [
        ("生态系统", {
            "relations": [
                ("生产者", "转化", "能量"),
                ("消费者", "消耗", "资源"),
                ("分解者", "循环", "物质")
            ]
        }),
        ("经济系统", {
            "relations": [
                ("生产者", "创造", "商品"),
                ("消费者", "购买", "商品"),
                ("回收商", "处理", "废弃物")
            ]
        }),
        ("知识系统", {
            "relations": [
                ("创造者", "生产", "知识"),
                ("学习者", "吸收", "知识"),
                ("教师", "传播", "知识")
            ]
        })
    ]
    
    creative_analogies = engine.find_creative_analogies(domains, min_creativity=0.5)
    
    print(f"发现 {len(creative_analogies)} 个创造性类比:")
    for i, analogy in enumerate(creative_analogies[:3], 1):
        print(f"\n  {i}. {analogy.source_domain} → {analogy.target_domain}")
        print(f"     类型：{analogy.analogy_type.value}")
        print(f"     创造性：{analogy.creativity_score:.2f}")
        print(f"     映射数：{len(analogy.mappings)}")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demonstrate_analogy()
