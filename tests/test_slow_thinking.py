"""
系统 2 慢思考推理引擎测试
测试 ChainOfThought, TreeOfThought, LogicValidator, MultiStepPlanner, SlowThinkingEngine
"""

import pytest
import time
from src.modules.slow_thinking import (
    ReasoningStrategy,
    ThoughtNode,
    ReasoningStep,
    ReasoningTrace,
    ChainOfThought,
    TreeOfThought,
    LogicValidator,
    MultiStepPlanner,
    SlowThinkingEngine,
    deep_reason,
    plan_task
)


class TestThoughtNode:
    """测试思维节点"""
    
    def test_create_node(self):
        """创建基本节点"""
        node = ThoughtNode(
            id="test_1",
            content="这是一个测试节点",
            depth=0
        )
        assert node.id == "test_1"
        assert node.content == "这是一个测试节点"
        assert node.depth == 0
        assert node.visits == 0
        assert node.value == 0.0
    
    def test_uct_score_unvisited(self):
        """未访问节点的 UCT 分数应为无穷大"""
        node = ThoughtNode(id="test", content="test", visits=0)
        assert node.uct_score() == float('inf')
    
    def test_uct_score_visited(self):
        """已访问节点的 UCT 分数应有限"""
        node = ThoughtNode(
            id="test",
            content="test",
            visits=10,
            total_reward=8.0
        )
        score = node.uct_score()
        assert score > 0
        assert score < float('inf')


class TestReasoningStep:
    """测试推理步骤"""
    
    def test_create_step(self):
        step = ReasoningStep(
            step_number=1,
            content="第一步分析",
            method="analyze",
            confidence=0.9
        )
        assert step.step_number == 1
        assert step.confidence == 0.9
        assert step.validation_status == "pending"
        assert len(step.dependencies) == 0


class TestChainOfThought:
    """测试思维链推理器"""
    
    def test_basic_reasoning(self):
        """基本推理测试"""
        cot = ChainOfThought(max_steps=10)
        trace = cot.reason("计算 1+2+3 的和")
        
        assert len(trace.steps) > 0
        assert trace.conclusion is not None
        assert trace.confidence > 0
        assert trace.strategy == ReasoningStrategy.CHAIN_OF_THOUGHT
        assert trace.total_time > 0
    
    def test_reasoning_with_context(self):
        """带上下文的推理"""
        cot = ChainOfThought()
        context = {"known_facts": ["1+1=2", "2+2=4"]}
        trace = cot.reason("推导 3+3 的值", context)
        
        assert len(trace.steps) >= 1
        assert trace.conclusion is not None
    
    def test_confidence_calculation(self):
        """置信度计算测试"""
        cot = ChainOfThought(max_steps=5)
        trace = cot.reason("简单问题")
        
        # 置信度应在合理范围内
        assert 0.0 <= trace.confidence <= 1.0
        
        # 多步推理后置信度应合理
        steps_confidences = [s.confidence for s in trace.steps]
        assert all(0.0 <= c <= 1.0 for c in steps_confidences)
    
    def test_backtracking(self):
        """测试回溯机制"""
        cot = ChainOfThought(max_steps=20, min_confidence=0.5)
        trace = cot.reason("复杂逻辑问题")
        
        # 应该有合理的步骤数
        assert len(trace.steps) >= 1
        assert trace.nodes_explored == len(trace.steps)
    
    def test_step_generation(self):
        """测试步骤生成"""
        cot = ChainOfThought(max_steps=15)
        trace = cot.reason("数学证明题")
        
        # 检查步骤的连贯性
        for i in range(1, len(trace.steps)):
            step = trace.steps[i]
            assert step.step_number == i + 1
            assert step.method in ["analyze", "infer", "verify", "calculate", "compare", "decompose"]


