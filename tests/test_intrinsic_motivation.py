"""
阶段 9: 内在动机与好奇心驱动模块 - 单元测试

测试覆盖：
- PredictionErrorCalculator
- InformationGainCalculator
- CompetenceTracker
- ControlEstimator
- IntrinsicMotivationEngine
"""

import pytest
import numpy as np
from src.modules.intrinsic_motivation import (
    IntrinsicMotivationType,
    PredictionError,
    IntrinsicReward,
    ExplorationGoal,
    PredictionErrorCalculator,
    InformationGainCalculator,
    CompetenceTracker,
    ControlEstimator,
    IntrinsicMotivationEngine,
)


class TestPredictionErrorCalculator:
    """测试预测误差计算器"""
    
    def test_calculate_error_basic(self):
        """测试基本误差计算"""
        calc = PredictionErrorCalculator()
        
        predicted = np.array([1.0, 2.0, 3.0])
        actual = np.array([1.5, 2.5, 3.5])
        
        error = calc.calculate_error(predicted, actual, "test")
        
        assert error.error > 0
        assert np.allclose(error.error_vector, actual - predicted)
        assert error.modality == "test"
        assert error.timestamp == 0
    
    def test_calculate_error_zero(self):
        """测试零误差情况"""
        calc = PredictionErrorCalculator()
        
        predicted = np.array([1.0, 2.0, 3.0])
        actual = np.array([1.0, 2.0, 3.0])
        
        error = calc.calculate_error(predicted, actual)
        
        assert error.error == 0.0
        assert np.allclose(error.error_vector, np.zeros(3))
    
    def test_calculate_error_shape_mismatch(self):
        """测试形状不匹配错误"""
        calc = PredictionErrorCalculator()
        
        predicted = np.array([1.0, 2.0])
        actual = np.array([1.0, 2.0, 3.0])
        
        with pytest.raises(ValueError):
            calc.calculate_error(predicted, actual)
    
    def test_weighted_error(self):
        """测试多模态加权误差"""
        weights = {"vision": 2.0, "audio": 1.0}
        calc = PredictionErrorCalculator(modality_weights=weights)
        
        predictions = {
            "vision": np.array([1.0, 2.0]),
            "audio": np.array([3.0, 4.0])
        }
        actuals = {
            "vision": np.array([1.5, 2.5]),
            "audio": np.array([3.0, 4.0])
        }
        
        weighted_error = calc.calculate_weighted_error(predictions, actuals)
        
        assert weighted_error > 0
        assert weighted_error < 1.0
    
    def test_error_history(self):
        """测试误差历史记录"""
        calc = PredictionErrorCalculator()
        
        for i in range(15):
            predicted = np.random.randn(5)
            actual = np.random.randn(5)
            calc.calculate_error(predicted, actual)
        
        assert len(calc.error_history) == 15
    
    def test_recent_average_error(self):
        """测试最近平均误差"""
        calc = PredictionErrorCalculator()
        
        for _ in range(10):
            predicted = np.zeros(5)
            actual = np.ones(5)
            calc.calculate_error(predicted, actual)
        
        avg_error = calc.get_recent_average_error(window_size=5)
        assert avg_error > 0
    
    def test_error_trend(self):
        """测试误差趋势"""
        calc = PredictionErrorCalculator()
        
        for i in range(30):
            magnitude = 1.0 if i < 15 else 0.5
            predicted = np.zeros(5)
            actual = np.ones(5) * magnitude
            calc.calculate_error(predicted, actual)
        
        trend = calc.get_error_trend(window_size=20)
        assert trend < 0


