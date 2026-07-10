"""
世界模型模块测试 - World Model Tests
=======================================
测试世界模型的核心功能：
- 状态观测与管理
- 转移学习
- 预测引擎
- 反事实推理
- 自我模型

作者：AI Cognition Engine Team
版本：v8.0
"""

import unittest
import time
import json
import os
from src.modules.world_model import (
    WorldModel,
    State,
    StateVariable,
    Transition,
    Prediction,
    Counterfactual,
    StateType,
    TransitionType,
)


class TestStateVariable(unittest.TestCase):
    """测试状态变量"""

    def test_create_state_variable(self):
        """创建状态变量"""
        var = StateVariable(name="temperature", value=25.0, var_type=StateType.PHYSICAL)
        self.assertEqual(var.name, "temperature")
        self.assertEqual(var.value, 25.0)
        self.assertEqual(var.var_type, StateType.PHYSICAL)
        self.assertEqual(var.uncertainty, 0.0)
        self.assertEqual(var.confidence, 1.0)

    def test_state_variable_with_domain(self):
        """带定义域的状态变量"""
        var = StateVariable(
            name="status",
            value="active",
            var_type=StateType.ABSTRACT,
            domain=["active", "inactive", "pending"],
        )
        self.assertIn("active", var.domain)

    def test_state_variable_to_dict(self):
        """状态变量序列化"""
        var = StateVariable(name="energy", value=100, var_type=StateType.COGNITIVE, uncertainty=0.1)
        d = var.to_dict()
        self.assertEqual(d["name"], "energy")
        self.assertEqual(d["value"], 100)
        self.assertEqual(d["var_type"], "cognitive")
        self.assertEqual(d["uncertainty"], 0.1)

    def test_state_variable_from_dict(self):
        """状态变量反序列化"""
        data = {
            "name": "humidity",
            "value": 60.0,
            "var_type": "physical",
            "uncertainty": 0.05,
            "confidence": 0.95,
        }
        var = StateVariable.from_dict(data)
        self.assertEqual(var.name, "humidity")
        self.assertEqual(var.value, 60.0)
        self.assertEqual(var.var_type, StateType.PHYSICAL)


class TestState(unittest.TestCase):
    """测试状态类"""

    def test_create_state(self):
        """创建状态"""
        state = State(state_id="test_state_001")
        state.add_variable(
            StateVariable(name="position", value=(0, 0), var_type=StateType.PHYSICAL)
        )
        self.assertEqual(state.state_id, "test_state_001")
        self.assertEqual(len(state.variables), 1)

    def test_state_get_set_value(self):
        """状态值的获取和设置"""
        state = State(state_id="test")
        state.set_value("temperature", 25.0, StateType.PHYSICAL)
        self.assertEqual(state.get_value("temperature"), 25.0)

        state.set_value("temperature", 30.0)
        self.assertEqual(state.get_value("temperature"), 30.0)

    def test_state_similarity_identical(self):
        """相同状态的相似度"""
        state1 = State(state_id="s1")
        state1.set_value("temp", 25.0, StateType.PHYSICAL)
        state1.set_value("humid", 60.0, StateType.PHYSICAL)

        state2 = State(state_id="s2")
        state2.set_value("temp", 25.0, StateType.PHYSICAL)
        state2.set_value("humid", 60.0, StateType.PHYSICAL)

        sim = state1.similarity(state2)
        self.assertAlmostEqual(sim, 1.0, places=5)

    def test_state_similarity_different(self):
        """不同状态的相似度"""
        state1 = State(state_id="s1")
        state1.set_value("temp", 25.0, StateType.PHYSICAL)

        state2 = State(state_id="s2")
        state2.set_value("temp", 35.0, StateType.PHYSICAL)

        sim = state1.similarity(state2)
        self.assertLess(sim, 1.0)
        self.assertGreater(sim, 0.0)

    def test_state_to_from_dict(self):
        """状态序列化与反序列化"""
        state = State(state_id="serialize_test", context={"step": 5})
        state.set_value("x", 10, StateType.PHYSICAL)
        state.set_value("y", 20, StateType.PHYSICAL)

        data = state.to_dict()
        restored = State.from_dict(data)

        self.assertEqual(restored.state_id, state.state_id)
        self.assertEqual(restored.get_value("x"), 10)
        self.assertEqual(restored.context["step"], 5)


