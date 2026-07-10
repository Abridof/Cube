"""
Unified Cognitive Representation (UCR) Layer v1.0
==================================================
核心创新：将多模态输入转换为统一的符号 - 向量混合表示

设计原理：
1. 符号表示：精确的逻辑结构、因果关系、规则
2. 向量表示：语义相似性、模糊匹配、模式识别
3. 混合索引：同时支持精确查询和相似性搜索

Author: AI Assistant
Goal: 为"识别万物、研究万物"提供统一的表示基础
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class RepresentationType(Enum):
    """表示类型枚举"""

    SYMBOLIC = "symbolic"  # 符号表示：精确逻辑
    VECTOR = "vector"  # 向量表示：语义嵌入
    HYBRID = "hybrid"  # 混合表示
    GRAPH = "graph"  # 图结构：关系网络


class EntityType(Enum):
    """实体类型"""

    CONCEPT = "concept"  # 概念
    ACTION = "action"  # 动作
    PROPERTY = "property"  # 属性
    RELATION = "relation"  # 关系
    EVENT = "event"  # 事件
    CONSTRAINT = "constraint"  # 约束
    HYPOTHESIS = "hypothesis"  # 假设
    EVIDENCE = "evidence"  # 证据


@dataclass
class SymbolicNode:
    """
    符号节点：精确的逻辑单元

    特点：
    - 可解释性强
    - 支持逻辑推理
    - 可验证
    """

    id: str
    entity_type: EntityType
    label: str  # 人类可读标签
    definition: str  # 精确定义
    attributes: Dict[str, Any] = field(default_factory=dict)
    relations: List[Tuple[str, str]] = field(default_factory=list)  # (relation_type, target_id)
    constraints: List[str] = field(default_factory=list)
    source: Optional[str] = None  # 来源（代码行、文档段落等）
    confidence: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "entity_type": self.entity_type.value,
            "label": self.label,
            "definition": self.definition,
            "attributes": self.attributes,
            "relations": self.relations,
            "constraints": self.constraints,
            "source": self.source,
            "confidence": self.confidence,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SymbolicNode":
        data["entity_type"] = EntityType(data["entity_type"])
        return cls(**data)


@dataclass
class VectorEmbedding:
    """
    向量嵌入：语义表示

    简化实现：使用词频 + TF-IDF 风格的权重
    生产环境可替换为真实神经网络嵌入
    """

    id: str
    vector: Dict[str, float]  # 稀疏表示：{term: weight}
    metadata: Dict[str, Any] = field(default_factory=dict)
    norm: float = 0.0  # 向量范数，用于相似度计算

    def __post_init__(self):
        if self.norm == 0.0 and self.vector:
            import math

            self.norm = math.sqrt(sum(v * v for v in self.vector.values()))

    def similarity(self, other: "VectorEmbedding") -> float:
        """计算余弦相似度"""
        if not self.vector or not other.vector or self.norm == 0 or other.norm == 0:
            return 0.0

        # 点积
        dot_product = sum(
            self.vector.get(term, 0) * other.vector.get(term, 0)
            for term in set(self.vector.keys()) & set(other.vector.keys())
        )

        return dot_product / (self.norm * other.norm)

    def to_dict(self) -> Dict:
        return {"id": self.id, "vector": self.vector, "metadata": self.metadata, "norm": self.norm}

    @classmethod
    def from_dict(cls, data: Dict) -> "VectorEmbedding":
        return cls(**data)


@dataclass
class CognitiveUnit:
    """
    认知单元：符号 + 向量的混合表示

    这是 UCR 的核心数据结构，每个认知单元包含：
    1. 符号部分：精确的逻辑结构
    2. 向量部分：语义嵌入
    3. 关联图谱：与其他单元的关系
    """

    id: str
    symbolic: SymbolicNode
    vector: Optional[VectorEmbedding] = None
    tags: Set[str] = field(default_factory=set)
    activation_level: float = 0.5  # 激活水平（用于注意力机制）
    access_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "symbolic": self.symbolic.to_dict(),
            "vector": self.vector.to_dict() if self.vector else None,
            "tags": list(self.tags),
            "activation_level": self.activation_level,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CognitiveUnit":
        data["symbolic"] = SymbolicNode.from_dict(data["symbolic"])
        if data.get("vector"):
            data["vector"] = VectorEmbedding.from_dict(data["vector"])
        data["tags"] = set(data.get("tags", []))
        return cls(**data)


class TextEncoder:
    """
    文本编码器：将自然语言转换为向量表示

    简化实现：基于词频和简单权重
    可扩展为 BERT、Sentence Transformers 等
    """

    # 停用词表（简化版）
    STOP_WORDS = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",
        "i",
        "you",
        "he",
        "she",
        "we",
        "they",
        "what",
        "which",
        "who",
        "whom",
        "whose",
        "where",
        "when",
        "why",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "also",
        "now",
        "here",
        "there",
        "then",
        "once",
        "if",
        "because",
        "as",
        "until",
        "while",
        "about",
        "against",
        "between",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "up",
        "down",
        "out",
        "off",
        "over",
        "under",
        "again",
        "further",
        "am",
        "any",
        "your",
        "our",
        "their",
    }

    def __init__(self):
        self.vocabulary: Dict[str, int] = defaultdict(int)
        self.document_count: int = 0

    def _tokenize(self, text: str) -> List[str]:
        """分词并标准化"""
        # 转小写
        text = text.lower()
        # 提取单词
        words = re.findall(r"\b[a-z][a-z]*\b", text)
        # 去除停用词
        return [w for w in words if w not in self.STOP_WORDS and len(w) > 2]

    def encode(self, text: str) -> VectorEmbedding:
        """将文本编码为向量"""
        tokens = self._tokenize(text)

        # 计算词频
        term_freq = defaultdict(int)
        for token in tokens:
            term_freq[token] += 1
            self.vocabulary[token] += 1

        self.document_count += 1

        # 简化的 TF-IDF 风格权重
        vector = {}
        for term, freq in term_freq.items():
            # TF: 词频
            tf = freq / len(tokens) if tokens else 0
            # IDF: 逆文档频率（简化）
            doc_freq = self.vocabulary[term]
            idf = 1.0 + (self.document_count / (doc_freq + 1))
            vector[term] = tf * idf

        embedding_id = hashlib.sha256(text.encode()).hexdigest()[:16]
        return VectorEmbedding(id=embedding_id, vector=vector, metadata={"text_length": len(text)})

    def batch_encode(self, texts: List[str]) -> List[VectorEmbedding]:
        """批量编码"""
        return [self.encode(text) for text in texts]


class SymbolicParser:
    """
    符号解析器：从文本/代码中提取符号结构

    支持：
    - 代码结构解析（函数、类、变量）
    - 逻辑关系提取（因果、条件、约束）
    - 概念识别
    """

    # 代码模式
    CODE_PATTERNS = {
        "function_def": r"(?:def|function)\s+(\w+)\s*\(([^)]*)\)",
        "class_def": r"class\s+(\w+)(?:\s*\(([^)]*)\))?:",
        "variable_assign": r"(\w+)\s*=\s*(.+?)(?:\n|$)",
        "import_stmt": r"import\s+([\w.,\s]+)|from\s+([\w.]+)\s+import\s+([\w.,\s]+)",
        "loop": r"(?:for|while)\s+.+?:",
        "conditional": r"if\s+.+?:",
        "return_stmt": r"return\s+(.+?)(?:\n|$)",
    }

    # 逻辑关系模式
    LOGICAL_PATTERNS = {
        "causation": r"(?:because|therefore|thus|hence|consequently|leads? to|causes?)",
        "condition": r"(?:if|unless|provided that|given that|when|whenever)",
        "contrast": r"(?:however|but|although|despite|nevertheless|whereas)",
        "example": r"(?:for example|for instance|such as|like)",
        "definition": r"(?:is defined as|means|refers to|called)",
    }

    def parse_code(self, code: str, source: Optional[str] = None) -> List[SymbolicNode]:
        """解析代码，提取符号节点"""
        nodes = []

        # 提取函数定义
        for match in re.finditer(self.CODE_PATTERNS["function_def"], code, re.MULTILINE):
            func_name = match.group(1)
            params = match.group(2)

            node = SymbolicNode(
                id=f"func_{func_name}_{hashlib.sha256(code.encode()).hexdigest()[:16]}",
                entity_type=EntityType.ACTION,
                label=f"Function: {func_name}",
                definition=f"Function '{func_name}' with parameters: {params}",
                attributes={
                    "name": func_name,
                    "parameters": [p.strip() for p in params.split(",") if p.strip()],
                    "source_type": "code",
                },
                source=source or f"Line {code[:match.start()].count(chr(10)) + 1}",
            )
            nodes.append(node)

        # 提取类定义
        for match in re.finditer(self.CODE_PATTERNS["class_def"], code, re.MULTILINE):
            class_name = match.group(1)
            bases = match.group(2) or ""

            node = SymbolicNode(
                id=f"class_{class_name}_{hashlib.sha256(code.encode()).hexdigest()[:16]}",
                entity_type=EntityType.CONCEPT,
                label=f"Class: {class_name}",
                definition=f"Class '{class_name}' inheriting from: {bases}",
                attributes={
                    "name": class_name,
                    "base_classes": [b.strip() for b in bases.split(",") if b.strip()],
                    "source_type": "code",
                },
                source=source,
            )
            nodes.append(node)

        # 提取约束（如类型注解、断言）
        for match in re.finditer(r"assert\s+(.+?)(?:\n|$)", code):
            constraint = match.group(1)
            node = SymbolicNode(
                id=f"constraint_{hashlib.sha256(constraint.encode()).hexdigest()[:16]}",
                entity_type=EntityType.CONSTRAINT,
                label="Assertion",
                definition=f"Runtime constraint: {constraint}",
                attributes={"expression": constraint},
                source=source,
            )
            nodes.append(node)

        return nodes

    def parse_text(self, text: str, domain: str = "general") -> List[SymbolicNode]:
        """解析自然语言文本，提取逻辑关系"""
        nodes = []

        # 提取因果关系
        for match in re.finditer(self.LOGICAL_PATTERNS["causation"], text, re.IGNORECASE):
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]

            node = SymbolicNode(
                id=f"causation_{hashlib.sha256(context.encode()).hexdigest()[:16]}",
                entity_type=EntityType.RELATION,
                label="Causal Relationship",
                definition=context.strip(),
                attributes={"relation_type": "causation", "domain": domain},
                source=f"Position {match.start()}-{match.end()}",
            )
            nodes.append(node)

        # 提取条件关系
        for match in re.finditer(self.LOGICAL_PATTERNS["condition"], text, re.IGNORECASE):
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 50)
            context = text[start:end]

            node = SymbolicNode(
                id=f"condition_{hashlib.sha256(context.encode()).hexdigest()[:16]}",
                entity_type=EntityType.CONSTRAINT,
                label="Conditional Statement",
                definition=context.strip(),
                attributes={"relation_type": "condition", "domain": domain},
                source=f"Position {match.start()}-{match.end()}",
            )
            nodes.append(node)

        return nodes

    def parse(
        self, content: Any, content_type: str, source: Optional[str] = None
    ) -> List[SymbolicNode]:
        """通用解析接口"""
        if content_type == "code":
            return self.parse_code(str(content), source)
        elif content_type == "text":
            return self.parse_text(str(content))
        else:
            # 默认作为通用文本处理
            return self.parse_text(str(content))


class UnifiedRepresentationEngine:
    """
    统一表示引擎：将任意输入转换为 CognitiveUnit

    核心功能：
    1. 多模态输入解析（代码、文本、结构化数据）
    2. 符号 - 向量混合表示生成
    3. 自动关系发现和链接
    """

    def __init__(self):
        self.encoder = TextEncoder()
        self.parser = SymbolicParser()
        self.units: Dict[str, CognitiveUnit] = {}
        self.index_by_type: Dict[EntityType, Set[str]] = defaultdict(set)
        self.index_by_tag: Dict[str, Set[str]] = defaultdict(set)

    def create_unit(
        self,
        content: Any,
        content_type: str = "text",
        domain: str = "general",
        tags: Optional[Set[str]] = None,
        source: Optional[str] = None,
    ) -> CognitiveUnit:
        """
        从内容创建认知单元

        Args:
            content: 输入内容（文本、代码、数据等）
            content_type: 内容类型 ('code', 'text', 'data')
            domain: 领域标签
            tags: 附加标签
            source: 来源信息

        Returns:
            CognitiveUnit: 生成的认知单元
        """
        # 1. 符号解析
        symbolic_nodes = self.parser.parse(content, content_type, source)

        # 2. 向量编码
        content_str = str(content) if not isinstance(content, str) else content
        vector_embedding = self.encoder.encode(content_str)

        # 3. 如果没有解析出符号节点，创建一个概括性节点
        if not symbolic_nodes:
            main_node = SymbolicNode(
                id=f"unit_{vector_embedding.id}",
                entity_type=EntityType.CONCEPT,
                label=f"Concept from {content_type}",
                definition=content_str[:200] + ("..." if len(content_str) > 200 else ""),
                attributes={
                    "content_type": content_type,
                    "domain": domain,
                    "length": len(content_str),
                },
                source=source,
            )
            symbolic_nodes = [main_node]

        # 4. 创建主认知单元（使用第一个符号节点）
        main_symbolic = symbolic_nodes[0]
        unit_id = main_symbolic.id

        cognitive_unit = CognitiveUnit(
            id=unit_id,
            symbolic=main_symbolic,
            vector=vector_embedding,
            tags=tags or {domain, content_type},
        )

        # 5. 建立索引
        self.units[unit_id] = cognitive_unit
        self.index_by_type[main_symbolic.entity_type].add(unit_id)
        for tag in cognitive_unit.tags:
            self.index_by_tag[tag].add(unit_id)

        # 6. 如果有多个符号节点，创建关联单元
        for additional_node in symbolic_nodes[1:]:
            additional_unit = CognitiveUnit(
                id=additional_node.id,
                symbolic=additional_node,
                vector=vector_embedding,  # 共享向量表示
                tags=cognitive_unit.tags.copy(),
            )
            self.units[additional_node.id] = additional_unit
            self.index_by_type[additional_node.entity_type].add(additional_node.id)

            # 建立关系
            main_symbolic.relations.append(("related_to", additional_node.id))
            additional_node.relations.append(("related_to", unit_id))

        logger.info(f"Created cognitive unit: {unit_id} with {len(symbolic_nodes)} symbolic nodes")
        return cognitive_unit

    def get_unit(self, unit_id: str) -> Optional[CognitiveUnit]:
        """获取认知单元"""
        unit = self.units.get(unit_id)
        if unit:
            unit.access_count += 1
            unit.last_accessed = datetime.now().isoformat()
        return unit

    def search_by_type(self, entity_type: EntityType) -> List[CognitiveUnit]:
        """按实体类型搜索"""
        unit_ids = self.index_by_type.get(entity_type, set())
        return [self.get_unit(uid) for uid in unit_ids if self.get_unit(uid)]

    def search_by_tag(self, tag: str) -> List[CognitiveUnit]:
        """按标签搜索"""
        unit_ids = self.index_by_tag.get(tag, set())
        return [self.get_unit(uid) for uid in unit_ids if self.get_unit(uid)]

    def search_by_similarity(
        self, query: str, threshold: float = 0.3, limit: int = 10
    ) -> List[Tuple[CognitiveUnit, float]]:
        """
        基于语义相似性搜索

        Args:
            query: 查询文本
            threshold: 相似度阈值
            limit: 返回数量限制

        Returns:
            List of (CognitiveUnit, similarity_score)
        """
        query_vector = self.encoder.encode(query)
        results = []

        for unit in self.units.values():
            if unit.vector:
                similarity = unit.vector.similarity(query_vector)
                if similarity >= threshold:
                    results.append((unit, similarity))

        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def find_relations(self, unit_id: str, max_depth: int = 2) -> List[CognitiveUnit]:
        """
        查找与给定单元相关的所有单元（广度优先搜索）

        Args:
            unit_id: 起始单元 ID
            max_depth: 最大搜索深度

        Returns:
            相关单元列表
        """
        visited = set()
        queue = [(unit_id, 0)]
        related = []

        while queue:
            current_id, depth = queue.pop(0)
            if current_id in visited or depth > max_depth:
                continue

            visited.add(current_id)
            unit = self.get_unit(current_id)
            if unit and current_id != unit_id:
                related.append(unit)

            if unit and depth < max_depth:
                for _, target_id in unit.symbolic.relations:
                    if target_id not in visited:
                        queue.append((target_id, depth + 1))

        return related

    def export_to_dict(self) -> Dict:
        """导出所有认知单元"""
        return {
            "units": {uid: unit.to_dict() for uid, unit in self.units.items()},
            "index_by_type": {k.value: list(v) for k, v in self.index_by_type.items()},
            "index_by_tag": dict(self.index_by_tag),
            "metadata": {"total_units": len(self.units), "exported_at": datetime.now().isoformat()},
        }

    def import_from_dict(self, data: Dict):
        """从字典导入认知单元"""
        for uid, unit_data in data.get("units", {}).items():
            unit = CognitiveUnit.from_dict(unit_data)
            self.units[uid] = unit
            self.index_by_type[unit.symbolic.entity_type].add(uid)
            for tag in unit.tags:
                self.index_by_tag[tag].add(uid)

        logger.info(f"Imported {len(self.units)} cognitive units")


# 便捷函数
_default_engine: Optional[UnifiedRepresentationEngine] = None


def get_engine() -> UnifiedRepresentationEngine:
    """获取或创建默认引擎"""
    global _default_engine
    if _default_engine is None:
        _default_engine = UnifiedRepresentationEngine()
    return _default_engine


def represent(content: Any, content_type: str = "text", **kwargs) -> CognitiveUnit:
    """便捷函数：将内容转换为认知单元"""
    engine = get_engine()
    return engine.create_unit(content, content_type, **kwargs)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)

    print("=== Testing Unified Cognitive Representation ===\n")

    engine = UnifiedRepresentationEngine()

    # 测试 1: 代码解析
    print("--- Test 1: Code Parsing ---")
    code = """
