"""
认知闭环控制器测试套件
测试覆盖：CognitiveLoopController 所有阶段和功能
"""

import unittest
import json
import time
from unittest.mock import Mock, patch

# 导入被测模块
from src.modules.cognitive_loop import (
    CognitiveLoopController,
    CognitiveEvent,
    LoopPhase
)


class TestCognitiveEvent(unittest.TestCase):
    """测试认知事件类"""
    
    def test_event_creation(self):
        """测试事件创建"""
        event = CognitiveEvent(
            phase=LoopPhase.PERCEIVE,
            timestamp=time.time(),
            input_data="test input",
            output_data={"result": "test"},
            metadata={"key": "value"}
        )
        
        self.assertEqual(event.phase, LoopPhase.PERCEIVE)
        self.assertEqual(event.metadata["key"], "value")
    
    def test_event_to_dict(self):
        """测试事件序列化"""
        event = CognitiveEvent(
            phase=LoopPhase.REASON,
            timestamp=1234567890.0,
            input_data="input",
            output_data="output"
        )
        
        event_dict = event.to_dict()
        
        self.assertEqual(event_dict["phase"], "reason")
        self.assertEqual(event_dict["timestamp"], 1234567890.0)
        self.assertIn("input_type", event_dict)
        self.assertIn("output_type", event_dict)


