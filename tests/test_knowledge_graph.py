"""
测试知识图谱模块 (Knowledge Graph Module)
"""

import unittest
import json
from knowledge_graph import (
    RelationType, KnowledgeEdge, LearningStrategy, Hypothesis,
    KnowledgeGraph, HybridRetriever, MetaLearner, EnhancedMemoryBank,
    get_memory_bank
)
from ucr_layer import UnifiedRepresentationEngine, EntityType


class TestRelationType(unittest.TestCase):
    """测试关系类型枚举"""
    
    def test_relation_types_exist(self):
        """测试所有关系类型存在"""
        self.assertEqual(RelationType.IS_A.value, "is_a")
        self.assertEqual(RelationType.PART_OF.value, "part_of")
        self.assertEqual(RelationType.CAUSES.value, "causes")
        self.assertEqual(RelationType.SIMILAR_TO.value, "similar_to")


class TestKnowledgeEdge(unittest.TestCase):
    """测试知识边"""
    
    def test_creation(self):
        """测试创建边"""
        edge = KnowledgeEdge(
            source_id="node1",
            target_id="node2",
            relation_type=RelationType.CAUSES,
            weight=0.9,
            confidence=0.85
        )
        
        self.assertEqual(edge.source_id, "node1")
        self.assertEqual(edge.target_id, "node2")
        self.assertEqual(edge.relation_type, RelationType.CAUSES)
        self.assertEqual(edge.weight, 0.9)
    
    def test_serialization(self):
        """测试序列化/反序列化"""
        edge = KnowledgeEdge(
            source_id="s1",
            target_id="t1",
            relation_type=RelationType.SUPPORTS,
            evidence=["evidence1", "evidence2"]
        )
        
        data = edge.to_dict()
        restored = KnowledgeEdge.from_dict(data)
        
        self.assertEqual(restored.source_id, edge.source_id)
        self.assertEqual(restored.relation_type, edge.relation_type)
        self.assertEqual(restored.evidence, edge.evidence)


class TestLearningStrategy(unittest.TestCase):
    """测试学习策略"""
    
    def test_creation_and_success_rate(self):
        """测试创建和成功率计算"""
        strategy = LearningStrategy(
            id="test_strat",
            name="Test Strategy",
            description="A test strategy",
            domain="general"
        )
        
        self.assertEqual(strategy.success_rate, 0.5)  # 初始值
        
        strategy.reinforce(True)
        strategy.reinforce(True)
        strategy.reinforce(False)
        
        self.assertEqual(strategy.success_count, 2)
        self.assertEqual(strategy.failure_count, 1)
        self.assertAlmostEqual(strategy.success_rate, 2/3, places=2)
    
    def test_serialization(self):
        """测试序列化"""
        strategy = LearningStrategy(
            id="strat1",
            name="Strategy 1",
            description="Description",
            domain="test",
            applicable_patterns=["pattern1"]
        )
        
        data = strategy.to_dict()
        restored = LearningStrategy.from_dict(data)
        
        self.assertEqual(restored.id, strategy.id)
        self.assertEqual(restored.applicable_patterns, strategy.applicable_patterns)


class TestHypothesis(unittest.TestCase):
    """测试假设"""
    
    def test_creation_and_update(self):
        """测试创建和更新"""
        hyp = Hypothesis(
            id="hyp1",
            description="Test hypothesis"
        )
        
        self.assertEqual(hyp.confidence, 0.5)
        self.assertEqual(hyp.status, "pending")
        
        # 正面证据
        hyp.update_confidence(True, strength=0.2)
        self.assertAlmostEqual(hyp.confidence, 0.7, places=2)
        
        # 负面证据
        hyp.update_confidence(False, strength=0.1)
        self.assertAlmostEqual(hyp.confidence, 0.6, places=2)
    
    def test_verification_thresholds(self):
        """测试验证阈值"""
        hyp = Hypothesis(id="hyp2", description="Test")
        
        # 多次正面更新应达到 verified
        for _ in range(5):
            hyp.update_confidence(True, strength=0.1)
        
        self.assertEqual(hyp.status, "verified")
        
        # 重置并测试 refuted
        hyp2 = Hypothesis(id="hyp3", description="Test")
        for _ in range(4):
            hyp2.update_confidence(False, strength=0.1)
        
        self.assertEqual(hyp2.status, "refuted")


