"""
阶段 14: 元认知监控系统 (Metacognitive Monitoring System)

实现认知的自我监控、评估和调节功能，包括：
- 实时认知状态监测
- 认知负荷评估
- 自适应策略调节
- 流状态（Flow State）优化
- 元认知日志与学习
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Union
import time
import math
from datetime import datetime

# 从核心类型系统导入精确类型
import sys
sys.path.insert(0, '/workspace/src')
from core.strict_types import JsonValueT


class CognitiveState(Enum):
    """认知状态枚举"""

    FLOW = auto()  # 流状态：最佳表现
    FOCUSED = auto()  # 专注状态：高效工作
    CONFUSED = auto()  # 困惑状态：需要帮助
    OVERLOADED = auto()  # 过载状态：需要简化
    FATIGUED = auto()  # 疲劳状态：需要休息
    BORED = auto()  # 无聊状态：需要挑战
    ANXIOUS = auto()  # 焦虑状态：需要降低难度


class RegulationStrategy(Enum):
    """调节策略枚举"""

    INCREASE_CHALLENGE = auto()  # 增加挑战
    DECREASE_CHALLENGE = auto()  # 降低挑战
    PROVIDE_HINT = auto()  # 提供提示
    TAKE_BREAK = auto()  # 休息
    SWITCH_TASK = auto()  # 切换任务
    DECOMPOSE_TASK = auto()  # 分解任务
    REINFORCE_MOTIVATION = auto()  # 强化动机
    ADJUST_PACE = auto()  # 调整节奏


@dataclass
class CognitiveMetrics:
    """认知指标数据类"""

    attention_level: float = 0.0  # 注意力水平 (0-1)
    working_memory_load: float = 0.0  # 工作记忆负载 (0-1)
    processing_speed: float = 0.0  # 处理速度 (0-1)
    error_rate: float = 0.0  # 错误率 (0-1)
    response_time: float = 0.0  # 响应时间 (秒)
    confidence_level: float = 0.0  # 信心水平 (0-1)
    mental_effort: float = 0.0  # 心理努力程度 (0-1)
    engagement: float = 0.0  # 参与度 (0-1)

    def to_dict(self) -> Dict[str, float]:
        return {
            "attention_level": self.attention_level,
            "working_memory_load": self.working_memory_load,
            "processing_speed": self.processing_speed,
            "error_rate": self.error_rate,
            "response_time": self.response_time,
            "confidence_level": self.confidence_level,
            "mental_effort": self.mental_effort,
            "engagement": self.engagement,
        }


@dataclass
class MetacognitiveLog:
    """元认知日志记录"""

    timestamp: datetime
    state: CognitiveState
    metrics: CognitiveMetrics
    strategy_applied: Optional[RegulationStrategy]
    outcome: Optional[str] = None

    def to_dict(self) -> Dict[str, JsonValueT]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "state": self.state.name,
            "metrics": self.metrics.to_dict(),
            "strategy_applied": self.strategy_applied.name if self.strategy_applied else None,
            "outcome": self.outcome,
        }


class CognitiveLoadCalculator:
    """认知负荷计算器"""

    def __init__(
        self,
        working_memory_capacity: float = 7.0,  # 米勒定律：7±2
        intrinsic_load_weight: float = 0.4,
        extraneous_load_weight: float = 0.3,
        germane_load_weight: float = 0.3,
    ):
        self.working_memory_capacity = working_memory_capacity
        self.intrinsic_load_weight = intrinsic_load_weight
        self.extraneous_load_weight = extraneous_load_weight
        self.germane_load_weight = germane_load_weight

    def calculate_intrinsic_load(
        self, element_interactivity: float, prior_knowledge: float
    ) -> float:
        """计算内在认知负荷"""
        # 元素交互性越高，先验知识越少，内在负荷越高
        base_load = element_interactivity * (1.0 - prior_knowledge * 0.5)
        return min(1.0, base_load)

    def calculate_extraneous_load(
        self, presentation_complexity: float, distraction_level: float
    ) -> float:
        """计算外在认知负荷"""
        return min(1.0, presentation_complexity * 0.6 + distraction_level * 0.4)

    def calculate_germane_load(self, schema_construction: float, automation_level: float) -> float:
        """计算相关认知负荷（用于学习的负荷）"""
        return min(1.0, schema_construction * 0.7 + automation_level * 0.3)

    def calculate_total_load(self, intrinsic: float, extraneous: float, germane: float) -> float:
        """计算总认知负荷"""
        weighted_sum = (
            intrinsic * self.intrinsic_load_weight
            + extraneous * self.extraneous_load_weight
            + germane * self.germane_load_weight
        )
        return min(1.0, weighted_sum)

    def is_overloaded(self, total_load: float, threshold: float = 0.85) -> bool:
        """判断是否过载"""
        return total_load > threshold

    def optimal_load_range(self) -> Tuple[float, float]:
        """返回最优认知负荷范围"""
        return (0.6, 0.8)  # 略低于容量上限以促进学习


class StateDetector:
    """认知状态检测器"""

    def __init__(self):
        self.state_history: List[CognitiveState] = []
        self.transition_matrix = self._init_transition_matrix()

    def _init_transition_matrix(self) -> Dict[CognitiveState, Dict[CognitiveState, float]]:
        """初始化状态转移概率矩阵（简化版）"""
        states = list(CognitiveState)
        return {s1: {s2: 0.0 for s2 in states} for s1 in states}

    def detect_state(self, metrics: CognitiveMetrics) -> CognitiveState:
        """根据指标检测当前认知状态"""
        # 基于多指标综合判断
        attention = metrics.attention_level
        load = metrics.working_memory_load
        effort = metrics.mental_effort
        engagement = metrics.engagement
        confidence = metrics.confidence_level
        error_rate = metrics.error_rate

        # 流状态：高注意力、适中负荷、高参与、高信心
        if (
            attention > 0.7
            and 0.5 < load < 0.8
            and engagement > 0.7
            and confidence > 0.6
            and error_rate < 0.2
        ):
            return CognitiveState.FLOW

        # 专注状态：高注意力、负荷可控
        if attention > 0.6 and load < 0.7 and error_rate < 0.3:
            return CognitiveState.FOCUSED

        # 过载状态：高负荷、低信心、高错误率
        if load > 0.85 or (effort > 0.8 and confidence < 0.4):
            return CognitiveState.OVERLOADED

        # 困惑状态：中等负荷、低信心、中等错误率
        if 0.5 < load < 0.8 and confidence < 0.5 and error_rate > 0.3:
            return CognitiveState.CONFUSED

        # 疲劳状态：低注意力、高努力、低参与
        if attention < 0.4 and effort > 0.7 and engagement < 0.4:
            return CognitiveState.FATIGUED

        # 无聊状态：低负荷、低参与
        if load < 0.3 and engagement < 0.4:
            return CognitiveState.BORED

        # 焦虑状态：高努力、低信心、高错误率
        if effort > 0.7 and confidence < 0.4 and error_rate > 0.4:
            return CognitiveState.ANXIOUS

        # 默认返回专注状态
        return CognitiveState.FOCUSED

    def update_history(self, state: CognitiveState):
        """更新状态历史"""
        self.state_history.append(state)
        if len(self.state_history) > 100:
            self.state_history.pop(0)

        # 更新转移矩阵
        if len(self.state_history) >= 2:
            prev_state = self.state_history[-2]
            curr_state = self.state_history[-1]
            # 简化：直接计数
            total = sum(1 for s in self.state_history[:-1] if s == prev_state)
            if total > 0:
                count = sum(
                    1
                    for i, s in enumerate(self.state_history[:-1])
                    if s == prev_state and self.state_history[i + 1] == curr_state
                )
                self.transition_matrix[prev_state][curr_state] = count / total


class StrategySelector:
    """调节策略选择器"""

    def __init__(self):
        self.strategy_effectiveness: Dict[RegulationStrategy, List[float]] = {
            s: [] for s in RegulationStrategy
        }

    def select_strategy(
        self, current_state: CognitiveState, context: Dict[str, JsonValueT]
    ) -> Optional[RegulationStrategy]:
        """根据当前状态选择调节策略"""

        # 基于状态的默认策略映射
        default_strategies: Dict[CognitiveState, Optional[RegulationStrategy]] = {
            CognitiveState.FLOW: None,  # 保持现状
            CognitiveState.FOCUSED: None,  # 保持现状
            CognitiveState.CONFUSED: RegulationStrategy.PROVIDE_HINT,
            CognitiveState.OVERLOADED: RegulationStrategy.DECOMPOSE_TASK,
            CognitiveState.FATIGUED: RegulationStrategy.TAKE_BREAK,
            CognitiveState.BORED: RegulationStrategy.INCREASE_CHALLENGE,
            CognitiveState.ANXIOUS: RegulationStrategy.DECREASE_CHALLENGE,
        }

        strategy: Optional[RegulationStrategy] = default_strategies.get(current_state)

        # 考虑上下文进行微调
        if context.get("task_criticality", False) and strategy == RegulationStrategy.TAKE_BREAK:
            # 关键任务不能休息，改为降低难度
            strategy = RegulationStrategy.DECREASE_CHALLENGE

        if context.get("time_pressure", False) and strategy == RegulationStrategy.DECOMPOSE_TASK:
            # 时间紧迫时不分解任务，改为提供提示
            strategy = RegulationStrategy.PROVIDE_HINT

        return strategy

    def record_outcome(self, strategy: RegulationStrategy, effectiveness: float):
        """记录策略效果"""
        self.strategy_effectiveness[strategy].append(effectiveness)
        # 保持历史记录长度
        if len(self.strategy_effectiveness[strategy]) > 50:
            self.strategy_effectiveness[strategy].pop(0)

    def get_best_strategy(self, state: CognitiveState) -> Optional[RegulationStrategy]:
        """获取历史上对该状态最有效的策略"""
        # 简化实现：返回平均效果最好的策略
        best_avg: float = -1
        best_strategy: Optional[RegulationStrategy] = None

        for strategy, outcomes in self.strategy_effectiveness.items():
            if outcomes:
                avg = sum(outcomes) / len(outcomes)
                if avg > best_avg:
                    best_avg = avg
                    best_strategy = strategy

        return best_strategy


class DifficultyAdjuster:
    """动态难度调整器"""

    def __init__(
        self,
        initial_difficulty: float = 0.5,
        adjustment_rate: float = 0.1,
        target_performance: float = 0.75,
    ):
        self.current_difficulty = initial_difficulty
        self.adjustment_rate = adjustment_rate
        self.target_performance = target_performance
        self.performance_history: List[float] = []

    def adjust(self, performance: float) -> float:
        """根据表现调整难度"""
        self.performance_history.append(performance)
        if len(self.performance_history) > 20:
            self.performance_history.pop(0)

        # 计算近期平均表现
        recent_perf = sum(self.performance_history[-5:]) / min(5, len(self.performance_history))

        # 基于表现与目标的差距调整难度
        error = self.target_performance - recent_perf

        # 表现好则增加难度，表现差则降低难度
        adjustment = error * (-self.adjustment_rate)

        self.current_difficulty = max(0.1, min(0.9, self.current_difficulty + adjustment))

        return self.current_difficulty

    def get_recommended_difficulty(
        self, skill_level: float, challenge_seeking: float = 0.5
    ) -> float:
        """根据技能水平和挑战寻求度推荐难度"""
        # 流理论：难度应略高于技能水平
        base_difficulty = skill_level + 0.1

        # 考虑个体的挑战寻求倾向
        adjusted = base_difficulty + (challenge_seeking - 0.5) * 0.2

        return max(0.1, min(0.9, adjusted))


class MetacognitiveMonitor:
    """元认知监控器 - 核心类"""

    def __init__(self, agent_id: str = "default"):
        self.agent_id = agent_id
        self.load_calculator = CognitiveLoadCalculator()
        self.state_detector = StateDetector()
        self.strategy_selector = StrategySelector()
        self.difficulty_adjuster = DifficultyAdjuster()

        self.log_history: List[MetacognitiveLog] = []
        self.session_start_time = datetime.now()
        self.total_regulation_count = 0
        self.successful_regulations = 0

        # 配置参数
        self.monitoring_interval = 1.0  # 秒
        self.last_check_time = time.time()

    def monitor(self, metrics: CognitiveMetrics, task_context: Dict[str, JsonValueT]) -> Dict[str, JsonValueT]:
        """执行一次完整的监控循环"""

        # 1. 计算认知负荷（如果上下文中没有提供预计算的负荷）
        if "cognitive_load" not in task_context:
            intrinsic = self.load_calculator.calculate_intrinsic_load(
                task_context.get("element_interactivity", 0.5),
                task_context.get("prior_knowledge", 0.5),
            )
            extraneous = self.load_calculator.calculate_extraneous_load(
                task_context.get("presentation_complexity", 0.3),
                task_context.get("distraction_level", 0.2),
            )
            germane = self.load_calculator.calculate_germane_load(
                task_context.get("schema_construction", 0.5),
                task_context.get("automation_level", 0.3),
            )
            total_load = self.load_calculator.calculate_total_load(intrinsic, extraneous, germane)
        else:
            # 使用提供的负荷值
            total_load = task_context["cognitive_load"]
            intrinsic = total_load * 0.4
            extraneous = total_load * 0.3
            germane = total_load * 0.3

        # 只有在指标中未设置工作记忆负载时才更新
        if metrics.working_memory_load == 0.0:
            metrics.working_memory_load = total_load

        load_breakdown = {"intrinsic": intrinsic, "extraneous": extraneous, "germane": germane}

        # 2. 检测认知状态
        current_state = self.state_detector.detect_state(metrics)
        self.state_detector.update_history(current_state)

        # 3. 选择调节策略
        context = {
            "task_criticality": task_context.get("criticality", False),
            "time_pressure": task_context.get("time_pressure", False),
        }
        strategy = self.strategy_selector.select_strategy(current_state, context)

        # 4. 应用调节（如果有策略）
        outcome = None
        if strategy:
            outcome = self._apply_regulation(strategy, task_context)
            self.total_regulation_count += 1
            if outcome and "success" in outcome.lower():
                self.successful_regulations += 1
            self.strategy_selector.record_outcome(
                strategy, 1.0 if outcome and "success" in outcome.lower() else 0.0
            )

        # 5. 调整难度
        if "performance" in task_context:
            new_difficulty = self.difficulty_adjuster.adjust(task_context["performance"])
            task_context["recommended_difficulty"] = new_difficulty

        # 6. 记录日志
        log_entry = MetacognitiveLog(
            timestamp=datetime.now(),
            state=current_state,
            metrics=metrics,
            strategy_applied=strategy,
            outcome=outcome,
        )
        self.log_history.append(log_entry)

        # 7. 生成报告
        report = {
            "current_state": current_state.name,
            "cognitive_load": total_load,
            "load_breakdown": load_breakdown,
            "is_optimal": self.load_calculator.is_overloaded(total_load) == False,
            "regulation_strategy": strategy.name if strategy else None,
            "regulation_outcome": outcome,
            "recommended_difficulty": task_context.get("recommended_difficulty"),
            "flow_probability": self._calculate_flow_probability(metrics, current_state),
        }

        return report

    def _apply_regulation(self, strategy: RegulationStrategy, context: Dict[str, JsonValueT]) -> str:
        """应用调节策略"""
        actions = {
            RegulationStrategy.INCREASE_CHALLENGE: "增加任务复杂度或引入新约束",
            RegulationStrategy.DECREASE_CHALLENGE: "简化任务要求或减少信息量",
            RegulationStrategy.PROVIDE_HINT: "提供分步指导或示例",
            RegulationStrategy.TAKE_BREAK: "建议短暂休息（5-10 分钟）",
            RegulationStrategy.SWITCH_TASK: "切换到不同类型的任务",
            RegulationStrategy.DECOMPOSE_TASK: "将任务分解为更小的子任务",
            RegulationStrategy.REINFORCE_MOTIVATION: "提供正向反馈和目标提醒",
            RegulationStrategy.ADJUST_PACE: "调整任务节奏或截止时间",
        }

        action = actions.get(strategy, "未知策略")
        return f"已应用策略：{action}"

    def _calculate_flow_probability(
        self, metrics: CognitiveMetrics, state: CognitiveState
    ) -> float:
        """计算进入流状态的概率"""
        if state == CognitiveState.FLOW:
            return 0.95

        # 基于指标计算接近流的程度
        balance_score = 1.0 - abs(metrics.mental_effort - metrics.engagement)
        challenge_skill_ratio = 1.0 if 0.8 < metrics.working_memory_load < 1.2 else 0.5

        probability = balance_score * 0.6 + challenge_skill_ratio * 0.4

        return min(0.9, probability)

    def get_session_summary(self) -> Dict[str, JsonValueT]:
        """获取会话总结"""
        if not self.log_history:
            return {"status": "no_data"}

        # 统计各状态持续时间（简化：按次数）
        state_counts: Dict[str, int] = {}
        for log in self.log_history:
            state_name = log.state.name
            state_counts[state_name] = state_counts.get(state_name, 0) + 1

        # 计算调节成功率
        success_rate = (
            self.successful_regulations / self.total_regulation_count
            if self.total_regulation_count > 0
            else 0.0
        )

        # 找出主导状态
        dominant_state: Optional[str] = max(state_counts, key=lambda k: state_counts[k]) if state_counts else None

        session_duration = (datetime.now() - self.session_start_time).total_seconds()

        return {
            "session_duration_seconds": session_duration,
            "total_monitoring_cycles": len(self.log_history),
            "state_distribution": state_counts,
            "dominant_state": dominant_state,
            "total_regulations": self.total_regulation_count,
            "regulation_success_rate": success_rate,
            "average_cognitive_load": sum(
                log.metrics.working_memory_load for log in self.log_history
            )
            / len(self.log_history),
        }

    def export_logs(self, format: str = "json") -> List[Dict]:
        """导出元认知日志"""
        return [log.to_dict() for log in self.log_history]


class MetaLearner:
    """元学习者 - 从监控历史中学习优化策略"""

    def __init__(self, monitor: MetacognitiveMonitor):
        self.monitor = monitor
        self.patterns_discovered: List[Dict[str, JsonValueT]] = []
        self.optimal_parameters: Dict[str, float] = {}

    def analyze_patterns(self) -> List[Dict[str, JsonValueT]]:
        """分析监控历史中的模式"""
        logs = self.monitor.log_history

        if len(logs) < 10:
            return []

        patterns = []

        # 模式 1: 状态转换序列
        state_sequence = [log.state for log in logs]
        for i in range(len(state_sequence) - 2):
            seq = (state_sequence[i], state_sequence[i + 1], state_sequence[i + 2])
            # 检测常见的负面转换模式
            if seq[0] == CognitiveState.FOCUSED and seq[2] == CognitiveState.OVERLOADED:
                patterns.append(
                    {"type": "overload_warning", "pattern": [s.name for s in seq], "frequency": 1}
                )

        # 模式 2: 最有效的时间段
        morning_logs = [l for l in logs if l.timestamp.hour < 12]
        afternoon_logs = [l for l in logs if 12 <= l.timestamp.hour < 18]

        if morning_logs and afternoon_logs:
            morning_flow = sum(1 for l in morning_logs if l.state == CognitiveState.FLOW) / len(
                morning_logs
            )
            afternoon_flow = sum(1 for l in afternoon_logs if l.state == CognitiveState.FLOW) / len(
                afternoon_logs
            )

            if morning_flow > afternoon_flow + 0.2:
                patterns.append(
                    {
                        "type": "temporal_advantage",
                        "description": "上午更容易进入流状态",
                        "morning_flow_rate": morning_flow,
                        "afternoon_flow_rate": afternoon_flow,
                    }
                )

        self.patterns_discovered = patterns
        return patterns

    def optimize_parameters(self) -> Dict[str, float]:
        """基于历史数据优化监控参数"""
        logs = self.monitor.log_history

        if len(logs) < 20:
            return {}

        # 找到流状态时的指标范围
        flow_logs = [l for l in logs if l.state == CognitiveState.FLOW]

        if flow_logs:
            avg_attention = sum(l.metrics.attention_level for l in flow_logs) / len(flow_logs)
            avg_load = sum(l.metrics.working_memory_load for l in flow_logs) / len(flow_logs)
            avg_engagement = sum(l.metrics.engagement for l in flow_logs) / len(flow_logs)

            self.optimal_parameters = {
                "target_attention": avg_attention,
                "target_load": avg_load,
                "target_engagement": avg_engagement,
                "optimal_challenge_level": avg_load,  # 挑战水平约等于认知负荷
            }

        return self.optimal_parameters

    def generate_recommendations(self) -> List[str]:
        """生成个性化建议"""
        recommendations = []

        summary = self.monitor.get_session_summary()
        patterns = self.analyze_patterns()

        # 基于主导状态的建议
        dominant = summary.get("dominant_state")
        if dominant == "OVERLOADED":
            recommendations.append("经常处于过载状态，建议增加休息时间或分解任务")
        elif dominant == "BORED":
            recommendations.append("经常感到无聊，建议增加任务挑战性或多样性")
        elif dominant == "FATIGUED":
            recommendations.append("频繁疲劳，建议优化作息或减少连续工作时间")

        # 基于模式的建议
        for pattern in patterns:
            if pattern["type"] == "overload_warning":
                recommendations.append("检测到快速过载模式，建议在专注后主动降低负荷")
            elif pattern["type"] == "temporal_advantage":
                recommendations.append("利用高效时间段处理重要任务")

        # 基于调节成功率的建议
        success_rate = summary.get("regulation_success_rate", 0)
        if success_rate < 0.5:
            recommendations.append("调节策略效果不佳，建议尝试不同的应对方法")

        return recommendations


# 辅助函数
def create_sample_metrics(
    attention: float = 0.7,
    load: float = 0.6,
    speed: float = 0.7,
    error: float = 0.15,
    response: float = 1.5,
    confidence: float = 0.7,
    effort: float = 0.6,
    engagement: float = 0.75,
) -> CognitiveMetrics:
    """创建示例认知指标"""
    return CognitiveMetrics(
        attention_level=attention,
        working_memory_load=load,
        processing_speed=speed,
        error_rate=error,
        response_time=response,
        confidence_level=confidence,
        mental_effort=effort,
        engagement=engagement,
    )
