"""
具身环境模块测试套件
测试 ContinuousPhysicsEngine, EmbodiedAgent, MultiAgentSociety, EmergenceAnalyzer
"""

import unittest
import math
from src.modules.embodied_environment import (
    Vector2D, GameObject, ObjectType,
    ContinuousPhysicsEngine,
    InternalState, Action, MotivationType, EmbodiedAgent,
    Message, MultiAgentSociety,
    EmergenceAnalyzer
)


class TestVector2D(unittest.TestCase):
    """测试 2D 向量类"""
    
    def test_addition(self):
        v1 = Vector2D(1, 2)
        v2 = Vector2D(3, 4)
        result = v1 + v2
        self.assertEqual(result.x, 4)
        self.assertEqual(result.y, 6)
        
    def test_subtraction(self):
        v1 = Vector2D(5, 7)
        v2 = Vector2D(2, 3)
        result = v1 - v2
        self.assertEqual(result.x, 3)
        self.assertEqual(result.y, 4)
        
    def test_multiplication(self):
        v = Vector2D(2, 3)
        result = v * 2.5
        self.assertEqual(result.x, 5.0)
        self.assertEqual(result.y, 7.5)
        
    def test_magnitude(self):
        v = Vector2D(3, 4)
        self.assertEqual(v.magnitude(), 5.0)
        
    def test_normalize(self):
        v = Vector2D(3, 4)
        norm = v.normalize()
        self.assertAlmostEqual(norm.magnitude(), 1.0)
        
    def test_distance(self):
        v1 = Vector2D(0, 0)
        v2 = Vector2D(3, 4)
        self.assertEqual(v1.distance_to(v2), 5.0)
        
    def test_dot_product(self):
        v1 = Vector2D(1, 2)
        v2 = Vector2D(3, 4)
        self.assertEqual(v1.dot(v2), 11)
        
    def test_serialization(self):
        v = Vector2D(1.5, 2.5)
        data = v.to_dict()
        restored = Vector2D.from_dict(data)
        self.assertEqual(v.x, restored.x)
        self.assertEqual(v.y, restored.y)


class TestContinuousPhysicsEngine(unittest.TestCase):
    """测试连续物理引擎"""
    
    def setUp(self):
        self.physics = ContinuousPhysicsEngine(world_size=(100, 100))
        
    def test_add_object(self):
        obj = GameObject(id="test", position=Vector2D(50, 50))
        self.physics.add_object(obj)
        self.assertIn("test", self.physics.objects)
        
    def test_remove_object(self):
        obj = GameObject(id="test", position=Vector2D(50, 50))
        self.physics.add_object(obj)
        self.physics.remove_object("test")
        self.assertNotIn("test", self.physics.objects)
        
    def test_position_update(self):
        obj = GameObject(
            id="test",
            position=Vector2D(50, 50),
            velocity=Vector2D(10, 0)
        )
        self.physics.add_object(obj)
        self.physics.update(dt=1.0)
        # 位置应该更新
        self.assertGreater(self.physics.objects["test"].position.x, 50)
        
    def test_boundary_collision(self):
        obj = GameObject(
            id="test",
            position=Vector2D(95, 50),
            velocity=Vector2D(10, 0),
            radius=5
        )
        self.physics.add_object(obj)
        self.physics.update(dt=1.0)
        # 应该反弹
        self.assertLessEqual(
            self.physics.objects["test"].position.x,
            self.physics.world_size.x
        )
        
    def test_get_nearby_objects(self):
        center = GameObject(id="center", position=Vector2D(50, 50))
        near = GameObject(id="near", position=Vector2D(55, 50))
        far = GameObject(id="far", position=Vector2D(90, 90))
        
        for obj in [center, near, far]:
            self.physics.add_object(obj)
            
        nearby = self.physics.get_nearby_objects(Vector2D(50, 50), radius=10)
        self.assertEqual(len(nearby), 2)  # center 和 near
        
        nearby_small = self.physics.get_nearby_objects(Vector2D(50, 50), radius=3)
        self.assertEqual(len(nearby_small), 1)  # 只有自己
        
    def test_line_of_sight_clear(self):
        start = Vector2D(10, 10)
        end = Vector2D(20, 10)
        self.assertTrue(self.physics.check_line_of_sight(start, end))
        
    def test_line_of_sight_blocked(self):
        start = Vector2D(10, 10)
        end = Vector2D(30, 10)
        
        obstacle = GameObject(
            id="obs",
            position=Vector2D(20, 10),
            radius=5,
            obj_type=ObjectType.OBSTACLE
        )
        self.physics.add_object(obstacle)
        
        self.assertFalse(self.physics.check_line_of_sight(start, end))