class TestTreeOfThought:
    """测试思维树搜索器"""
    
    def test_basic_search(self):
        """基本树搜索测试"""
        tot = TreeOfThought(max_depth=5, branching_factor=2, beam_width=3)
        trace, nodes = tot.search("优化算法设计")
        
        assert len(trace.steps) > 0
        assert trace.conclusion is not None
        assert trace.strategy == ReasoningStrategy.TREE_OF_THOUGHT
        assert len(nodes) > 0
        assert trace.nodes_explored > 0
    
    def test_mcts_search(self):
        """蒙特卡洛树搜索测试"""
        tot = TreeOfThought(max_depth=5)
        trace, nodes = tot.mcts_search(
            "游戏策略优化",
            num_simulations=50
        )
        
        assert len(trace.steps) > 0
        assert trace.strategy == ReasoningStrategy.MONTE_CARLO
        assert trace.nodes_explored > 0
        
        # MCTS 应该有访问次数和奖励信息
        if trace.steps:
            first_step = trace.steps[0]
            assert "visits" in first_step.metadata or "total_reward" in first_step.metadata
    
    def test_custom_evaluator(self):
        """使用自定义评估函数"""
        def custom_eval(content: str) -> float:
            return 0.8 if "优化" in content else 0.5
        
        tot = TreeOfThought(max_depth=3)
        trace, nodes = tot.search(
            "代码优化方案",
            evaluator=custom_eval
        )
        
        assert trace.confidence >= 0.5
    
    def test_node_generation(self):
        """测试节点生成"""
        tot = TreeOfThought(branching_factor=3)
        root = tot._create_node("根节点", None, 0)
        
        assert root.id == "node_1"
        assert root.depth == 0
        assert root.parent_id is None
        
        children = tot._generate_children(root)
        assert len(children) == 3
        assert all(c.depth == 1 for c in children)
        assert all(c.parent_id == root.id for c in children)


class TestLogicValidator:
    """测试逻辑验证器"""
    
    def test_valid_trace(self):
        """验证有效的推理轨迹"""
        validator = LogicValidator()
        
        trace = ReasoningTrace(
            problem="测试问题",
            strategy=ReasoningStrategy.CHAIN_OF_THOUGHT,
            steps=[
                ReasoningStep(1, "步骤 1", "analyze", 0.9),
                ReasoningStep(2, "步骤 2", "infer", 0.85, dependencies=[1]),
                ReasoningStep(3, "步骤 3", "verify", 0.88, dependencies=[2])
            ],
            conclusion="基于以上推理得出结论",
            confidence=0.88
        )
        
        result = validator.validate(trace)
        assert result["is_valid"] == True
        assert len(result["errors"]) == 0
    
    def test_confidence_drop_warning(self):
        """检测置信度下降过快"""
        validator = LogicValidator()
        
        trace = ReasoningTrace(
            problem="测试",
            strategy=ReasoningStrategy.CHAIN_OF_THOUGHT,
            steps=[
                ReasoningStep(1, "步骤 1", "analyze", 0.95),
                ReasoningStep(2, "步骤 2", "infer", 0.5),  # 大幅下降
            ],
            conclusion="结论",
            confidence=0.5
        )
        
        result = validator.validate(trace)
        assert len(result["warnings"]) > 0
    
    def test_empty_trace(self):
        """处理空轨迹"""
        validator = LogicValidator()
        
        trace = ReasoningTrace(
            problem="测试",
            strategy=ReasoningStrategy.CHAIN_OF_THOUGHT,
            steps=[],
            conclusion=None,
            confidence=0.0
        )
        
        result = validator.validate(trace)
        # 应该能处理边界情况而不崩溃
        assert isinstance(result, dict)


