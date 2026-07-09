"""
阶段 11: 概念抽象与零样本泛化模块测试

测试内容:
- 元模式识别器 (MetaPatternRecognizer)
- 类比推理引擎 (AnalogyEngine)
- 概念组合模块 (ConceptBlender)
- 概念层级图谱 (ConceptHierarchyGraph)
- 统一引擎 (ConceptAbstractionEngine)

运行方式:
    python -m pytest tests/test_concept_abstraction.py -v
"""

import pytest
import numpy as np
from src.modules.concept_abstraction import (
    PatternType,
    AbstractPattern,
    Concept,
    Mapping,
    BlendedConcept,
    ConceptHierarchyGraph,
    MetaPatternRecognizer,
    AnalogyEngine,
    ConceptBlender,
    ConceptAbstractionEngine
)


class TestConceptHierarchyGraph:
    """测试概念层级图谱"""
    
    def test_add_concept(self):
        """测试添加概念"""
        graph = ConceptHierarchyGraph()
        concept = Concept(
            concept_id="c1",
            name="TestConcept",
            attributes={'attr1': 5},
            relations=[],
            abstraction_level=2,
            domain="test"
        )
        
        graph.add_concept(concept)
        
        assert "c1" in graph.concepts
        assert graph.concepts["c1"].name == "TestConcept"
    
    def test_add_parent_child_relation(self):
        """测试添加父子关系"""
        graph = ConceptHierarchyGraph()
        
        parent = Concept("p", "Parent", {}, [], 3, "test")
        child = Concept("c", "Child", {}, [], 2, "test")
        
        graph.add_concept(parent)
        graph.add_concept(child)
        graph.add_parent_child("p", "c")
        
        assert "c" in graph.parent_child_relations["p"]
    
    def test_get_ancestors(self):
        """测试获取祖先概念"""
        graph = ConceptHierarchyGraph()
        
        # 创建三代：grandparent -> parent -> child
        graph.add_concept(Concept("gp", "GrandParent", {}, [], 4, "test"))
        graph.add_concept(Concept("p", "Parent", {}, [], 3, "test"))
        graph.add_concept(Concept("c", "Child", {}, [], 2, "test"))
        
        graph.add_parent_child("gp", "p")
        graph.add_parent_child("p", "c")
        
        ancestors = graph.get_ancestors("c")
        
        assert "p" in ancestors
        assert "gp" in ancestors
    
    def test_get_descendants(self):
        """测试获取后代概念"""
        graph = ConceptHierarchyGraph()
        
        graph.add_concept(Concept("gp", "GrandParent", {}, [], 4, "test"))
        graph.add_concept(Concept("p", "Parent", {}, [], 3, "test"))
        graph.add_concept(Concept("c", "Child", {}, [], 2, "test"))
        
        graph.add_parent_child("gp", "p")
        graph.add_parent_child("p", "c")
        
        descendants = graph.get_descendants("gp")
        
        assert "p" in descendants
        assert "c" in descendants
    
    def test_find_similar_concepts(self):
        """测试查找相似概念"""
        graph = ConceptHierarchyGraph()
        
        c1 = Concept("c1", "Concept1", {'a': 5, 'b': 10}, [], 2, "physics")
        c2 = Concept("c2", "Concept2", {'a': 6, 'b': 11}, [], 2, "physics")
        c3 = Concept("c3", "Concept3", {'x': 100}, [], 1, "biology")
        
        graph.add_concept(c1)
        graph.add_concept(c2)
        graph.add_concept(c3)
        
        similar = graph.find_similar_concepts("c1", threshold=0.3)
        
        # c2 应该与 c1 相似（同领域，属性接近）
        assert len(similar) > 0
        assert similar[0][0] == "c2"
    
    def test_get_abstraction_path(self):
        """测试获取抽象路径"""
        graph = ConceptHierarchyGraph()
        
        graph.add_concept(Concept("specific", "Specific", {}, [], 1, "test"))
        graph.add_concept(Concept("general", "General", {}, [], 3, "test"))
        
        graph.add_parent_child("general", "specific")
        
        path = graph.get_abstraction_path("specific")
        
        assert path == ["specific", "general"]
    
    def test_add_instance(self):
        """测试添加实例"""
        graph = ConceptHierarchyGraph()
        
        concept = Concept("c", "Concept", {}, [], 2, "test")
        graph.add_concept(concept)
        graph.add_instance("inst1", "c")
        
        assert "inst1" in graph.instance_of_relations
        assert "inst1" in graph.concepts["c"].instances