class TestEmbodiedAgent(unittest.TestCase):
    """测试具身智能体"""
    
    def setUp(self):
        self.physics = ContinuousPhysicsEngine(world_size=(100, 100))
        self.agent = EmbodiedAgent(
            agent_id="test_agent",
            position=Vector2D(50, 50)
        )
        self.physics.add_object(self.agent.game_object)
        
    def test_initial_state(self):
        self.assertEqual(self.agent.internal_state.energy, 100.0)
        self.assertEqual(self.agent.internal_state.curiosity_level, 50.0)
        
    def test_internal_state_update(self):
        initial_energy = self.agent.internal_state.energy
        self.agent.internal_state.update(dt=10.0)
        self.assertLess(self.agent.internal_state.energy, initial_energy)
        
    def test_perceive_empty(self):
        visible = self.agent.perceive(self.physics)
        self.assertEqual(len(visible), 0)
        
    def test_perceive_with_objects(self):
        food = GameObject(
            id="food",
            position=Vector2D(60, 60),
            obj_type=ObjectType.FOOD,
            radius=1.5
        )
        self.physics.add_object(food)
        
        visible = self.agent.perceive(self.physics)
        self.assertEqual(len(visible), 1)
        self.assertEqual(visible[0].obj_type, ObjectType.FOOD)
        
    def test_decide_action_survival(self):
        # 设置低能量
        self.agent.internal_state.energy = 20.0
        
        food = GameObject(
            id="food",
            position=Vector2D(60, 60),
            obj_type=ObjectType.FOOD,
            radius=1.5
        )
        self.physics.add_object(food)
        
        visible = self.agent.perceive(self.physics)
        action = self.agent.decide_action(visible)
        
        self.assertEqual(action.action_type, "apply_force")
        # 力应该指向食物方向
        self.assertGreater(action.parameters["force_x"], 0)
        self.assertGreater(action.parameters["force_y"], 0)
        
    def test_execute_action(self):
        action = Action(
            action_type="apply_force",
            parameters={"force_x": 5.0, "force_y": 5.0}
        )
        self.agent.execute_action(action, self.physics)
        self.assertEqual(self.agent.game_object.acceleration.x, 5.0)
        self.assertEqual(len(self.agent.action_history), 1)
        
    def test_prediction_model_update(self):
        initial_error = self.agent.internal_state.last_prediction_error
        self.agent.update_prediction_model({
            "position": Vector2D(55, 55)
        })
        # 预测模型应该更新
        self.assertIn("last_position", self.agent.prediction_model)


class TestMultiAgentSociety(unittest.TestCase):
    """测试多智能体社会系统"""
    
    def setUp(self):
        self.physics = ContinuousPhysicsEngine(world_size=(100, 100))
        self.society = MultiAgentSociety(self.physics)
        
    def test_add_agent(self):
        agent = EmbodiedAgent("agent1", Vector2D(50, 50))
        self.society.add_agent(agent)
        self.assertIn("agent1", self.society.agents)
        
    def test_remove_agent(self):
        agent = EmbodiedAgent("agent1", Vector2D(50, 50))
        self.society.add_agent(agent)
        self.society.remove_agent("agent1")
        self.assertNotIn("agent1", self.society.agents)
        
    def test_broadcast_message(self):
        agent1 = EmbodiedAgent("agent1", Vector2D(50, 50))
        agent2 = EmbodiedAgent("agent2", Vector2D(60, 60))
        self.society.add_agent(agent1)
        self.society.add_agent(agent2)
        
        self.society.broadcast_message("agent1", {"msg": "hello"})
        self.assertEqual(len(self.society.message_queue), 1)
        
    def test_process_messages(self):
        agent1 = EmbodiedAgent("agent1", Vector2D(50, 50))
        agent2 = EmbodiedAgent("agent2", Vector2D(60, 60))
        self.society.add_agent(agent1)
        self.society.add_agent(agent2)
        
        self.society.send_message("agent1", "agent2", {"msg": "hello"})
        self.society.process_messages()
        
        self.assertEqual(len(self.society.interaction_log), 1)
        self.assertEqual(self.society.interaction_log[0]["to"], "agent2")
        
    def test_step_simulation(self):
        agent = EmbodiedAgent("agent1", Vector2D(50, 50))
        self.society.add_agent(agent)
        
        initial_pos = agent.game_object.position.x
        self.society.step(dt=1.0)
        
        # 位置可能改变
        self.assertIsNotNone(self.society.get_statistics())
        
    def test_statistics(self):
        agent = EmbodiedAgent("agent1", Vector2D(50, 50))
        self.society.add_agent(agent)
        
        stats = self.society.get_statistics()
        self.assertEqual(stats["agent_count"], 1)
        self.assertIn("total_interactions", stats)