def calculate_sum(a, b):
    '''Calculate the sum of two numbers'''
    return a + b

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x):
        self.result += x
        assert self.result >= 0
"""
    unit = engine.create_unit(
        code, content_type="code", domain="programming", tags={"python", "arithmetic"}
    )
    print(f"Created unit: {unit.id}")
    print(f"Entity type: {unit.symbolic.entity_type}")
    print(f"Tags: {unit.tags}")
    print(f"Relations: {unit.symbolic.relations}")

    # 测试 2: 文本解析
    print("\n--- Test 2: Text Parsing ---")
    text = """
    If the temperature exceeds 100 degrees, water will boil.
    This happens because heat causes molecules to move faster.
    However, at high altitudes, water boils at lower temperatures.
    """
    unit = engine.create_unit(
        text, content_type="text", domain="physics", tags={"thermodynamics", "phase_change"}
    )
    print(f"Created unit: {unit.id}")
    print(f"Definition: {unit.symbolic.definition[:100]}...")
    print(f"Relations: {unit.symbolic.relations}")

    # 测试 3: 相似性搜索
    print("\n--- Test 3: Similarity Search ---")
    query = "temperature and boiling"
    results = engine.search_by_similarity(query, threshold=0.1)
    print(f"Query: {query}")
    print(f"Found {len(results)} similar units:")
    for unit, score in results:
        print(f"  - {unit.symbolic.label} (score: {score:.3f})")

    # 测试 4: 关系发现
    print("\n--- Test 4: Relation Discovery ---")
    if len(engine.units) > 1:
        first_unit_id = list(engine.units.keys())[0]
        related = engine.find_relations(first_unit_id)
        print(f"Related to {first_unit_id}: {len(related)} units")

    # 测试 5: 导出/导入
    print("\n--- Test 5: Export/Import ---")
    data = engine.export_to_dict()
    print(f"Exported {data['metadata']['total_units']} units")

    new_engine = UnifiedRepresentationEngine()
    new_engine.import_from_dict(data)
    print(f"Imported into new engine: {len(new_engine.units)} units")

    print("\n=== All Tests Complete ===")


# ============================================================================
# 导出别名（用于兼容其他模块的导入）
# ============================================================================

# UCR 是 CognitiveUnit 的别名，用于简化导入
UCR = CognitiveUnit

# UCRLayer 是 UnifiedRepresentationEngine 的别名，用于保持接口一致性
UCRLayer = UnifiedRepresentationEngine