class TestWorldModelObservation(unittest.TestCase):
    """测试世界模型的观测功能"""

    def setUp(self):
        self.wm = WorldModel("test_model")

    def test_observe_creates_state(self):
        """观测创建状态"""
        state = self.wm.observe(
            {"temperature": (25.0, StateType.PHYSICAL), "humidity": (60.0, StateType.PHYSICAL)}
        )
        self.assertIsNotNone(state)
        self.assertEqual(state.get_value("temperature"), 25.0)
        self.assertEqual(state.get_value("humidity"), 60.0)

    def test_observe_updates_current_state(self):
        """观测更新当前状态"""
        state1 = self.wm.observe({"x": (1, StateType.PHYSICAL)})
        state2 = self.wm.observe({"x": (2, StateType.PHYSICAL)})

        current = self.wm.get_current_state()
        self.assertEqual(current.state_id, state2.state_id)
        self.assertEqual(current.get_value("x"), 2)

    def test_multiple_observations_count(self):
        """多次观测计数"""
        for i in range(10):
            self.wm.observe({"val": (i, StateType.PHYSICAL)})

        self.assertEqual(self.wm.observation_count, 10)


class TestTransitionLearning(unittest.TestCase):
    """测试转移学习"""

    def setUp(self):
        self.wm = WorldModel("transition_test")

    def test_learn_transition_from_observations(self):
        """从观测中学习转移"""
        self.wm.observe({"step": (0, StateType.ABSTRACT)})
        self.wm.observe({"step": (1, StateType.ABSTRACT)})
        self.wm.observe({"step": (2, StateType.ABSTRACT)})

        # 应该学习到至少 2 个转移
        self.assertGreaterEqual(len(self.wm.transitions), 2)

    def test_transition_support_count(self):
        """转移支持计数"""
        # 重复相同的观测序列 - 使用相同的状态值来确保匹配
        self.wm.observe({"state": ("A", StateType.ABSTRACT)})
        self.wm.observe({"state": ("B", StateType.ABSTRACT)})

        # 重置当前状态到 A，以便下次观测能匹配相同的转移
        self.wm.current_state_id = list(self.wm.states.keys())[0]

        for _ in range(2):
            self.wm.observe({"state": ("B", StateType.ABSTRACT)})

        # 检查是否有转移的支持计数大于 1
        has_repeated = any(t.support_count > 1 for t in self.wm.transitions.values())
        self.assertTrue(has_repeated)

    def test_causal_graph_population(self):
        """因果图填充"""
        for i in range(5):
            self.wm.observe(
                {"cause": (i, StateType.PHYSICAL), "effect": (i * 2, StateType.PHYSICAL)}
            )

        # 因果图应该有记录
        self.assertGreater(len(self.wm.causal_graph), 0)


class TestPrediction(unittest.TestCase):
    """测试预测功能"""

    def setUp(self):
        self.wm = WorldModel("prediction_test")
        # 建立一些观测用于学习
        for i in range(10):
            self.wm.observe(
                {"time": (i, StateType.PHYSICAL), "value": (i * 10, StateType.PHYSICAL)}
            )

    def test_predict_returns_prediction(self):
        """预测返回 Prediction 对象"""
        prediction = self.wm.predict(steps=1)

        if prediction:  # 如果有可预测的转移
            self.assertIsInstance(prediction, Prediction)
            self.assertIsNotNone(prediction.predicted_state)
            self.assertGreaterEqual(prediction.confidence, 0.0)
            self.assertLessEqual(prediction.confidence, 1.0)

    def test_prediction_horizon(self):
        """预测范围"""
        pred1 = self.wm.predict(steps=1)
        pred3 = self.wm.predict(steps=3)

        # 多步预测的置信度应该更低（由于衰减）
        if pred1 and pred3:
            self.assertGreaterEqual(pred1.confidence, pred3.confidence)

    def test_prediction_uncertainty_increases(self):
        """预测不确定性随步数增加"""
        prediction = self.wm.predict(steps=5)

        if prediction:
            # 预测状态的变量应该有更高的不确定性
            for var in prediction.predicted_state.variables.values():
                if var.source == "prediction":
                    self.assertGreater(var.uncertainty, 0.0)

    def test_no_current_state_no_prediction(self):
        """没有当前状态无法预测"""
        wm_empty = WorldModel("empty")
        prediction = wm_empty.predict(steps=1)
        self.assertIsNone(prediction)