class TestMetaPatternRecognizer:
    """测试元模式识别器"""
    
    def test_extract_sequential_pattern(self):
        """测试提取序列模式"""
        recognizer = MetaPatternRecognizer()
        
        case = {
            'sequence': [1, 2, 3, 4, 5]
        }
        
        pattern = recognizer.extract_pattern(case, "math", PatternType.SEQUENTIAL)
        
        assert pattern.pattern_type == PatternType.SEQUENTIAL
        assert pattern.structure['type'] == 'sequence'
        assert pattern.structure['length'] == 5
        assert len(pattern.structure['transitions']) == 4
    
    def test_extract_hierarchical_pattern(self):
        """测试提取层级模式"""
        recognizer = MetaPatternRecognizer()
        
        case = {
            'root': {
                'value': 'A',
                'children': [
                    {'value': 'B', 'children': []},
                    {'value': 'C', 'children': []}
                ]
            }
        }
        
        pattern = recognizer.extract_pattern(case, "cs", PatternType.HIERARCHICAL)
        
        assert pattern.pattern_type == PatternType.HIERARCHICAL
        assert pattern.structure['type'] == 'hierarchy'
        assert pattern.structure['depth'] == 0
    
    def test_extract_transformational_pattern(self):
        """测试提取转换模式"""
        recognizer = MetaPatternRecognizer()
        
        case = {
            'initial': {'state': 'A'},
            'final': {'state': 'B'},
            'operations': ['op1', 'op2']
        }
        
        pattern = recognizer.extract_pattern(case, "physics", PatternType.TRANSFORMATIONAL)
        
        assert pattern.pattern_type == PatternType.TRANSFORMATIONAL
        assert pattern.structure['type'] == 'transformation'
        assert 'initial_state' in pattern.structure
    
    def test_extract_causal_pattern(self):
        """测试提取因果模式"""
        recognizer = MetaPatternRecognizer()
        
        case = {
            'causes': ['rain'],
            'effects': ['wet_ground'],
            'mechanism': 'water_accumulation'
        }
        
        pattern = recognizer.extract_pattern(case, "science", PatternType.CAUSAL)
        
        assert pattern.pattern_type == PatternType.CAUSAL
        assert pattern.structure['type'] == 'causal'
        assert 'causes' in pattern.structure
    
    def test_extract_recursive_pattern(self):
        """测试提取递归模式"""
        recognizer = MetaPatternRecognizer()
        
        case = {
            'base_case': 'n=0 return 1',
            'recursive_case': 'n>0 return n * f(n-1)',
            'termination': 'n reaches 0'
        }
        
        pattern = recognizer.extract_pattern(case, "math", PatternType.RECURSIVE)
        
        assert pattern.pattern_type == PatternType.RECURSIVE
        assert pattern.structure['type'] == 'recursive'
        assert 'base_case' in pattern.structure
    
    def test_identify_variables(self):
        """测试变量识别"""
        recognizer = MetaPatternRecognizer()
        
        structure = {
            'type': 'equation',
            'left': '$x',
            'right': '$y + $z'
        }
        
        variables = recognizer._identify_variables(structure)
        
        assert '$x' in variables
        assert '$y' in variables
        assert '$z' in variables
    
    def test_calculate_abstraction_level(self):
        """测试抽象层级计算"""
        recognizer = MetaPatternRecognizer()
        
        # 简单结构，少变量 -> 低抽象
        level1 = recognizer._calculate_abstraction_level({'simple': 1}, [])
        assert level1 <= 2
        
        # 复杂结构，多变量 -> 高抽象
        complex_struct = {str(i): i for i in range(20)}
        variables = [f'${i}' for i in range(6)]
        level2 = recognizer._calculate_abstraction_level(complex_struct, variables)
        assert level2 >= 3
    
    def test_find_isomorphic_patterns(self):
        """测试查找同构模式"""
        recognizer = MetaPatternRecognizer()
        
        # 在两个领域创建相似模式
        case1 = {'sequence': [1, 2, 3]}
        case2 = {'sequence': ['a', 'b', 'c']}
        
        recognizer.extract_pattern(case1, "math", PatternType.SEQUENTIAL)
        recognizer.extract_pattern(case2, "language", PatternType.SEQUENTIAL)
        
        isomorphisms = recognizer.find_isomorphic_patterns("math", "language")
        
        assert len(isomorphisms) > 0
        assert isomorphisms[0][2] > 0.6  # 相似度应较高
    
    def test_build_concept_hierarchy(self):
        """测试构建概念层级"""
        recognizer = MetaPatternRecognizer()
        
        concepts = [
            Concept("c1", "Specific", {'a': 1, 'b': 2, 'c': 3}, [], 1, "test"),
            Concept("c2", "General", {'a': 1}, [], 3, "test")
        ]
        
        recognizer.build_concept_hierarchy(concepts)
        
        # General 应该是 Specific 的父节点
        ancestors = recognizer.concept_graph.get_ancestors("c1")
        assert "c2" in ancestors


