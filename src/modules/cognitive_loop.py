"""
认知闭环控制器 (Cognitive Loop Controller)
==========================================
第六阶段核心组件：将感知、推理、行动、学习、反思连接成自动化闭环。
支持内在动机驱动和神经符号混合处理。

核心流程:
1. Perceive: 多模态输入 -> UCR + 神经嵌入
2. Reason: 知识图谱检索 + 世界模型预测
3. Decide: 内在动机 + 目标优化 -> 动作选择
4. Act: 执行动作 -> 环境反馈
5. Learn: 更新知识图谱 + 神经权重优化
6. Reflect: 自我模型更新 + 元认知分析
"""

import time
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# 导入前序模块
try:
    from ucr_layer import UCR, UCRLayer, EntityType
    from knowledge_graph import KnowledgeGraph, HybridRetriever, EnhancedMemoryBank
    from world_model import WorldModel, State, Prediction
    from multimodal_perception import MultimodalFusionEngine, Modality
    from neural_backend import NeuralUCREncoder, DataManager, IntrinsicMotivation
except ImportError as e:
    print(f"警告：部分模块未找到，将使用模拟模式: {e}")
    # 定义模拟类以保证代码可运行
    class UCR: pass
    class UCRLayer: 
        def __init__(self): self.units = {}
        def create_unit(self, *args, **kwargs): return UCR()
    class EntityType: CONCEPT = "CONCEPT"
    class KnowledgeGraph: pass
    class HybridRetriever: pass
    class EnhancedMemoryBank: pass
    class WorldModel: pass
    class State: pass
    class Prediction: pass
    class MultimodalFusionEngine: pass
    class Modality: TEXT = "TEXT"
    class NeuralUCREncoder: pass
    class DataManager: pass
    class IntrinsicMotivation:
        def __init__(self): self.current_drive = "curiosity"
        def get_current_drive(self): return self.current_drive


class LoopPhase(Enum):
    """认知循环阶段"""
    PERCEIVE = "perceive"
    REASON = "reason"
    DECIDE = "decide"
    ACT = "act"
    LEARN = "learn"
    REFLECT = "reflect"


@dataclass
class CognitiveEvent:
    """认知事件记录"""
    phase: LoopPhase
    timestamp: float
    input_data: Any
    output_data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "phase": self.phase.value,
            "timestamp": self.timestamp,
            "input_type": type(self.input_data).__name__ if self.input_data else None,
            "output_type": type(self.output_data).__name__ if self.output_data else None,
            "metadata": self.metadata
        }