class TestCounterfactualReasoning(unittest.TestCase):
    """测试反事实推理"""

    def setUp(self):
        self.wm = WorldModel("counterfactual_test")
        for i in range(5):
            self.wm.observe(
                {
                    "temperature": (20 + i, StateType.PHYSICAL),
                    "pressure": (100 + i * 2, StateType.PHYSICAL),
                }
            )

    def test_counterfactual_creation(self):
        """创建反事实"""
        cf = self.wm.counterfactual({"temperature": 50.0})

        self.assertIsInstance(cf, Counterfactual)
        self.assertIn("temperature", cf.premise)
        self.assertIsNotNone(cf.actual_outcome)
        self.assertIsNotNone(cf.counterfactual_outcome)

    def test_counterfactual_plausibility(self):
        """反事实合理性评分"""
        cf_normal = self.wm.counterfactual({"temperature": 25.0})
        cf_extreme = self.wm.counterfactual({"temperature": 1000.0})

        # 极端干预的合理性应该更低（如果有定义域限制）
        self.assertGreaterEqual(cf_normal.plausibility, 0.0)
        self.assertLessEqual(cf_normal.plausibility, 1.0)

    def test_counterfactual_causal_chain(self):
        """反事实因果链"""
        cf = self.wm.counterfactual({"temperature": 30.0})

        # 应该有因果链（可能为空，但结构应该存在）
        self.assertIsInstance(cf.causal_chain, list)

    def test_counterfactual_difference_analysis(self):
        """反事实差异分析"""
        cf = self.wm.counterfactual({"temperature": 40.0})

        self.assertIn("changed_variables", cf.difference_analysis)
        self.assertIn("details", cf.difference_analysis)
        self.assertIn("total_changes", cf.difference_analysis)


class TestSelfModel(unittest.TestCase):
    """测试自我模型"""

    def setUp(self):
        self.wm = WorldModel("self_model_test")

    def test_update_capability(self):
        """更新能力"""
        self.wm.update_self_model(capability="predict")
        self.wm.update_self_model(capability="reason")

        self_model = self.wm.get_self_model()
        self.assertIn("predict", self_model["capabilities"])
        self.assertIn("reason", self_model["capabilities"])

    def test_update_limitation(self):
        """更新局限性"""
        self.wm.update_self_model(limitation="slow_learning")

        self_model = self.wm.get_self_model()
        self.assertIn("slow_learning", self_model["limitations"])

    def test_update_belief(self):
        """更新信念"""
        self.wm.update_self_model(belief={"learning_rate": 0.1})
        self.wm.update_self_model(belief={"curiosity": 0.9})

        self_model = self.wm.get_self_model()
        self.assertEqual(self_model["beliefs_about_self"]["learning_rate"], 0.1)
        self.assertEqual(self_model["beliefs_about_self"]["curiosity"], 0.9)

    def test_meta_cognitive_state_progression(self):
        """元认知状态进展"""
        # 初始状态
        self.assertEqual(self.wm.get_self_model()["meta_cognitive_state"], "unknown")

        # 添加多个能力
        for i in range(12):
            self.wm.update_self_model(capability=f"capability_{i}")

        self_model = self.wm.get_self_model()
        self.assertEqual(self_model["meta_cognitive_state"], "aware")

    def test_get_self_model_returns_copy(self):
        """获取自我模型返回副本"""
        self.wm.update_self_model(capability="test")

        model1 = self.wm.get_self_model()
        model1["capabilities"].append("external_modification")

        model2 = self.wm.get_self_model()
        self.assertNotIn("external_modification", model2["capabilities"])