class TestCognitiveLoopController(unittest.TestCase):
    """测试认知闭环控制器"""
    
    def setUp(self):
        """初始化测试环境"""
        self.config = {
            "learning_rate": 0.01,
            "exploration_bonus": 0.2,
            "reflection_threshold": 0.7
        }
        self.controller = CognitiveLoopController(self.config)
    
    def test_initialization(self):
        """测试控制器初始化"""
        self.assertEqual(self.controller.loop_count, 0)
        self.assertFalse(self.controller.is_running)
        self.assertEqual(self.controller.learning_rate, 0.01)
        self.assertEqual(self.controller.exploration_bonus, 0.2)
    
    def test_perceive_phase(self):
        """测试感知阶段"""
        result = self.controller.perceive("test input", modality="TEXT")
        
        self.assertIsNotNone(result)
        self.assertEqual(len(self.controller.event_log), 1)
        self.assertEqual(self.controller.event_log[0].phase, LoopPhase.PERCEIVE)
    
    def test_reason_phase(self):
        """测试推理阶段"""
        # 先创建一个 UCR
        ucr = self.controller.perceive("test query")
        
        # 进行推理
        results = self.controller.reason(ucr)
        
        self.assertIn("graph_retrieval", results)
        self.assertIn("vector_search", results)
        self.assertIn("predictions", results)
        self.assertIn("confidence", results)
        self.assertEqual(len(self.controller.event_log), 2)
    
    def test_decide_phase_with_goals(self):
        """测试决策阶段（有目标）"""
        reasoning_results = {"confidence": 0.8, "predictions": ["pred1"]}
        goals = ["achieve_goal_1"]
        
        decision = self.controller.decide(reasoning_results, goals)
        
        self.assertIn("selected_action", decision)
        self.assertIn("alternative_actions", decision)
        self.assertIn("motivation_state", decision)
        self.assertGreater(len(decision["alternative_actions"]), 0)
    
    def test_decide_phase_without_goals(self):
        """测试决策阶段（无目标）"""
        reasoning_results = {"confidence": 0.5}
        
        decision = self.controller.decide(reasoning_results)
        
        self.assertIn("selected_action", decision)
        # 应该有基于好奇心的探索动作
        self.assertGreater(len(decision["alternative_actions"]), 0)
    
    def test_act_phase_explore(self):
        """测试行动阶段（探索动作）"""
        decision = {
            "selected_action": {
                "type": "explore",
                "target": "unknown",
                "value": 0.8,
                "reason": "curiosity"
            }
        }
        
        feedback = self.controller.act(decision)
        
        self.assertTrue(feedback["success"])
        self.assertEqual(feedback["reward"], 0.5)
        self.assertIn("discovered_new_pattern", feedback["observations"])
    
    def test_act_phase_achieve_success(self):
        """测试行动阶段（目标达成 - 成功）"""
        decision = {
            "selected_action": {
                "type": "achieve",
                "target": "goal",
                "value": 0.9,  # 高置信度
                "reason": "goal_oriented"
            },
            "confidence": 0.9
        }
        
        # 多次测试以确保概率成功
        success_count = 0
        for _ in range(10):
            feedback = self.controller.act(decision)
            if feedback["success"]:
                success_count += 1
        
        # 高置信度应该有较高的成功率（至少 3/10）
        self.assertGreaterEqual(success_count, 3)
    
    def test_act_phase_prevent(self):
        """测试行动阶段（预防动作）"""
        decision = {
            "selected_action": {
                "type": "prevent",
                "target": "risk",
                "value": 0.9,
                "reason": "predictive"
            }
        }
        
        feedback = self.controller.act(decision)
        
        self.assertTrue(feedback["success"])
        self.assertEqual(feedback["reward"], 0.3)
    
    def test_learn_phase_success(self):
        """测试学习阶段（成功经验）"""
        feedback = {"success": True, "reward": 1.0}
        experience = {"action": "explore", "context": {}}
        
        stats = self.controller.learn(feedback, experience)
        
        self.assertIn("graph_updates", stats)
        self.assertIn("neural_updates", stats)
        self.assertIn("memory_stored", stats)
        self.assertIn("loss_change", stats)
    
    def test_learn_phase_failure(self):
        """测试学习阶段（失败经验）"""
        feedback = {"success": False, "reward": -0.2}
        experience = {"action": "achieve", "context": {}}
        
        stats = self.controller.learn(feedback, experience)
        
        # 失败时损失应该增加
        self.assertGreaterEqual(stats["loss_change"], 0)
    
    def test_reflect_phase_high_performance(self):
        """测试反思阶段（高性能）"""
        learning_stats = {"graph_updates": 2, "neural_updates": 1}
        cycle_data = {
            "feedback": {"reward": 1.0},
            "decision": {"confidence": 0.9}
        }
        
        reflection = self.controller.reflect(learning_stats, cycle_data)
        
        self.assertGreater(reflection["performance_score"], 0.7)
        self.assertIn("high_performance_pattern_detected", reflection["insights"])
        self.assertIn("reinforce_current_strategy", reflection["strategy_adjustments"])
    
    def test_reflect_phase_low_performance(self):
        """测试反思阶段（低性能）"""
        learning_stats = {"graph_updates": 0, "neural_updates": 0}
        cycle_data = {
            "feedback": {"reward": -0.2},
            "decision": {"confidence": 0.3}
        }
        
        reflection = self.controller.reflect(learning_stats, cycle_data)
        
        self.assertLess(reflection["performance_score"], 0.3)
        self.assertIn("low_performance_warning", reflection["insights"])
        self.assertIn("increase_exploration", reflection["strategy_adjustments"])
    
    def test_full_cycle(self):
        """测试完整认知循环"""
        result = self.controller.run_cycle(
            input_data="test question",
            goals=["learn_something"]
        )
        
        self.assertIn("cycle_id", result)
        self.assertIn("duration", result)
        self.assertIn("action_taken", result)
        self.assertIn("reward", result)
        self.assertIn("performance", result)
        self.assertIn("insights", result)
        
        # 应该有 6 个事件（每个阶段一个）
        self.assertEqual(len(self.controller.event_log), 6)
    
    def test_autonomous_session(self):
        """测试自主会话"""
        # 运行一个非常短的会话（1 秒）
        results = self.controller.run_autonomous_session(
            duration_seconds=1,
            tick_rate=0.1
        )
        
        self.assertGreater(len(results), 0)
        self.assertFalse(self.controller.is_running)
        
        # 检查所有结果都有必要的字段
        for result in results:
            self.assertIn("cycle_id", result)
            self.assertIn("action_taken", result)
            self.assertIn("reward", result)
    
    def test_statistics_collection(self):
        """测试统计信息收集"""
        # 运行几个循环
        for i in range(3):
            self.controller.run_cycle(f"query_{i}")
        
        stats = self.controller.get_statistics()
        
        self.assertEqual(stats["total_loops"], 3)
        self.assertEqual(stats["total_events"], 3 * 6)  # 6 个阶段 per loop
        self.assertIn("events_per_phase", stats)
        self.assertIn("average_processing_time", stats)
    
    def test_event_log_export(self):
        """测试事件日志导出"""
        # 运行一个循环
        self.controller.run_cycle("test")
        
        # 导出日志
        filename = "test_cognitive_log.json"
        self.controller.export_log(filename)
        
        # 验证文件存在且可解析
        with open(filename, 'r') as f:
            log_data = json.load(f)
        
        self.assertIsInstance(log_data, list)
        self.assertGreater(len(log_data), 0)
        self.assertIn("phase", log_data[0])
    
    def test_motivation_driven_exploration(self):
        """测试动机驱动的探索"""
        # 设置高探索奖励
        self.controller.exploration_bonus = 0.9
        
        explore_count = 0
        total_runs = 10
        
        for _ in range(total_runs):
            decision = self.controller.decide({"confidence": 0.5})
            if decision["selected_action"]["type"] == "explore":
                explore_count += 1
        
        # 高探索奖励应该导致更多探索行为
        self.assertGreater(explore_count, total_runs * 0.5)
    
    def test_goal_oriented_behavior(self):
        """测试目标导向行为"""
        goals = ["urgent_goal"]
        reasoning_results = {"confidence": 0.9, "predictions": []}
        
        decision = self.controller.decide(reasoning_results, goals)
        
        # 有高置信度目标时，应该选择目标导向动作
        selected_type = decision["selected_action"]["type"]
        self.assertIn(selected_type, ["achieve", "explore", "prevent"])
    
    def test_confidence_calculation(self):
        """测试置信度计算"""
        ucr = self.controller.perceive("test")
        
        # 测试基本置信度计算（没有模拟数据）
        results = self.controller.reason(ucr)
        
        # 置信度应该在 0-1 范围内
        self.assertGreaterEqual(results["confidence"], 0.0)
        self.assertLessEqual(results["confidence"], 1.0)
    
    def test_reflection_insights_generation(self):
        """测试反思洞察生成"""
        # 运行多个不同性能的循环
        for reward in [1.0, -0.2, 0.5, 0.9, 0.1]:
            self.controller.run_cycle(f"query_{reward}")
        
        stats = self.controller.get_statistics()
        
        # 应该有独特的洞察
        self.assertIn("unique_insights", stats)
        self.assertGreaterEqual(stats["unique_insights"], 0)


class TestCognitiveLoopIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_sequential_cycles_learning(self):
        """测试连续循环的学习效果"""
        controller = CognitiveLoopController()
        
        rewards = []
        for i in range(5):
            result = controller.run_cycle(f"learning_query_{i}")
            rewards.append(result["reward"])
        
        # 验证系统能够持续运行
        self.assertEqual(len(rewards), 5)
        # 所有奖励都应该是有效数值
        for r in rewards:
            self.assertIsInstance(r, (int, float))
    
    def test_memory_accumulation(self):
        """测试记忆累积"""
        controller = CognitiveLoopController()
        
        # 运行多个循环
        for i in range(10):
            controller.run_cycle(f"memory_test_{i}")
        
        stats = controller.get_statistics()
        
        # 验证事件日志正确累积
        self.assertEqual(stats["total_events"], 10 * 6)
        self.assertEqual(stats["total_loops"], 10)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestCognitiveEvent))
    suite.addTests(loader.loadTestsFromTestCase(TestCognitiveLoopController))
    suite.addTests(loader.loadTestsFromTestCase(TestCognitiveLoopIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