class TestMultiStepPlanner:
    """测试多步规划器"""
    
    def test_create_plan(self):
        """创建计划"""
        planner = MultiStepPlanner()
        plan = planner.create_plan("解决复杂数学问题")
        
        assert len(plan) > 0
        assert all("step_id" in step for step in plan)
        assert all("name" in step for step in plan)
        assert all("status" in step for step in plan)
    
    def test_plan_types(self):
        """测试不同类型的计划"""
        planner = MultiStepPlanner()
        
        plan1 = planner.create_plan("目标 1", plan_type="problem_solving")
        plan2 = planner.create_plan("目标 2", plan_type="analysis")
        plan3 = planner.create_plan("目标 3", plan_type="creative")
        
        assert len(plan1) > 0
        assert len(plan2) > 0
        assert len(plan3) > 0
        
        # 不同类型的计划第一步应该不同
        assert plan1[0]["name"] != plan2[0]["name"]
    
    def test_execute_plan_without_executor(self):
        """无执行器的模拟执行"""
        planner = MultiStepPlanner()
        plan = planner.create_plan("测试目标")
        
        result = planner.execute_plan(plan)
        
        assert result["completed_steps"] == len(plan)
        assert result["failed_steps"] == 0
        assert result["overall_success"] == True
    
    def test_execute_plan_with_executor(self):
        """带执行器的实际执行"""
        planner = MultiStepPlanner()
        plan = planner.create_plan("测试目标")
        
        def mock_executor(step):
            return f"执行了{step['name']}"
        
        result = planner.execute_plan(plan, executor=mock_executor)
        
        assert result["completed_steps"] == len(plan)
        assert all("result" in step for step in result["step_results"])
    
    def test_replan_after_failure(self):
        """失败后重新规划"""
        planner = MultiStepPlanner()
        original_plan = planner.create_plan("原始目标")
        
        new_plan = planner.replan(
            original_plan,
            failed_step_index=2,
            new_context={"new_info": "发现新情况"}
        )
        
        assert len(new_plan) > 2
        # 前两步应该保留
        assert new_plan[0]["step_id"] == original_plan[0]["step_id"]
        assert new_plan[1]["step_id"] == original_plan[1]["step_id"]


class TestSlowThinkingEngine:
    """测试慢思考引擎"""
    
    def test_basic_reasoning(self):
        """基本推理"""
        engine = SlowThinkingEngine()
        result = engine.reason("证明勾股定理")
        
        assert "problem" in result
        assert "conclusion" in result
        assert "confidence" in result
        assert "steps" in result
        assert len(result["steps"]) > 0
    
    def test_different_strategies(self):
        """测试不同推理策略"""
        engine = SlowThinkingEngine()
        
        result_cot = engine.reason(
            "优化问题",
            strategy=ReasoningStrategy.CHAIN_OF_THOUGHT
        )
        result_tot = engine.reason(
            "优化问题",
            strategy=ReasoningStrategy.TREE_OF_THOUGHT
        )
        
        assert result_cot["strategy"] == "chain_of_thought"
        assert result_tot["strategy"] == "tree_of_thought"
    
    def test_validation_enabled(self):
        """测试验证功能"""
        engine = SlowThinkingEngine()
        result = engine.reason(
            "逻辑推理题",
            enable_validation=True
        )
        
        assert "validation" in result
        assert result["validation"] is not None
    
    def test_validation_disabled(self):
        """关闭验证"""
        engine = SlowThinkingEngine()
        result = engine.reason(
            "简单问题",
            enable_validation=False
        )
        
        assert result["validation"] is None
    
    def test_plan_and_execute(self):
        """规划并执行"""
        engine = SlowThinkingEngine()
        result = engine.plan_and_execute(
            "完成数据分析项目",
            plan_type="analysis"
        )
        
        assert "goal" in result
        assert "plan" in result
        assert "execution" in result
        assert "summary" in result
        assert result["execution"]["overall_success"] == True
    
    def test_compare_strategies(self):
        """比较不同策略"""
        engine = SlowThinkingEngine()
        strategies = [
            ReasoningStrategy.CHAIN_OF_THOUGHT,
            ReasoningStrategy.TREE_OF_THOUGHT
        ]
        
        result = engine.compare_strategies(
            "复杂优化问题",
            strategies
        )
        
        assert "comparison" in result
        assert "best_strategy" in result
        assert "recommendation" in result
        assert len(result["comparison"]) == 2
    
    def test_performance_metrics(self):
        """测试性能指标更新"""
        engine = SlowThinkingEngine()
        
        # 执行多次推理
        for i in range(5):
            engine.reason(f"问题{i}")
        
        metrics = engine.performance_metrics
        assert metrics["total_reasonings"] == 5
        assert metrics["avg_steps"] > 0
        assert metrics["avg_confidence"] > 0
        assert metrics["avg_time"] > 0
    
    def test_get_insights(self):
        """获取推理洞察"""
        engine = SlowThinkingEngine()
        
        # 先执行一些推理
        engine.reason("问题 1", ReasoningStrategy.CHAIN_OF_THOUGHT)
        engine.reason("问题 2", ReasoningStrategy.TREE_OF_THOUGHT)
        
        insights = engine.get_insights()
        
        assert insights["total_reasonings"] == 2
        assert "strategies_distribution" in insights
        assert "performance_metrics" in insights
        assert "recommendations" in insights
    
    def test_empty_history_insights(self):
        """空历史时的洞察"""
        engine = SlowThinkingEngine()
        insights = engine.get_insights()
        
        assert "message" in insights


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_deep_reason(self):
        """测试深度推理便捷函数"""
        result = deep_reason("计算斐波那契数列第 10 项")
        
        assert "conclusion" in result
        assert "confidence" in result
        assert "steps" in result
    
    def test_deep_reason_with_strategy(self):
        """指定策略的深度推理"""
        result = deep_reason(
            "优化算法",
            strategy="tree_of_thought"
        )
        
        assert result["strategy"] == "tree_of_thought"
    
    def test_plan_task(self):
        """测试任务规划便捷函数"""
        result = plan_task("开发新功能")
        
        assert "goal" in result
        assert "plan" in result
        assert "execution" in result