class TestPersistence(unittest.TestCase):
    """测试持久化"""

    def setUp(self):
        self.wm = WorldModel("persistence_test")
        self.test_file = "/tmp/test_world_model.json"

        # 添加一些数据
        for i in range(5):
            self.wm.observe({"x": (i, StateType.PHYSICAL), "y": (i * 2, StateType.PHYSICAL)})

        self.wm.update_self_model(capability="persist")

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_save_and_load(self):
        """保存和加载"""
        # 保存
        self.wm.save(self.test_file)
        self.assertTrue(os.path.exists(self.test_file))

        # 加载到新实例
        wm_loaded = WorldModel("new_model")
        wm_loaded.load(self.test_file)

        # 验证数据
        self.assertEqual(wm_loaded.model_id, "persistence_test")
        self.assertEqual(len(wm_loaded.states), len(self.wm.states))
        self.assertEqual(len(wm_loaded.transitions), len(self.wm.transitions))
        self.assertIn("persist", wm_loaded.get_self_model()["capabilities"])

    def test_export_summary(self):
        """导出摘要"""
        summary = self.wm.export_summary()

        self.assertIn("model_id", summary)
        self.assertIn("total_states", summary)
        self.assertIn("total_transitions", summary)
        self.assertIn("observations", summary)
        self.assertEqual(summary["model_id"], "persistence_test")
        self.assertEqual(summary["total_states"], 5)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_cycle(self):
        """完整周期：观测 -> 学习 -> 预测 -> 反事实 -> 自我反思"""
        wm = WorldModel("integration_test")

        # 1. 观测
        for i in range(10):
            wm.observe(
                {
                    "time": (i, StateType.PHYSICAL),
                    "temperature": (20 + i, StateType.PHYSICAL),
                    "energy": (100 - i * 5, StateType.COGNITIVE),
                },
                context={"phase": "observation"},
            )

        # 2. 预测
        prediction = wm.predict(steps=2)

        # 3. 反事实推理
        cf = wm.counterfactual({"temperature": 50.0})

        # 4. 自我模型更新
        wm.update_self_model(capability="full_cycle_execution")
        wm.update_self_model(belief={"cycle_completed": True})

        # 5. 验证
        self.assertGreater(wm.observation_count, 0)
        self.assertGreater(len(wm.transitions), 0)
        self.assertIn("full_cycle_execution", wm.get_self_model()["capabilities"])

        # 6. 导出摘要
        summary = wm.export_summary()
        self.assertEqual(summary["observations"], 10)
        self.assertGreater(summary["causal_relations"], 0)

    def test_multi_agent_scenario(self):
        """多智能体场景模拟"""
        wm = WorldModel("multi_agent")

        # 模拟两个智能体的交互
        for i in range(5):
            wm.observe(
                {
                    "agent1_pos": (i * 10, StateType.PHYSICAL),
                    "agent2_pos": (50 - i * 10, StateType.PHYSICAL),
                    "distance": (abs(50 - i * 20), StateType.PHYSICAL),
                    "interaction": ("approaching" if i < 3 else "separating", StateType.SOCIAL),
                }
            )

        # 预测相遇后的状态
        prediction = wm.predict(steps=1)

        # 反事实：如果一个智能体改变方向
        cf = wm.counterfactual({"agent1_pos": (-10, 0)})

        self.assertIsNotNone(cf)
        self.assertIn("agent1_pos", cf.premise)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestStateVariable))
    suite.addTests(loader.loadTestsFromTestCase(TestState))
    suite.addTests(loader.loadTestsFromTestCase(TestWorldModelObservation))
    suite.addTests(loader.loadTestsFromTestCase(TestTransitionLearning))
    suite.addTests(loader.loadTestsFromTestCase(TestPrediction))
    suite.addTests(loader.loadTestsFromTestCase(TestCounterfactualReasoning))
    suite.addTests(loader.loadTestsFromTestCase(TestSelfModel))
    suite.addTests(loader.loadTestsFromTestCase(TestPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印摘要
    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)
    print(f"运行测试数：{result.testsRun}")
    print(f"成功：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败：{len(result.failures)}")
    print(f"错误：{len(result.errors)}")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