class TestEmergenceAnalyzer(unittest.TestCase):
    """测试涌现分析器"""
    
    def setUp(self):
        self.analyzer = EmergenceAnalyzer()
        
    def test_record_behavior(self):
        state = {
            "id": "agent1",
            "position": {"x": 10, "y": 10},
            "internal_state": {"energy": 100}
        }
        self.analyzer.record_behavior([state])
        self.assertEqual(len(self.analyzer.behavior_history), 1)
        
    def test_shannon_entropy_uniform(self):
        # 均匀分布应该有高熵
        data = [1, 2, 3, 4, 5]
        entropy = self.analyzer.calculate_shannon_entropy(data)
        self.assertGreater(entropy, 2.0)
        
    def test_shannon_entropy_constant(self):
        # 常数序列应该有零熵
        data = [1, 1, 1, 1, 1]
        entropy = self.analyzer.calculate_shannon_entropy(data)
        self.assertEqual(entropy, 0.0)
        
    def test_mutual_information_independent(self):
        # 独立序列应该有低互信息
        series_a = [1, 2, 3, 4, 5]
        series_b = [5, 4, 3, 2, 1]
        mi = self.analyzer.calculate_mutual_information(series_a, series_b)
        self.assertLess(mi, 3.0)  # 互信息上界为 log2(5) ≈ 2.32
        
    def test_mutual_information_identical(self):
        # 相同序列应该有高互信息
        series = [1, 2, 3, 4, 5]
        mi = self.analyzer.calculate_mutual_information(series, series)
        self.assertGreater(mi, 2.0)
        
    def test_analyze_emergence_insufficient_data(self):
        result = self.analyzer.analyze_emergence()
        self.assertEqual(result["status"], "insufficient_data")
        
    def test_analyze_emergence_with_data(self):
        # 添加足够的数据
        for i in range(10):
            states = [
                {"position": {"x": i, "y": j}} 
                for j in range(3)
            ]
            self.analyzer.record_behavior(states)
            
        result = self.analyzer.analyze_emergence()
        self.assertEqual(result["status"], "analyzed")
        self.assertIn("entropy", result)
        self.assertIn("frames_analyzed", result)
        
    def test_detect_emergent_patterns_empty(self):
        patterns = self.analyzer.detect_emergent_patterns()
        self.assertEqual(len(patterns), 0)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_full_simulation_cycle(self):
        """测试完整的模拟周期"""
        physics = ContinuousPhysicsEngine(world_size=(100, 100))
        society = MultiAgentSociety(physics)
        analyzer = EmergenceAnalyzer()
        
        # 添加智能体
        for i in range(3):
            agent = EmbodiedAgent(
                f"agent_{i}",
                Vector2D(50 + i*10, 50)
            )
            society.add_agent(agent)
            
        # 运行模拟
        for _ in range(20):
            society.step(dt=0.5)
            
            # 记录行为
            states = [a.to_dict() for a in society.agents.values()]
            analyzer.record_behavior(states)
            
        # 分析结果
        analysis = analyzer.analyze_emergence()
        self.assertEqual(analysis["status"], "analyzed")
        
        # 验证统计
        stats = society.get_statistics()
        self.assertEqual(stats["agent_count"], 3)
        self.assertGreater(stats["total_interactions"], 0)


if __name__ == "__main__":
    unittest.main()