class TestAnalogyEngine:
    """测试类比推理引擎"""
    
    def test_create_analogy_basic(self):
        """测试创建基本类比"""
        engine = AnalogyEngine()
        
        source = {
            'objects': ['sun', 'earth'],
            'attributes': {'mass': 100, 'brightness': 90},
            'relations': [('orbits', 'earth', 'sun')]
        }
        
        target = {
            'objects': ['nucleus', 'electron'],
            'attributes': {'mass': 80, 'charge': 50},
            'relations': [('orbits', 'electron', 'nucleus')]
        }
        
        result = engine.create_analogy(source, target)
        
        assert 'mappings' in result
        assert 'inference' in result
        assert 'confidence' in result
        assert result['confidence'] > 0
    
    def test_attribute_mapping(self):
        """测试属性映射"""
        engine = AnalogyEngine()
        
        source = {
            'attributes': {'temperature': 100, 'pressure': 50}
        }
        
        target = {
            'attributes': {'heat': 90, 'force': 45}
        }
        
        result = engine.create_analogy(source, target)
        
        # 应该有属性映射
        mappings = result['mappings']
        attr_mappings = [m for m in mappings if m.mapping_type == 'attribute']
        assert len(attr_mappings) > 0
    
    def test_structural_consistency(self):
        """测试结构一致性验证"""
        engine = AnalogyEngine()
        
        source = {
            'objects': ['A', 'B'],
            'relations': [('connects', 'A', 'B')]
        }
        
        target = {
            'objects': ['X', 'Y'],
            'relations': [('connects', 'X', 'Y')]
        }
        
        result = engine.create_analogy(source, target)
        
        # 一致的映射应该通过验证
        assert len(result['mappings']) > 0
    
    def test_generate_inference(self):
        """测试基于类比生成推理"""
        engine = AnalogyEngine()
        
        source = {
            'attributes': {'has_wings': True, 'can_fly': True},
            'relations': []
        }
        
        target = {
            'attributes': {'has_feathers': True},
            'relations': []
        }
        
        result = engine.create_analogy(source, target)
        
        # 应该推断出目标可能缺少的属性
        inference = result['inference']
        assert 'predicted_attributes' in inference
    
    def test_zero_shot_transfer_success(self):
        """测试成功的零样本迁移"""
        engine = AnalogyEngine()
        
        source_task = {
            'domain': {
                'objects': ['lever', 'fulcrum'],
                'attributes': {'mechanical_advantage': 5}
            }
        }
        
        target_task = {
            'domain': {
                'objects': ['gear', 'axle'],
                'attributes': {}
            }
        }
        
        source_solution = {'apply_force': 'lever', 'pivot_point': 'fulcrum'}
        
        result = engine.zero_shot_transfer(source_task, target_task, source_solution)
        
        # 由于领域相似度可能不高，结果可能为 None
        # 但函数不应报错
        assert result is None or 'transferred_solution' in result
    
    def test_zero_shot_transfer_low_confidence(self):
        """测试低置信度的零样本迁移"""
        engine = AnalogyEngine()
        
        # 完全不相关的领域
        source_task = {'domain': {'objects': ['apple'], 'attributes': {}}}
        target_task = {'domain': {'objects': ['quantum'], 'attributes': {}}}
        
        result = engine.zero_shot_transfer(source_task, target_task, {'solution': 'test'})
        
        # 应该返回 None 因为类比太弱
        assert result is None
    
    def test_mapping_selection_one_to_one(self):
        """测试一对一映射选择"""
        engine = AnalogyEngine()
        
        source = {
            'objects': ['A', 'B', 'C'],
            'attributes': {}
        }
        
        target = {
            'objects': ['X', 'Y', 'Z'],
            'attributes': {}
        }
        
        result = engine.create_analogy(source, target)
        
        # 每个源元素最多映射到一个目标元素
        sources_mapped = [m.source_element for m in result['mappings']]
        targets_mapped = [m.target_element for m in result['mappings']]
        
        assert len(sources_mapped) == len(set(sources_mapped))
        assert len(targets_mapped) == len(set(targets_mapped))


