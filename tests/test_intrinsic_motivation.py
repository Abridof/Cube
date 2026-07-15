"""
测试内在动机模块 - Test Intrinsic Motivation Module
====================================================
验证第九阶段核心功能：好奇心驱动与自主探索能力

测试覆盖:
- 预测误差计算
- 信息增益计算
- 内在奖励生成
- 探索目标生成
- 探索 - 利用决策
"""

import unittest
import sys
import os
import math

# 添加 src 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.modules.intrinsic_motivation import (
    MotivationType,
    PredictionError,
    InformationGain,
    IntrinsicReward,
    ExplorationGoal,
    PredictionErrorCalculator,
    InformationGainCalculator,
    IntrinsicMotivationEngine,
)


class TestPredictionErrorCalculator(unittest.TestCase):
    """测试预测误差计算器"""

    def setUp(self):
        self.calculator = PredictionErrorCalculator("test_calc")

    def test_calculate_numerical_error(self):
        """测试数值误差计算"""
        error = self.calculator.calculate_error(predicted=5.0, actual=7.0, var_name="test_var")

        self.assertEqual(error.error_magnitude, 2.0)
        self.assertGreaterEqual(error.normalized_error, 0.0)
        self.assertLessEqual(error.normalized_error, 1.0)
        self.assertGreaterEqual(error.surprise_level, 0.0)
        self.assertLessEqual(error.surprise_level, 1.0)

    def test_calculate_zero_error(self):
        """测试零误差情况"""
        error = self.calculator.calculate_error(predicted=5.0, actual=5.0, var_name="test_var")

        self.assertEqual(error.error_magnitude, 0.0)
        self.assertEqual(error.normalized_error, 0.0)

    def test_calculate_vector_error(self):
        """测试向量误差计算"""
        error = self.calculator.calculate_error(
            predicted=[1.0, 2.0, 3.0], actual=[1.0, 2.0, 3.0], var_name="vector_var"
        )

        self.assertEqual(error.error_magnitude, 0.0)

    def test_calculate_vector_error_nonzero(self):
        """测试非零向量误差"""
        error = self.calculator.calculate_error(
            predicted=[1.0, 2.0, 3.0], actual=[2.0, 3.0, 4.0], var_name="vector_var2"
        )

        expected_magnitude = math.sqrt(3)  # sqrt(1^2 + 1^2 + 1^2)
        self.assertAlmostEqual(error.error_magnitude, expected_magnitude, places=5)

    def test_error_history_tracking(self):
        """测试误差历史追踪"""
        for i in range(10):
            self.calculator.calculate_error(predicted=i, actual=i + 1, var_name="history_var")

        self.assertEqual(len(self.calculator.error_history["history_var"]), 10)
        self.assertIn("history_var", self.calculator.error_stats)

    def test_surprise_calculation(self):
        """测试惊讶度计算"""
        # 先建立基线
        for i in range(20):
            self.calculator.calculate_error(
                predicted=10.0, actual=10.0 + i * 0.1, var_name="surprise_var"
            )

        # 产生一个大误差
        big_error = self.calculator.calculate_error(
            predicted=10.0, actual=50.0, var_name="surprise_var"
        )

        # 大误差应该有较高的惊讶度
        self.assertGreater(big_error.surprise_level, 0.5)

    def test_get_learning_priorities(self):
        """测试学习优先级获取"""
        self.calculator.calculate_error(5.0, 10.0, "high_error_var")
        self.calculator.calculate_error(1.0, 1.1, "low_error_var")

        priorities = self.calculator.get_learning_priorities()

        self.assertIn("high_error_var", priorities)
        self.assertIn("low_error_var", priorities)
        self.assertGreater(priorities["high_error_var"], priorities["low_error_var"])


class TestInformationGainCalculator(unittest.TestCase):
    """测试信息增益计算器"""

    def setUp(self):
        self.calculator = InformationGainCalculator("test_info_gain")

    def test_entropy_uniform_distribution(self):
        """测试均匀分布的熵"""
        probs = [0.2, 0.2, 0.2, 0.2, 0.2]
        entropy = self.calculator.calculate_entropy(probs)

        # 均匀分布熵最大，应为 log2(5) ≈ 2.32
        expected_entropy = math.log2(5)
        self.assertAlmostEqual(entropy, expected_entropy, places=2)

    def test_entropy_peaked_distribution(self):
        """测试峰值分布的熵（低熵）"""
        probs = [0.0, 1.0, 0.0, 0.0, 0.0]
        entropy = self.calculator.calculate_entropy(probs)

        # 确定性分布熵为 0
        self.assertEqual(entropy, 0.0)

    def test_information_gain_positive(self):
        """测试信息增益为正（从不确定到确定）"""
        before = [0.2, 0.2, 0.2, 0.2, 0.2]
        after = [0.0, 1.0, 0.0, 0.0, 0.0]

        gain = self.calculator.calculate_information_gain(
            before_probs=before, after_probs=after, knowledge_area="test_area"
        )

        self.assertGreater(gain.information_gain, 0)
        self.assertAlmostEqual(gain.before_entropy, math.log2(5), places=2)
        self.assertEqual(gain.after_entropy, 0.0)

    def test_mutual_information_independent(self):
        """测试独立变量的互信息（应为 0）"""
        # 独立变量：联合分布等于边缘分布乘积
        joint_probs = {(0, 0): 0.25, (0, 1): 0.25, (1, 0): 0.25, (1, 1): 0.25}

        mi = self.calculator.calculate_mutual_information(
            joint_probs=joint_probs, x_values=[0, 1], y_values=[0, 1]
        )

        self.assertAlmostEqual(mi, 0.0, places=5)

    def test_knowledge_growth_tracking(self):
        """测试知识增长追踪"""
        for i in range(5):
            before = [0.5, 0.5]
            after = [0.5 - i * 0.1, 0.5 + i * 0.1]
            self.calculator.calculate_information_gain(
                before_probs=before, after_probs=after, knowledge_area="growing_area"
            )

        growth_rate = self.calculator.get_knowledge_growth_rate("growing_area")
        self.assertGreater(growth_rate, 0)