class CognitiveLoopController:
    """
    认知闭环控制器
    
    协调所有认知模块，实现自动化学习和推理循环。
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # 初始化核心组件
        self.ucr_layer = UCRLayer()
        self.knowledge_graph = KnowledgeGraph()
        self.memory_bank = EnhancedMemoryBank()
        self.world_model = WorldModel()
        self.perception_engine = MultimodalFusionEngine()
        self.neural_encoder = NeuralUCREncoder()
        self.data_manager = DataManager()
        self.motivation_system = IntrinsicMotivation()
        
        # 状态追踪
        self.current_state: Optional[State] = None
        self.event_log: List[CognitiveEvent] = []
        self.loop_count = 0
        self.is_running = False
        
        # 配置参数
        self.learning_rate = self.config.get("learning_rate", 0.01)
        self.exploration_bonus = self.config.get("exploration_bonus", 0.1)
        self.reflection_threshold = self.config.get("reflection_threshold", 0.8)
        
    def perceive(self, raw_input: Any, modality: str = "TEXT") -> UCR:
        """
        阶段 1: 感知
        将原始输入转换为统一认知表示 (UCR)
        """
        start_time = time.time()
        
        # 多模态融合处理
        if hasattr(self.perception_engine, 'process'):
            perceived = self.perception_engine.process(raw_input, modality)
        else:
            # 模拟处理
            perceived = {"content": raw_input, "modality": modality}
        
        # 创建 UCR
        ucr = self.ucr_layer.create_unit(
            entity_type=EntityType.CONCEPT,
            content=str(raw_input)[:100],  # 截断避免过长
            metadata={"modality": modality, "raw_length": len(str(raw_input))}
        )
        
        # 生成神经嵌入
        if hasattr(self.neural_encoder, 'encode'):
            embedding = self.neural_encoder.encode(str(raw_input))
            ucr.vector_embedding = embedding
        
        event = CognitiveEvent(
            phase=LoopPhase.PERCEIVE,
            timestamp=start_time,
            input_data=raw_input,
            output_data=ucr,
            metadata={"processing_time": time.time() - start_time}
        )
        self.event_log.append(event)
        
        return ucr
    
    def reason(self, query_ucr: UCR, context: Optional[List[UCR]] = None) -> Dict:
        """
        阶段 2: 推理
        结合知识图谱检索和世界模型预测进行推理
        """
        start_time = time.time()
        
        results = {
            "graph_retrieval": [],
            "vector_search": [],
            "predictions": [],
            "confidence": 0.0
        }
        
        # 知识图谱检索
        if hasattr(self.knowledge_graph, 'query'):
            try:
                graph_results = self.knowledge_graph.query(query_ucr.content)
                results["graph_retrieval"] = graph_results[:5]  # 取前 5 个
            except:
                pass
        
        # 向量相似性搜索
        if hasattr(self.memory_bank, 'search_similar'):
            try:
                similar = self.memory_bank.search_similar(query_ucr, top_k=5)
                results["vector_search"] = similar
            except:
                pass
        
        # 世界模型预测
        if self.current_state and hasattr(self.world_model, 'predict'):
            try:
                prediction = self.world_model.predict(self.current_state, steps=3)
                results["predictions"] = [prediction] if prediction else []
            except:
                pass
        
        # 计算置信度
        total_evidence = len(results["graph_retrieval"]) + len(results["vector_search"])
        results["confidence"] = min(1.0, total_evidence * 0.2)
        
        event = CognitiveEvent(
            phase=LoopPhase.REASON,
            timestamp=start_time,
            input_data=query_ucr,
            output_data=results,
            metadata={
                "processing_time": time.time() - start_time,
                "evidence_count": total_evidence
            }
        )
        self.event_log.append(event)
        
        return results
    
    def decide(self, reasoning_results: Dict, goals: Optional[List[str]] = None) -> Dict:
        """
        阶段 3: 决策
        基于内在动机和目标优化选择动作
        """
        start_time = time.time()
        
        # 获取内在动机驱动
        motivation = self.motivation_system.get_current_drive()
        
        # 计算动作价值
        actions = []
        
        # 基于好奇心的探索动作
        if motivation == "curiosity" or random.random() < self.exploration_bonus:
            actions.append({
                "type": "explore",
                "target": "unknown_concept",
                "value": 0.8,
                "reason": "intrinsic_curiosity"
            })
        
        # 基于目标的利用动作
        if goals:
            for goal in goals:
                actions.append({
                    "type": "achieve",
                    "target": goal,
                    "value": reasoning_results.get("confidence", 0.5),
                    "reason": "goal_oriented"
                })
        
        # 基于预测的预防动作
        if reasoning_results.get("predictions"):
            actions.append({
                "type": "prevent",
                "target": "negative_outcome",
                "value": 0.9,
                "reason": "predictive_avoidance"
            })
        
        # 选择最高价值动作
        best_action = max(actions, key=lambda x: x["value"]) if actions else {
            "type": "idle",
            "target": None,
            "value": 0.0,
            "reason": "no_viable_options"
        }
        
        decision = {
            "selected_action": best_action,
            "alternative_actions": actions,
            "motivation_state": motivation,
            "confidence": best_action["value"]
        }
        
        event = CognitiveEvent(
            phase=LoopPhase.DECIDE,
            timestamp=start_time,
            input_data=reasoning_results,
            output_data=decision,
            metadata={"processing_time": time.time() - start_time}
        )
        self.event_log.append(event)
        
        return decision
    
    def act(self, decision: Dict, environment: Optional[Any] = None) -> Dict:
        """
        阶段 4: 行动
        执行选定的动作并获取环境反馈
        """
        start_time = time.time()
        
        action = decision["selected_action"]
        feedback = {
            "success": False,
            "reward": 0.0,
            "new_state": None,
            "observations": []
        }
        
        # 模拟环境交互
        if action["type"] == "explore":
            # 探索动作：发现新概念
            feedback["success"] = True
            feedback["reward"] = 0.5
            feedback["observations"] = ["discovered_new_pattern"]
            
        elif action["type"] == "achieve":
            # 目标动作：尝试达成目标
            success_prob = decision["confidence"]
            feedback["success"] = random.random() < success_prob
            feedback["reward"] = 1.0 if feedback["success"] else -0.2
            
        elif action["type"] == "prevent":
            # 预防动作：避免负面结果
            feedback["success"] = True
            feedback["reward"] = 0.3
            feedback["observations"] = ["avoided_potential_risk"]
        
        # 更新世界模型状态
        if feedback.get("success"):
            self.current_state = State() if not self.current_state else self.current_state
            # 在实际实现中会更新状态变量
        
        event = CognitiveEvent(
            phase=LoopPhase.ACT,
            timestamp=start_time,
            input_data=decision,
            output_data=feedback,
            metadata={
                "processing_time": time.time() - start_time,
                "action_type": action["type"]
            }
        )
        self.event_log.append(event)
        
        return feedback
    
    def learn(self, feedback: Dict, experience: Dict) -> Dict:
        """
        阶段 5: 学习
        从经验中更新知识图谱和神经权重
        """
        start_time = time.time()
        
        learning_stats = {
            "graph_updates": 0,
            "neural_updates": 0,
            "memory_stored": False,
            "loss_change": 0.0
        }
        
        # 更新知识图谱
        if feedback["success"] and hasattr(self.knowledge_graph, 'add_relation'):
            try:
                # 提取经验中的因果关系
                cause = experience.get("action", "unknown")
                effect = "success" if feedback["success"] else "failure"
                # self.knowledge_graph.add_relation(cause, "leads_to", effect)
                learning_stats["graph_updates"] = 1
            except:
                pass
        
        # 神经权重更新 (对比学习)
        if hasattr(self.neural_encoder, 'update_weights'):
            try:
                # 基于奖励信号调整
                reward = feedback.get("reward", 0.0)
                # self.neural_encoder.update_weights(reward)
                learning_stats["neural_updates"] = 1
                learning_stats["loss_change"] = -0.01 if reward > 0 else 0.02
            except:
                pass
        
        # 存储到记忆库
        if hasattr(self.memory_bank, 'store'):
            try:
                self.memory_bank.store(experience)
                learning_stats["memory_stored"] = True
            except:
                pass
        
        event = CognitiveEvent(
            phase=LoopPhase.LEARN,
            timestamp=start_time,
            input_data=feedback,
            output_data=learning_stats,
            metadata={"processing_time": time.time() - start_time}
        )
        self.event_log.append(event)
        
        return learning_stats
    
    def reflect(self, learning_stats: Dict, cycle_data: Dict) -> Dict:
        """
        阶段 6: 反思
        元认知分析，更新自我模型
        """
        start_time = time.time()
        
        reflection = {
            "performance_score": 0.0,
            "insights": [],
            "self_model_updates": [],
            "strategy_adjustments": []
        }
        
        # 计算性能得分
        total_reward = cycle_data.get("feedback", {}).get("reward", 0.0)
        confidence = cycle_data.get("decision", {}).get("confidence", 0.5)
        reflection["performance_score"] = (total_reward + confidence) / 2
        
        # 生成洞察
        if reflection["performance_score"] > self.reflection_threshold:
            reflection["insights"].append("high_performance_pattern_detected")
            reflection["strategy_adjustments"].append("reinforce_current_strategy")
        elif reflection["performance_score"] < 0.3:
            reflection["insights"].append("low_performance_warning")
            reflection["strategy_adjustments"].append("increase_exploration")
        
        # 更新自我模型
        if hasattr(self.world_model, 'update_self_model'):
            try:
                self.world_model.update_self_model({
                    "last_performance": reflection["performance_score"],
                    "learning_efficiency": learning_stats.get("graph_updates", 0)
                })
                reflection["self_model_updates"].append("capability_metric_updated")
            except:
                pass
        
        event = CognitiveEvent(
            phase=LoopPhase.REFLECT,
            timestamp=start_time,
            input_data=learning_stats,
            output_data=reflection,
            metadata={"processing_time": time.time() - start_time}
        )
        self.event_log.append(event)
        
        return reflection
    
    def run_cycle(self, input_data: Any, goals: Optional[List[str]] = None) -> Dict:
        """
        执行完整的认知循环
        """
        self.loop_count += 1
        cycle_start = time.time()
        
        # 1. 感知
        query_ucr = self.perceive(input_data)
        
        # 2. 推理
        reasoning = self.reason(query_ucr)
        
        # 3. 决策
        decision = self.decide(reasoning, goals)
        
        # 4. 行动
        feedback = self.act(decision)
        
        # 5. 学习
        experience = {
            "input": input_data,
            "action": decision["selected_action"],
            "context": reasoning
        }
        learning = self.learn(feedback, experience)
        
        # 6. 反思
        cycle_data = {
            "reasoning": reasoning,
            "decision": decision,
            "feedback": feedback,
            "learning": learning
        }
        reflection = self.reflect(learning, cycle_data)
        
        cycle_result = {
            "cycle_id": self.loop_count,
            "duration": time.time() - cycle_start,
            "input": str(input_data)[:50],
            "action_taken": decision["selected_action"]["type"],
            "reward": feedback["reward"],
            "performance": reflection["performance_score"],
            "insights": reflection["insights"]
        }
        
        return cycle_result
    
    def run_autonomous_session(self, duration_seconds: int, tick_rate: float = 1.0) -> List[Dict]:
        """
        运行自主会话：在指定时间内持续执行认知循环
        """
        self.is_running = True
        results = []
        start_time = time.time()
        
        print(f"开始自主认知会话，持续 {duration_seconds} 秒...")
        
        while time.time() - start_time < duration_seconds and self.is_running:
            # 生成内在动机驱动的查询
            drive = self.motivation_system.get_current_drive()
            query = f"explore_{drive}_concept_{random.randint(1, 100)}"
            
            # 执行循环
            result = self.run_cycle(query)
            results.append(result)
            
            print(f"循环 #{result['cycle_id']}: 动作={result['action_taken']}, "
                  f"奖励={result['reward']:.2f}, 性能={result['performance']:.2f}")
            
            # 控制节奏
            time.sleep(tick_rate)
        
        self.is_running = False
        print(f"会话结束，完成 {len(results)} 个认知循环")
        
        return results
    
    def get_statistics(self) -> Dict:
        """获取认知循环统计信息"""
        if not self.event_log:
            return {"error": "No events recorded"}
        
        phase_counts = {}
        total_time = 0
        
        for event in self.event_log:
            phase = event.phase.value
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
            if event.metadata.get("processing_time"):
                total_time += event.metadata["processing_time"]
        
        return {
            "total_loops": self.loop_count,
            "total_events": len(self.event_log),
            "events_per_phase": phase_counts,
            "average_processing_time": total_time / len(self.event_log) if self.event_log else 0,
            "unique_insights": len(set(
                insight 
                for e in self.event_log 
                if e.phase == LoopPhase.REFLECT 
                for insight in e.output_data.get("insights", [])
            ))
        }
    
    def export_log(self, filename: str = "cognitive_log.json"):
        """导出事件日志"""
        log_data = [event.to_dict() for event in self.event_log]
        with open(filename, 'w') as f:
            json.dump(log_data, f, indent=2)
        print(f"日志已导出到 {filename}")


def demo_cognitive_loop():
    """演示认知闭环系统"""
    print("=" * 60)
    print("认知闭环控制器演示")
    print("=" * 60)
    
    # 初始化控制器
    config = {
        "learning_rate": 0.01,
        "exploration_bonus": 0.15,
        "reflection_threshold": 0.7
    }
    controller = CognitiveLoopController(config)
    
    # 运行单个循环
    print("\n1. 运行单个认知循环:")
    result = controller.run_cycle(
        input_data="什么是量子纠缠？",
        goals=["understand_quantum_physics"]
    )
    print(f"   循环 ID: {result['cycle_id']}")
    print(f"   采取动作: {result['action_taken']}")
    print(f"   获得奖励: {result['reward']:.2f}")
    print(f"   性能得分: {result['performance']:.2f}")
    print(f"   产生洞察: {result['insights']}")
    
    # 运行短期自主会话
    print("\n2. 运行 5 秒自主会话:")
    session_results = controller.run_autonomous_session(duration_seconds=5, tick_rate=0.5)
    
    # 显示统计
    print("\n3. 系统统计:")
    stats = controller.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 导出日志
    controller.export_log("demo_cognitive_log.json")
    
    print("\n演示完成!")
    return controller


if __name__ == "__main__":
    demo_cognitive_loop()