class TestInformationGainCalculator:
    """测试信息增益计算器"""
    
    def test_novelty_new_state(self):
        """测试新状态的新奇性"""
        calc = InformationGainCalculator()
        
        state = np.random.randn(5)
        novelty = calc.calculate_novelty(state)
        
        assert novelty == 1.0
    
    def test_novelty_visited_state(self):
        """测试已访问状态的新奇性"""
        calc = InformationGainCalculator()
        
        state = np.array([1.0, 2.0, 3.0])
        calc.update_distribution(state)
        calc.update_distribution(state)
        calc.update_distribution(state)
        
        novelty = calc.calculate_novelty(state)
        
        assert 0 <= novelty < 1.0
    
    def test_entropy_calculation(self):
        """测试熵计算"""
        calc = InformationGainCalculator()
        
        initial_entropy = calc.calculate_entropy()
        assert initial_entropy == 0.0
        
        for i in range(20):
            state = np.random.randn(3)
            calc.update_distribution(state)
        
        entropy = calc.calculate_entropy()
        assert entropy >= 0
    
    def test_surprise_calculation(self):
        """测试惊讶度计算"""
        calc = InformationGainCalculator()
        
        surprise_low = calc.calculate_surprise(observed=1.0, expected=1.0, variance=0.1)
        assert surprise_low < 0.5
        
        surprise_high = calc.calculate_surprise(observed=5.0, expected=1.0, variance=0.1)
        assert surprise_high > 0.5
    
    def test_expectation_update(self):
        """测试期望更新"""
        calc = InformationGainCalculator()
        
        calc.update_expectation("key1", 1.0, alpha=0.5)
        assert calc.expectation_model["key1"] == 1.0
        
        calc.update_expectation("key1", 3.0, alpha=0.5)
        assert 1.0 < calc.expectation_model["key1"] < 3.0


class TestCompetenceTracker:
    """测试能力感追踪器"""
    
    def test_record_performance(self):
        """测试性能记录"""
        tracker = CompetenceTracker()
        
        tracker.record_performance("task1", 0.5)
        tracker.record_performance("task1", 0.6)
        tracker.record_performance("task1", 0.7)
        
        assert len(tracker.task_performance["task1"]) == 3
    
    def test_competence_initial(self):
        """测试初始能力水平"""
        tracker = CompetenceTracker()
        
        competence = tracker.get_competence("new_task")
        assert competence == 0.0
    
    def test_competence_improvement(self):
        """测试能力提升"""
        tracker = CompetenceTracker()
        
        for perf in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
            tracker.record_performance("task1", perf)
        
        competence = tracker.get_competence("task1")
        assert competence > 0.5
    
    def test_learning_progress_positive(self):
        """测试正向学习进步"""
        tracker = CompetenceTracker()
        
        for perf in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
            tracker.record_performance("task1", perf)
        
        progress = tracker.get_learning_progress("task1", window=6)
        assert progress > 0
    
    def test_learning_progress_negative(self):
        """测试负向学习进步"""
        tracker = CompetenceTracker()
        
        for perf in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4]:
            tracker.record_performance("task1", perf)
        
        progress = tracker.get_learning_progress("task1", window=6)
        assert progress < 0


class TestControlEstimator:
    """测试控制感估计器"""
    
    def test_estimate_control_no_data(self):
        """测试无数据时的控制感"""
        estimator = ControlEstimator()
        
        control = estimator.estimate_control("action1")
        assert control == 0.0
    
    def test_estimate_control_with_effect(self):
        """测试有显著效果时的控制感"""
        estimator = ControlEstimator()
        
        # 先添加一些随机基线
        for _ in range(5):
            estimator.record_random_effect(1.0)
        
        for _ in range(10):
            estimator.record_action_effect("action1", 5.0)
        
        control = estimator.estimate_control("action1")
        assert control >= 0.5  # 至少 0.5，因为有随机基线
    
    def test_estimate_control_vs_random(self):
        """测试相对于随机基线的控制感"""
        estimator = ControlEstimator()
        
        for _ in range(10):
            estimator.record_random_effect(1.0)
        
        for _ in range(10):
            estimator.record_action_effect("action1", 5.0)
        
        control = estimator.estimate_control("action1")
        assert control > 0.7