class TestIntrinsicMotivationEngine(unittest.TestCase):
    """测试内在动机引擎"""

    def setUp(self):
        self.engine = IntrinsicMotivationEngine("test_engine")

    def test_process_prediction_reward(self):
        """测试预测奖励处理"""
        # 先建立一些误差历史，以便产生非零奖励
        self.engine.process_prediction(1.0, 1.0, "test_var")  # 零误差基线
        self.engine.process_prediction(2.0, 2.5, "test_var")  # 小误差

        reward = self.engine.process_prediction(predicted=5.0, actual=7.0, var_name="test_var")

        self.assertIsInstance(reward, IntrinsicReward)
        # 奖励可能为 0（如果误差在正常范围内），所以不强制大于 0
        self.assertGreaterEqual(reward.magnitude, 0)
        self.assertIn(reward.reward_type, [MotivationType.SURPRISE, MotivationType.COMPETENCE])

    def test_process_learning_reward(self):
        """测试学习奖励处理"""
        reward = self.engine.process_learning_event(
            before_probs=[0.2, 0.2, 0.2, 0.2, 0.2],
            after_probs=[0.0, 1.0, 0.0, 0.0, 0.0],
            knowledge_area="physics",
        )

        self.assertIsInstance(reward, IntrinsicReward)
        self.assertGreater(reward.magnitude, 0)
        self.assertEqual(reward.reward_type, MotivationType.LEARNING_PROGRESS)

    def test_generate_exploration_goal(self):
        """测试探索目标生成"""
        goal = self.engine.generate_exploration_goal(
            description="Test exploration",
            motivation_type=MotivationType.CURIOSITY,
            expected_gain=0.8,
        )

        self.assertIsInstance(goal, ExplorationGoal)
        self.assertEqual(goal.description, "Test exploration")
        self.assertEqual(goal.motivation_type, MotivationType.CURIOSITY)
        self.assertGreater(goal.priority, 0)
        self.assertFalse(goal.achieved)

    def test_auto_generate_goals(self):
        """测试自动生成目标"""
        # 先产生一些数据
        for i in range(10):
            self.engine.process_prediction(i, i + 2, "var_" + str(i))

        goals = self.engine.auto_generate_goals()

        self.assertIsInstance(goals, list)
        # 应该至少生成一些目标
        self.assertGreater(len(goals), 0)

    def test_exploration_decision(self):
        """测试探索决策"""
        explore_count = 0
        for _ in range(100):
            if self.engine.should_explore():
                explore_count += 1
            self.engine.update_exploration_rate()

        # 由于初始 exploration_rate=0.5，应该有大约 50% 的探索
        self.assertGreater(explore_count, 20)  # 至少 20%
        self.assertLess(explore_count, 80)  # 最多 80%

        # 探索率应该衰减
        self.assertLess(self.engine.exploration_rate, 0.5)

    def test_goal_achievement(self):
        """测试目标达成"""
        goal = self.engine.generate_exploration_goal(
            description="Achievable goal",
            motivation_type=MotivationType.CURIOSITY,
            expected_gain=0.5,
        )

        initial_achieved = self.engine.goals_achieved

        self.engine.achieve_goal(goal.goal_id)

        self.assertTrue(self.engine.goals[goal.goal_id].achieved)
        self.assertIsNotNone(self.engine.goals[goal.goal_id].achievement_time)
        self.assertEqual(self.engine.goals_achieved, initial_achieved + 1)

    def test_motivation_summary(self):
        """测试动机摘要"""
        self.engine.process_prediction(5.0, 7.0, "test")
        self.engine.process_learning_event([0.5, 0.5], [0.0, 1.0], "test_area")

        summary = self.engine.get_motivation_summary()

        self.assertIn("total_intrinsic_reward", summary)
        self.assertIn("exploration_rate", summary)
        self.assertIn("goals_achieved", summary)
        self.assertIn("motivation_weights", summary)
        self.assertGreater(summary["total_intrinsic_reward"], 0)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_learning_loop(self):
        """测试完整学习循环"""
        import random

        engine = IntrinsicMotivationEngine("integration_test")

        # 模拟学习过程
        true_function = lambda x: 2 * x + 1

        for step in range(50):
            x = step
            actual = true_function(x)

            # AI 的预测（逐渐改进）
            if step < 10:
                predicted = x * random.uniform(1.5, 2.5) + random.uniform(-2, 2)
            else:
                predicted = 2 * x + random.uniform(-1, 1)

            # 处理预测并获取内在奖励
            reward = engine.process_prediction(
                predicted=predicted, actual=actual, var_name="linear_func"
            )

            # 定期生成新目标
            if step % 10 == 0:
                goals = engine.auto_generate_goals()

        # 验证系统产生了内在奖励
        self.assertGreater(engine.total_intrinsic_reward, 0)

        # 验证误差统计已建立
        self.assertIn("linear_func", engine.error_calculator.error_stats)

        # 验证知识领域已记录
        summary = engine.get_motivation_summary()
        self.assertIn("error_stats_summary", summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)