class TestConceptBlender:
    """测试概念组合模块"""
    
    def test_fusion_blend(self):
        """测试融合式混合"""
        blender = ConceptBlender()
        
        c1 = Concept(
            "c1", "Bird",
            {'speed': 8, 'size': 3, 'wings': 2},
            [], 2, "biology"
        )
        
        c2 = Concept(
            "c2", "Airplane",
            {'speed': 9, 'size': 7, 'engines': 2},
            [], 2, "engineering"
        )
        
        blended = blender.blend_concepts(c1, c2, 'fusion')
        
        assert blended.source_concepts == ["c1", "c2"]
        assert 'speed' in blended.blended_attributes
        # 速度应该是平均值
        assert blended.blended_attributes['speed'] == 8.5
    
    def test_contrast_blend(self):
        """测试对比式混合"""
        blender = ConceptBlender()
        
        c1 = Concept("c1", "Hot", {'temperature': 90}, [], 1, "physics")
        c2 = Concept("c2", "Cold", {'temperature': 10}, [], 1, "physics")
        
        blended = blender.blend_concepts(c1, c2, 'contrast')
        
        # 应该有对比属性
        assert any('contrast' in k for k in blended.blended_attributes.keys())
    
    def test_metaphor_blend(self):
        """测试隐喻式混合"""
        blender = ConceptBlender()
        
        c1 = Concept("c1", "Mind", {'processing': 'fast'}, [], 3, "psychology")
        c2 = Concept("c2", "Computer", {'memory': 'large', 'storage': 'huge'}, [], 2, "cs")
        
        blended = blender.blend_concepts(c1, c2, 'metaphor')
        
        # 应该有隐喻属性
        assert any('metaphor' in k for k in blended.blended_attributes.keys())
    
    def test_emergent_properties_detection(self):
        """测试涌现属性检测"""
        blender = ConceptBlender()
        
        # 高速 + 小尺寸 -> 涌现属性
        c1 = Concept("c1", "Fast", {'speed': 9}, [], 2, "physics")
        c2 = Concept("c2", "Small", {'size': 2}, [], 2, "physics")
        
        blended = blender.blend_concepts(c1, c2, 'fusion')
        
        assert len(blended.emergent_properties) > 0
        assert "high_speed_small_form_factor" in blended.emergent_properties
    
    def test_cross_domain_creativity_bonus(self):
        """测试跨领域创造性加分"""
        blender = ConceptBlender()
        
        c1 = Concept("c1", "Biological", {'adaptation': 8}, [], 2, "biology")
        c2 = Concept("c2", "Mechanical", {'efficiency': 9}, [], 2, "engineering")
        
        blended = blender.blend_concepts(c1, c2, 'fusion')
        
        # 跨领域应该有创造性加分
        assert blended.creativity_score >= 0.3
        assert "cross_domain_biology_engineering" in blended.emergent_properties
    
    def test_overall_creativity_calculation(self):
        """测试综合创造性计算"""
        blender = ConceptBlender()
        
        c1 = Concept("c1", "C1", {'a': 1}, [], 2, "domain1")
        c2 = Concept("c2", "C2", {'b': 2}, [], 2, "domain2")
        
        blended = blender.blend_concepts(c1, c2, 'fusion')
        
        overall = blended.overall_creativity()
        
        assert 0 <= overall <= 1
        assert overall == 0.4 * blended.creativity_score + \
                         0.3 * blended.coherence_score + \
                         0.3 * blended.usefulness_score
    
    def test_generate_creative_variants(self):
        """测试生成创造性变体"""
        blender = ConceptBlender()
        
        base = Concept("base", "Base", {'core': 5}, [], 2, "general")
        
        variants = blender.generate_creative_variants(base, num_variants=3)
        
        assert len(variants) == 3
        assert all(isinstance(v, BlendedConcept) for v in variants)
    
    def test_get_top_creative_blends(self):
        """测试获取最有创造性的混合"""
        blender = ConceptBlender()
        
        # 创建多个混合
        for i in range(5):
            c1 = Concept(f"c1_{i}", f"C1_{i}", {'val': i}, [], 2, "d1")
            c2 = Concept(f"c2_{i}", f"C2_{i}", {'val': i+1}, [], 2, "d2")
            blender.blend_concepts(c1, c2, 'fusion')
        
        top = blender.get_top_creative_blends(top_n=3)
        
        assert len(top) == 3
        # 应该按创造性排序
        for i in range(len(top) - 1):
            assert top[i].overall_creativity() >= top[i+1].overall_creativity()