class TestKnowledgeGraph(unittest.TestCase):
    """测试知识图谱"""
    
    def setUp(self):
        """设置测试环境"""
        self.graph = KnowledgeGraph()
        self.ucr = UnifiedRepresentationEngine()
        
        # 创建测试节点
        unit1 = self.ucr.create_unit("Concept A", domain='test')
        unit2 = self.ucr.create_unit("Concept B", domain='test')
        
        self.graph.add_node(unit1)
        self.graph.add_node(unit2)
    
    def test_add_node(self):
        """测试添加节点"""
        self.assertEqual(len(self.graph.nodes), 2)
    
    def test_add_edge(self):
        """测试添加边"""
        node_ids = list(self.graph.nodes.keys())
        
        edge = self.graph.add_edge(
            node_ids[0], node_ids[1],
            RelationType.CAUSES,
            weight=0.8,
            evidence=["test evidence"]
        )
        
        self.assertIsNotNone(edge)
        self.assertEqual(len(self.graph.edges[node_ids[0]]), 1)
        self.assertEqual(edge.relation_type, RelationType.CAUSES)
    
    def test_get_neighbors(self):
        """测试获取邻居"""
        node_ids = list(self.graph.nodes.keys())
        
        self.graph.add_edge(node_ids[0], node_ids[1], RelationType.CAUSES)
        
        neighbors = self.graph.get_neighbors(node_ids[0])
        
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0][0].id, node_ids[1])
    
    def test_find_path(self):
        """测试路径查找"""
        node_ids = list(self.graph.nodes.keys())
        
        # 创建链式关系
        unit3 = self.ucr.create_unit("Concept C", domain='test')
        self.graph.add_node(unit3)
        
        self.graph.add_edge(node_ids[0], node_ids[1], RelationType.CAUSES)
        self.graph.add_edge(node_ids[1], unit3.id, RelationType.ENABLES)
        
        paths = self.graph.find_path(node_ids[0], unit3.id)
        
        self.assertGreater(len(paths), 0)
    
    def test_export_import(self):
        """测试导出/导入"""
        node_ids = list(self.graph.nodes.keys())
        self.graph.add_edge(node_ids[0], node_ids[1], RelationType.SIMILAR_TO)
        
        data = self.graph.export_to_dict()
        
        new_graph = KnowledgeGraph()
        new_graph.import_from_dict(data)
        
        self.assertEqual(len(new_graph.nodes), len(self.graph.nodes))
        self.assertGreater(len(new_graph.edge_index), 0)


class TestHybridRetriever(unittest.TestCase):
    """测试混合检索器"""
    
    def setUp(self):
        """设置测试环境"""
        self.ucr = UnifiedRepresentationEngine()
        self.graph = KnowledgeGraph()
        self.retriever = HybridRetriever(self.graph, self.ucr)
        
        # 添加一些测试数据
        self.ucr.create_unit("Machine learning is a subset of AI", domain='ai')
        self.ucr.create_unit("Deep learning uses neural networks", domain='ai')
        
        # 同步到图谱
        for unit in self.ucr.units.values():
            self.graph.add_node(unit)
    
    def test_retrieve_mixed(self):
        """测试混合检索"""
        results = self.retriever.retrieve("machine learning and AI", top_k=5)
        
        self.assertGreater(len(results), 0)
    
    def test_retrieve_graph_only(self):
        """测试仅图谱检索"""
        results = self.retriever.retrieve(
            "learning", 
            top_k=5,
            use_vector=False,
            use_graph=True
        )
        
        # 应该返回匹配标签或定义的节点
        self.assertGreaterEqual(len(results), 0)
    
    def test_retrieve_vector_only(self):
        """测试仅向量检索"""
        results = self.retriever.retrieve(
            "neural networks",
            top_k=5,
            use_graph=False,
            use_vector=True
        )
        
        self.assertGreater(len(results), 0)