class TestIntegration:
    """集成测试"""
    
    def test_full_reasoning_pipeline(self):
        """完整推理流程"""
        engine = SlowThinkingEngine(config={
            "max_cot_steps": 15,
            "max_tot_depth": 8,
            "beam_width": 4
        })
        
        # 思维链推理
        result1 = engine.reason(
            "如果所有 A 都是 B，有些 B 是 C，那么有些 A 是 C 吗？",
            strategy=ReasoningStrategy.CHAIN_OF_THOUGHT
        )
        
        # 思维树推理
        result2 = engine.reason(
            "同样的逻辑问题",
            strategy=ReasoningStrategy.TREE_OF_THOUGHT
        )
        
        # 两者都应该有结果
        assert result1["conclusion"] is not None
        assert result2["conclusion"] is not None
        
        # 性能指标应该更新
        assert engine.performance_metrics["total_reasonings"] == 2
    
    def test_complex_planning(self):
        """复杂任务规划"""
        engine = SlowThinkingEngine()
        
        # 创建并执行复杂计划
        goal = "设计并实现一个推荐系统"
        result = engine.plan_and_execute(
            goal,
            plan_type="creative",
            context={"constraints": ["时间紧迫", "资源有限"]}
        )
        
        assert result["goal"] == goal
        assert len(result["plan"]) > 0
        assert result["execution"]["overall_success"] == True
    
    def test_iterative_reasoning(self):
        """迭代推理"""
        engine = SlowThinkingEngine()
        
        problems = [
            "数学问题 1",
            "逻辑问题 2",
            "优化问题 3"
        ]
        
        results = []
        for problem in problems:
            result = engine.reason(problem)
            results.append(result)
        
        # 所有问题都应该有结果
        assert len(results) == 3
        assert all(r["conclusion"] is not None for r in results)
        
        # 历史记录应该包含所有推理
        assert len(engine.reasoning_history) == 3


class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_problem(self):
        """空问题处理"""
        engine = SlowThinkingEngine()
        result = engine.reason("")
        
        assert result is not None
        assert "conclusion" in result
    
    def test_very_long_problem(self):
        """超长问题处理"""
        engine = SlowThinkingEngine()
        long_problem = "问题描述 " * 1000
        result = engine.reason(long_problem)
        
        assert result is not None
    
    def test_max_steps_limit(self):
        """最大步骤限制"""
        cot = ChainOfThought(max_steps=3)
        trace = cot.reason("复杂问题")
        
        assert len(trace.steps) <= 3
    
    def test_zero_confidence_threshold(self):
        """零置信度阈值"""
        cot = ChainOfThought(min_confidence=0.0)
        trace = cot.reason("任何问题")
        
        # 应该能完成推理而不过早终止
        assert len(trace.steps) > 0
    
    def test_concurrent_reasoning(self):
        """并发推理 (简化测试)"""
        engine = SlowThinkingEngine()
        
        # 快速执行多次推理
        start = time.time()
        for i in range(3):
            engine.reason(f"问题{i}")
        elapsed = time.time() - start
        
        # 应该在合理时间内完成
        assert elapsed < 10.0  # 根据实际性能调整


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