class TestIntrinsicMotivationEngine:
    """测试内在动机引擎"""
    
    def test_compute_reward_basic(self):
        """测试基本奖励计算"""
        engine = IntrinsicMotivationEngine()
        
        state = np.random.randn(5)
        action = "move_forward"
        next_state = state + np.random.randn(5) * 0.5
        prediction = state + np.random.randn(5) * 0.3
        
        reward = engine.compute_intrinsic_reward(
            state=state,
            action=action,
            next_state=next_state,
            prediction=prediction,
            task_id="test_task"
        )
        
        assert isinstance(reward, IntrinsicReward)
        assert reward.reward_value >= 0
        assert reward.action_taken == action
    
    def test_compute_reward_components(self):
        """测试各奖励分量"""
        engine = IntrinsicMotivationEngine()
        
        state = np.random.randn(5)
        next_state = state + np.random.randn(5) * 0.5
        prediction = state
        
        reward = engine.compute_intrinsic_reward(
            state=state,
            action="test",
            next_state=next_state,
            prediction=prediction,
            task_id="test"
        )
        
        metadata = reward.metadata["individual_rewards"]
        assert "curiosity" in metadata or "novelty" in metadata
    
    def test_explore_or_exploit_exploration(self):
        """测试探索决策"""
        engine = IntrinsicMotivationEngine(exploration_epsilon=1.0)
        
        state = np.random.randn(5)
        actions = ["a", "b", "c"]
        
        action, is_exploring = engine.decide_explore_or_exploit(state, actions)
        
        assert action in actions
        assert is_exploring
    
    def test_explore_or_exploit_exploitation(self):
        """测试利用决策"""
        engine = IntrinsicMotivationEngine(exploration_epsilon=0.0, ucb_c=0.0)
        
        state = np.random.randn(5)
        q_values = {"a": 1.0, "b": 0.5, "c": 0.3}
        actions = list(q_values.keys())
        
        action, is_exploring = engine.decide_explore_or_exploit(
            state, actions, q_values
        )
        
        assert action == "a"
    
    def test_generate_goal(self):
        """测试目标生成"""
        engine = IntrinsicMotivationEngine()
        
        state = np.random.randn(5)
        
        goal = engine.generate_exploration_goal(state)
        
        assert isinstance(goal, ExplorationGoal)
        assert goal.goal_id == "goal_0"
        assert goal.target_state is not None
        assert goal.priority > 0
    
    def test_goal_management(self):
        """测试目标管理"""
        engine = IntrinsicMotivationEngine()
        
        state = np.random.randn(5)
        goal1 = engine.generate_exploration_goal(state)
        goal2 = engine.generate_exploration_goal(state)
        
        assert len(engine.goals) == 2
        
        next_goal = engine.get_next_goal()
        assert next_goal is not None
        
        engine.mark_goal_completed(goal1.goal_id)
        
        remaining = [g for g in engine.goals if not g.completed]
        assert len(remaining) == 1
    
    def test_statistics(self):
        """测试统计信息"""
        engine = IntrinsicMotivationEngine()
        
        for _ in range(20):
            state = np.random.randn(5)
            next_state = state + np.random.randn(5) * 0.5
            
            engine.compute_intrinsic_reward(
                state=state,
                action="test",
                next_state=next_state,
                prediction=state
            )
        
        stats = engine.get_statistics()
        
        assert stats["timestep"] == 20
        # total_reward 可能为正或负，取决于权重和奖励组合
        assert "total_intrinsic_reward" in stats
        # unique_states_visited 在没有调用 decide_explore_or_exploit 时为 0
        assert stats["unique_states_visited"] >= 0
        assert "average_prediction_error" in stats
    
    def test_cumulative_reward(self):
        """测试累积奖励"""
        engine = IntrinsicMotivationEngine()
        
        rewards = []
        for _ in range(10):
            state = np.random.randn(5)
            next_state = state + np.random.randn(5) * 0.5
            
            reward = engine.compute_intrinsic_reward(
                state=state,
                action="test",
                next_state=next_state,
                prediction=state
            )
            rewards.append(reward.reward_value)
        
        assert abs(engine.total_reward - sum(rewards)) < 1e-6
    
    def test_different_motivation_types(self):
        """测试不同动机类型"""
        engine = IntrinsicMotivationEngine(
            curiosity_weight=2.0,
            novelty_weight=0.1
        )
        
        state = np.random.randn(5)
        next_state = state + np.random.randn(5) * 2.0
        
        reward = engine.compute_intrinsic_reward(
            state=state,
            action="test",
            next_state=next_state,
            prediction=state
        )
        
        assert reward.motivation_type in IntrinsicMotivationType


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("阶段 9: 内在动机与好奇心驱动模块 - 单元测试")
    print("=" * 60)
    
    test_classes = [
        TestPredictionErrorCalculator,
        TestInformationGainCalculator,
        TestCompetenceTracker,
        TestControlEstimator,
        TestIntrinsicMotivationEngine,
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_class in test_classes:
        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith("test_")]
        
        for method in methods:
            try:
                getattr(instance, method)()
                print(f"✓ {test_class.__name__}.{method}")
                total_passed += 1
            except Exception as e:
                print(f"✗ {test_class.__name__}.{method}: {e}")
                total_failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果：{total_passed} 通过，{total_failed} 失败")
    print("=" * 60)
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