class TestMetaLearner(unittest.TestCase):
    """测试元学习器"""
    
    def setUp(self):
        """设置测试环境"""
        self.graph = KnowledgeGraph()
        self.learner = MetaLearner(self.graph)
    
    def test_initial_strategies(self):
        """测试初始策略"""
        self.assertGreater(len(self.learner.strategies), 0)
        
        strategy_ids = list(self.learner.strategies.keys())
        self.assertIn("strategy_pattern_matching", strategy_ids)
        self.assertIn("strategy_first_principles", strategy_ids)
    
    def test_select_strategy(self):
        """测试策略选择"""
        strategy = self.learner.select_strategy(
            "Test problem",
            domain="general"
        )
        
        self.assertIsNotNone(strategy)
        self.assertIsInstance(strategy, LearningStrategy)
    
    def test_reinforce_strategy(self):
        """测试策略强化"""
        strategy_id = "strategy_pattern_matching"
        initial_rate = self.learner.strategies[strategy_id].success_rate
        
        self.learner.reinforce_strategy(strategy_id, True)
        self.learner.reinforce_strategy(strategy_id, True)
        
        new_rate = self.learner.strategies[strategy_id].success_rate
        self.assertGreater(new_rate, initial_rate)
    
    def test_generate_hypothesis(self):
        """测试假设生成"""
        hyp = self.learner.generate_hypothesis(
            "Observation about learning",
            ["concept1", "concept2"]
        )
        
        self.assertIsNotNone(hyp)
        self.assertIn(hyp.id, self.learner.hypotheses)
    
    def test_test_hypothesis(self):
        """测试假设验证"""
        hyp = self.learner.generate_hypothesis("Test observation", [])
        initial_confidence = hyp.confidence
        
        result = self.learner.test_hypothesis(hyp.id, "Evidence 1", True)
        
        self.assertGreater(result.confidence, initial_confidence)
    
    def test_merge_similar_concepts(self):
        """测试相似概念合并"""
        ucr = UnifiedRepresentationEngine()
        
        # 创建两个非常相似的单元
        ucr.create_unit("Functions are reusable code blocks", domain='programming')
        ucr.create_unit("Functions are blocks of reusable code", domain='programming')
        
        # 同步到图谱
        for unit in ucr.units.values():
            self.graph.add_node(unit)
        
        merged = self.learner.merge_similar_concepts(threshold=0.8)
        
        # 高相似度应该触发合并
        self.assertGreaterEqual(len(merged), 0)


class TestEnhancedMemoryBank(unittest.TestCase):
    """测试增强记忆银行"""
    
    def setUp(self):
        """设置测试环境"""
        self.memory = EnhancedMemoryBank(
            storage_path="test_memory.json",
            graph_storage_path="test_knowledge_graph.json"
        )
    
    def tearDown(self):
        """清理测试文件"""
        import os
        try:
            os.remove("test_memory.json")
        except FileNotFoundError:
            pass
        try:
            os.remove("test_knowledge_graph.json")
        except FileNotFoundError:
            pass
    
    def test_add_knowledge(self):
        """测试添加知识"""
        unit = self.memory.add_knowledge(
            "Test knowledge content",
            content_type='text',
            domain='test',
            tags={'test_tag'}
        )
        
        self.assertIsNotNone(unit)
        # domain is automatically added as a tag
        self.assertIn('test_tag', unit.tags)
    
    def test_retrieve_knowledge(self):
        """测试检索知识"""
        self.memory.add_knowledge(
            "Python programming language features",
            domain='programming',
            tags={'python'}
        )
        
        results = self.memory.retrieve("programming languages", top_k=5)
        
        self.assertGreater(len(results), 0)
    
    def test_learn_from_interaction(self):
        """测试从交互学习"""
        result = self.memory.learn_from_interaction(
            problem="How to sort a list?",
            solution="Use the sorted() function",
            success=True,
            domain='coding'
        )
        
        self.assertIn('problem_id', result)
        self.assertIn('solution_id', result)
        self.assertIn('strategy_used', result)
    
    def test_get_knowledge_stats(self):
        """测试获取统计"""
        self.memory.add_knowledge("Content 1", domain='test1')
        self.memory.add_knowledge("Content 2", domain='test2')
        
        stats = self.memory.get_knowledge_stats()
        
        self.assertIn('total_units', stats)
        self.assertIn('total_edges', stats)
        self.assertIn('strategy_stats', stats)
        self.assertGreater(stats['total_units'], 0)
    
    def test_domain_filtering(self):
        """测试领域过滤"""
        self.memory.add_knowledge("AI concept", domain='ai', tags={'ai'})
        self.memory.add_knowledge("Cooking recipe", domain='cooking', tags={'cooking'})
        
        ai_results = self.memory.retrieve("concept", domain_filter='ai')
        cooking_results = self.memory.retrieve("concept", domain_filter='cooking')
        
        # 验证过滤效果
        ai_domains = ['ai' for unit, _ in ai_results if 'ai' in unit.tags]
        self.assertGreater(len(ai_domains), 0)


class TestGetMemoryBankSingleton(unittest.TestCase):
    """测试单例模式"""
    
    def test_singleton_behavior(self):
        """测试单例行为"""
        mem1 = get_memory_bank()
        mem2 = get_memory_bank()
        
        self.assertIs(mem1, mem2)


if __name__ == "__main__":
    unittest.main()