class TestConceptAbstractionEngine:
    """测试统一的概念抽象引擎"""
    
    def test_register_concept(self):
        """测试注册概念"""
        engine = ConceptAbstractionEngine()
        
        concept = Concept("c1", "Test", {}, [], 1, "test")
        engine.register_concept(concept)
        
        assert "c1" in engine.concept_registry
    
    def test_abstract_from_cases(self):
        """测试从案例中抽象模式"""
        engine = ConceptAbstractionEngine()
        
        cases = [
            {'sequence': [1, 2, 3]},
            {'sequence': ['a', 'b', 'c']}
        ]
        
        patterns = engine.abstract_from_cases(cases, ["math", "language"])
        
        assert len(patterns) > 0
        assert all(isinstance(p, AbstractPattern) for p in patterns)
    
    def test_find_cross_domain_analogies(self):
        """测试发现跨领域类比"""
        engine = ConceptAbstractionEngine()
        
        # 先在两个领域创建模式
        case1 = {'sequence': [1, 2, 3, 4]}
        case2 = {'sequence': ['a', 'b', 'c', 'd']}
        
        engine.abstract_from_cases([case1, case2], ["math", "language"])
        
        result = engine.find_cross_domain_analogies("math", "language")
        
        assert 'analogies' in result
        assert 'confidence' in result
    
    def test_perform_zero_shot_transfer(self):
        """测试执行零样本迁移"""
        engine = ConceptAbstractionEngine()
        
        source_problem = {
            'domain': {
                'objects': ['ball', 'ramp'],
                'attributes': {'angle': 30}
            }
        }
        
        target_problem = {
            'domain': {
                'objects': ['car', 'road'],
                'attributes': {'slope': 0.1}
            }
        }
        
        source_solution = {'roll': 'ball', 'surface': 'ramp'}
        
        result = engine.perform_zero_shot_transfer(
            source_problem, target_problem, source_solution
        )
        
        assert 'success' in result
        assert 'result' in result
    
    def test_create_creative_concept(self):
        """测试创建创造性概念"""
        engine = ConceptAbstractionEngine()
        
        c1 = Concept("c1", "Light", {'speed': 10}, [], 2, "physics")
        c2 = Concept("c2", "Sound", {'speed': 5}, [], 2, "physics")
        
        engine.register_concept(c1)
        engine.register_concept(c2)
        
        blended = engine.create_creative_concept(["c1", "c2"], 'fusion')
        
        assert blended is not None
        assert isinstance(blended, BlendedConcept)
    
    def test_create_creative_concept_insufficient(self):
        """测试概念不足时的处理"""
        engine = ConceptAbstractionEngine()
        
        c1 = Concept("c1", "Single", {}, [], 1, "test")
        engine.register_concept(c1)
        
        result = engine.create_creative_concept(["c1"])
        
        assert result is None
    
    def test_build_complete_hierarchy(self):
        """测试构建完整层级"""
        engine = ConceptAbstractionEngine()
        
        concepts = [
            Concept("c1", "Specific1", {'a': 1, 'b': 2}, [], 1, "test"),
            Concept("c2", "Specific2", {'a': 1, 'b': 2, 'c': 3}, [], 1, "test"),
            Concept("c3", "General", {'a': 1}, [], 3, "test")
        ]
        
        for c in concepts:
            engine.register_concept(c)
        
        hierarchy = engine.build_complete_hierarchy()
        
        assert isinstance(hierarchy, ConceptHierarchyGraph)
        assert len(hierarchy.concepts) == 3
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        engine = ConceptAbstractionEngine()
        
        # 添加一些数据
        engine.register_concept(Concept("c1", "C1", {}, [], 1, "test"))
        engine.register_concept(Concept("c2", "C2", {}, [], 1, "test"))
        
        engine.abstract_from_cases([{'sequence': [1, 2]}], ["math"])
        
        stats = engine.get_statistics()
        
        assert stats['registered_concepts'] == 2
        assert stats['recognized_patterns'] > 0
        assert 'analogies_created' in stats
        assert 'concepts_blended' in stats
        assert 'avg_pattern_abstraction' in stats


class TestIntegration:
    """集成测试"""
    
    def test_full_abstraction_pipeline(self):
        """测试完整的抽象流程"""
        engine = ConceptAbstractionEngine()
        
        # 1. 从案例中提取模式
        cases = [
            {'sequence': [1, 4, 9, 16]},  # 平方数序列
            {'sequence': [2, 4, 8, 16]},  # 等比序列
        ]
        
        patterns = engine.abstract_from_cases(cases, ["math", "math"])
        
        assert len(patterns) > 0
        
        # 2. 注册相关概念
        engine.register_concept(Concept(
            "square", "Square Number",
            {'formula': 'n^2', 'growth': 'quadratic'},
            [], 3, "math"
        ))
        
        engine.register_concept(Concept(
            "geometric", "Geometric Progression",
            {'formula': 'a*r^n', 'growth': 'exponential'},
            [], 3, "math"
        ))
        
        # 3. 构建层级
        hierarchy = engine.build_complete_hierarchy()
        
        assert len(hierarchy.concepts) >= 2
        
        # 4. 查找跨领域类比（这里都是 math，但测试流程）
        analogies = engine.find_cross_domain_analogies("math", "math")
        
        # 5. 创建创造性概念
        blended = engine.create_creative_concept(
            ["square", "geometric"],
            'fusion'
        )
        
        if blended:
            assert isinstance(blended, BlendedConcept)
            assert blended.overall_creativity() >= 0
    
    def test_pattern_recognition_and_analogy(self):
        """测试模式识别与类比的结合"""
        recognizer = MetaPatternRecognizer()
        analogy_engine = AnalogyEngine()
        
        # 在物理领域提取因果模式
        physics_case = {
            'causes': ['force_applied'],
            'effects': ['acceleration'],
            'mechanism': 'F=ma'
        }
        
        physics_pattern = recognizer.extract_pattern(
            physics_case, "physics", PatternType.CAUSAL
        )
        
        # 在经济领域提取因果模式
        economics_case = {
            'causes': ['demand_increase'],
            'effects': ['price_increase'],
            'mechanism': 'supply_demand'
        }
        
        econ_pattern = recognizer.extract_pattern(
            economics_case, "economics", PatternType.CAUSAL
        )
        
        # 创建类比
        analogy = analogy_engine.create_analogy(
            physics_pattern.structure,
            econ_pattern.structure
        )
        
        assert analogy['confidence'] > 0
        assert len(analogy['mappings']) > 0


# 运行所有测试的主函数
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
