"""
阶段 14: 元认知监控系统测试
测试覆盖：认知负荷计算、状态检测、策略选择、难度调整、元认知监控、元学习等
"""

import pytest
from datetime import datetime, timedelta
from src.modules.metacognition import (
    CognitiveState,
    RegulationStrategy,
    CognitiveMetrics,
    MetacognitiveLog,
    CognitiveLoadCalculator,
    StateDetector,
    StrategySelector,
    DifficultyAdjuster,
    MetacognitiveMonitor,
    MetaLearner,
    create_sample_metrics
)


class TestCognitiveMetrics:
    """测试认知指标数据类"""
    
    def test_default_values(self):
        metrics = CognitiveMetrics()
        assert metrics.attention_level == 0.0
        assert metrics.working_memory_load == 0.0
        assert metrics.error_rate == 0.0
    
    def test_custom_values(self):
        metrics = CognitiveMetrics(
            attention_level=0.8,
            working_memory_load=0.6,
            error_rate=0.1
        )
        assert metrics.attention_level == 0.8
        assert metrics.working_memory_load == 0.6
        assert metrics.error_rate == 0.1
    
    def test_to_dict(self):
        metrics = CognitiveMetrics(attention_level=0.75)
        result = metrics.to_dict()
        assert isinstance(result, dict)
        assert 'attention_level' in result
        assert result['attention_level'] == 0.75


class TestCognitiveLoadCalculator:
    """测试认知负荷计算器"""
    
    def test_intrinsic_load_basic(self):
        calc = CognitiveLoadCalculator()
        load = calc.calculate_intrinsic_load(element_interactivity=0.5, prior_knowledge=0.5)
        assert 0.0 <= load <= 1.0
    
    def test_intrinsic_load_high_interaction_low_knowledge(self):
        calc = CognitiveLoadCalculator()
        load = calc.calculate_intrinsic_load(element_interactivity=0.9, prior_knowledge=0.1)
        assert load > 0.5  # 高交互低知识应产生高负荷
    
    def test_intrinsic_load_low_interaction_high_knowledge(self):
        calc = CognitiveLoadCalculator()
        load = calc.calculate_intrinsic_load(element_interactivity=0.2, prior_knowledge=0.9)
        assert load < 0.3  # 低交互高知识应产生低负荷
    
    def test_extraneous_load(self):
        calc = CognitiveLoadCalculator()
        load = calc.calculate_extraneous_load(presentation_complexity=0.7, distraction_level=0.5)
        assert 0.0 <= load <= 1.0
    
    def test_germane_load(self):
        calc = CognitiveLoadCalculator()
        load = calc.calculate_germane_load(schema_construction=0.8, automation_level=0.6)
        assert 0.0 <= load <= 1.0
    
    def test_total_load_weighted(self):
        calc = CognitiveLoadCalculator(
            intrinsic_load_weight=0.4,
            extraneous_load_weight=0.3,
            germane_load_weight=0.3
        )
        total = calc.calculate_total_load(intrinsic=0.6, extraneous=0.4, germane=0.5)
        expected = 0.6 * 0.4 + 0.4 * 0.3 + 0.5 * 0.3
        assert abs(total - expected) < 0.01
    
    def test_total_load_capped(self):
        calc = CognitiveLoadCalculator()
        total = calc.calculate_total_load(intrinsic=1.0, extraneous=1.0, germane=1.0)
        assert total <= 1.0  # 应该被限制在 1.0
    
    def test_is_overloaded(self):
        calc = CognitiveLoadCalculator()
        assert calc.is_overloaded(0.9) == True
        assert calc.is_overloaded(0.8) == False
        assert calc.is_overloaded(0.85) == False  # 阈值是>0.85
    
    def test_optimal_load_range(self):
        calc = CognitiveLoadCalculator()
        low, high = calc.optimal_load_range()
        assert low < high
        assert 0.0 <= low <= 1.0
        assert 0.0 <= high <= 1.0


class TestStateDetector:
    """测试认知状态检测器"""
    
    def test_detect_flow_state(self):
        detector = StateDetector()
        metrics = create_sample_metrics(
            attention=0.85,
            load=0.65,
            confidence=0.75,
            engagement=0.8,
            error=0.1
        )
        state = detector.detect_state(metrics)
        assert state == CognitiveState.FLOW
    
    def test_detect_focused_state(self):
        detector = StateDetector()
        metrics = create_sample_metrics(
            attention=0.7,
            load=0.5,
            error=0.2
        )
        state = detector.detect_state(metrics)
        assert state == CognitiveState.FOCUSED
    
    def test_detect_overloaded_state(self):
        detector = StateDetector()
        metrics = create_sample_metrics(
            load=0.9,
            confidence=0.3,
            error=0.4
        )
        state = detector.detect_state(metrics)
        assert state == CognitiveState.OVERLOADED
    
    def test_detect_confused_state(self):
        detector = StateDetector()
        metrics = create_sample_metrics(
            load=0.65,
            confidence=0.4,
            error=0.4
        )
        state = detector.detect_state(metrics)
        assert state == CognitiveState.CONFUSED
    
    def test_detect_fatigued_state(self):
        detector = StateDetector()
        metrics = create_sample_metrics(
            attention=0.3,
            effort=0.8,
            engagement=0.3
        )
        state = detector.detect_state(metrics)
        assert state == CognitiveState.FATIGUED
    
    def test_detect_bored_state(self):
        detector = StateDetector()
        metrics = create_sample_metrics(
            load=0.2,
            engagement=0.3,
            attention=0.3  # 低注意力也是无聊的特征
        )
        state = detector.detect_state(metrics)
        assert state == CognitiveState.BORED
    
    def test_detect_anxious_state(self):
        detector = StateDetector()
        metrics = create_sample_metrics(
            effort=0.8,
            confidence=0.3,
            error=0.5,
            load=0.5  # 中等负荷，避免被识别为困惑
        )
        state = detector.detect_state(metrics)
        assert state == CognitiveState.ANXIOUS
    
    def test_update_history(self):
        detector = StateDetector()
        for _ in range(10):
            detector.update_history(CognitiveState.FOCUSED)
        assert len(detector.state_history) == 10
        
        # 超过 100 个应该被截断
        for _ in range(95):
            detector.update_history(CognitiveState.FLOW)
        assert len(detector.state_history) == 100


class TestStrategySelector:
    """测试调节策略选择器"""
    
    def test_select_strategy_for_confused(self):
        selector = StrategySelector()
        strategy = selector.select_strategy(CognitiveState.CONFUSED, {})
        assert strategy == RegulationStrategy.PROVIDE_HINT
    
    def test_select_strategy_for_overloaded(self):
        selector = StrategySelector()
        strategy = selector.select_strategy(CognitiveState.OVERLOADED, {})
        assert strategy == RegulationStrategy.DECOMPOSE_TASK
    
    def test_select_strategy_for_fatigued(self):
        selector = StrategySelector()
        strategy = selector.select_strategy(CognitiveState.FATIGUED, {})
        assert strategy == RegulationStrategy.TAKE_BREAK
    
    def test_select_strategy_for_bored(self):
        selector = StrategySelector()
        strategy = selector.select_strategy(CognitiveState.BORED, {})
        assert strategy == RegulationStrategy.INCREASE_CHALLENGE
    
    def test_select_strategy_for_anxious(self):
        selector = StrategySelector()
        strategy = selector.select_strategy(CognitiveState.ANXIOUS, {})
        assert strategy == RegulationStrategy.DECREASE_CHALLENGE
    
    def test_select_strategy_no_action_for_flow(self):
        selector = StrategySelector()
        strategy = selector.select_strategy(CognitiveState.FLOW, {})
        assert strategy is None
    
    def test_context_critical_task_override(self):
        selector = StrategySelector()
        # 关键任务时，疲劳不应该休息
        strategy = selector.select_strategy(
            CognitiveState.FATIGUED, 
            {'task_criticality': True}
        )
        assert strategy == RegulationStrategy.DECREASE_CHALLENGE
    
    def test_context_time_pressure_override(self):
        selector = StrategySelector()
        # 时间紧迫时，过载不分解任务
        strategy = selector.select_strategy(
            CognitiveState.OVERLOADED,
            {'time_pressure': True}
        )
        assert strategy == RegulationStrategy.PROVIDE_HINT
    
    def test_record_outcome(self):
        selector = StrategySelector()
        selector.record_outcome(RegulationStrategy.PROVIDE_HINT, 0.8)
        selector.record_outcome(RegulationStrategy.PROVIDE_HINT, 0.9)
        assert len(selector.strategy_effectiveness[RegulationStrategy.PROVIDE_HINT]) == 2


class TestDifficultyAdjuster:
    """测试动态难度调整器"""
    
    def test_initial_difficulty(self):
        adjuster = DifficultyAdjuster(initial_difficulty=0.5)
        assert adjuster.current_difficulty == 0.5
    
    def test_adjust_increase_on_good_performance(self):
        adjuster = DifficultyAdjuster(target_performance=0.75)
        # 表现好于目标，应该增加难度
        new_diff = adjuster.adjust(0.9)
        assert new_diff > 0.5
    
    def test_adjust_decrease_on_poor_performance(self):
        adjuster = DifficultyAdjuster(target_performance=0.75)
        # 表现差于目标，应该降低难度
        new_diff = adjuster.adjust(0.3)
        assert new_diff < 0.5
    
    def test_adjust_bounds(self):
        adjuster = DifficultyAdjuster()
        # 连续好表现
        for _ in range(30):
            new_diff = adjuster.adjust(1.0)
        assert new_diff <= 0.9  # 上限
        
        # 重置
        adjuster = DifficultyAdjuster()
        # 连续差表现
        for _ in range(30):
            new_diff = adjuster.adjust(0.0)
        assert new_diff >= 0.1  # 下限
    
    def test_get_recommended_difficulty(self):
        adjuster = DifficultyAdjuster()
        rec = adjuster.get_recommended_difficulty(skill_level=0.6)
        assert rec > 0.6  # 难度应略高于技能水平


class TestMetacognitiveMonitor:
    """测试元认知监控器"""
    
    def test_monitor_basic(self):
        monitor = MetacognitiveMonitor(agent_id="test_agent")
        metrics = create_sample_metrics()
        context = {
            'element_interactivity': 0.5,
            'prior_knowledge': 0.6
        }
        
        report = monitor.monitor(metrics, context)
        
        assert 'current_state' in report
        assert 'cognitive_load' in report
        assert 'load_breakdown' in report
        assert 'is_optimal' in report
    
    def test_monitor_load_calculation(self):
        monitor = MetacognitiveMonitor()
        metrics = create_sample_metrics()
        context = {
            'element_interactivity': 0.8,
            'prior_knowledge': 0.2,
            'presentation_complexity': 0.7,
            'distraction_level': 0.5
        }
        
        report = monitor.monitor(metrics, context)
        
        assert report['load_breakdown']['intrinsic'] > 0.5
        assert report['cognitive_load'] > 0
    
    def test_monitor_state_detection(self):
        monitor = MetacognitiveMonitor()
        # 流状态指标 - 需要更高的注意力和参与度
        metrics = create_sample_metrics(
            attention=0.9,
            load=0.65,
            engagement=0.85,
            confidence=0.75,
            error=0.1
        )
        context = {}
        
        report = monitor.monitor(metrics, context)
        assert report['current_state'] == 'FLOW'
    
    def test_monitor_regulation_triggered(self):
        monitor = MetacognitiveMonitor()
        # 过载状态 - 需要更高的负荷和更低的信心
        metrics = create_sample_metrics(
            load=0.95,
            confidence=0.2,
            effort=0.9  # 高努力也表明过载
        )
        context = {}
        
        report = monitor.monitor(metrics, context)
        assert report['regulation_strategy'] is not None
        assert 'DECOMPOSE_TASK' in report['regulation_strategy']
    
    def test_monitor_difficulty_adjustment(self):
        monitor = MetacognitiveMonitor()
        metrics = create_sample_metrics()
        context = {'performance': 0.9}
        
        report = monitor.monitor(metrics, context)
        assert 'recommended_difficulty' in report
        assert report['recommended_difficulty'] is not None
    
    def test_monitor_logging(self):
        monitor = MetacognitiveMonitor()
        metrics = create_sample_metrics()
        
        monitor.monitor(metrics, {})
        monitor.monitor(metrics, {})
        
        assert len(monitor.log_history) == 2
    
    def test_flow_probability(self):
        monitor = MetacognitiveMonitor()
        metrics = create_sample_metrics(
            attention=0.85,
            load=0.65,
            engagement=0.8
        )
        context = {}
        
        report = monitor.monitor(metrics, context)
        assert report['flow_probability'] > 0.5
    
    def test_session_summary(self):
        monitor = MetacognitiveMonitor()
        metrics = create_sample_metrics()
        
        for _ in range(5):
            monitor.monitor(metrics, {})
        
        summary = monitor.get_session_summary()
        
        assert summary['total_monitoring_cycles'] == 5
        assert 'state_distribution' in summary
        assert 'dominant_state' in summary
    
    def test_export_logs(self):
        monitor = MetacognitiveMonitor()
        metrics = create_sample_metrics()
        
        monitor.monitor(metrics, {})
        
        logs = monitor.export_logs()
        assert len(logs) == 1
        assert 'timestamp' in logs[0]
        assert 'state' in logs[0]
        assert 'metrics' in logs[0]


class TestMetaLearner:
    """测试元学习者"""
    
    def test_analyze_patterns_insufficient_data(self):
        monitor = MetacognitiveMonitor()
        learner = MetaLearner(monitor)
        
        # 少于 10 条日志
        for _ in range(5):
            monitor.monitor(create_sample_metrics(), {})
        
        patterns = learner.analyze_patterns()
        assert patterns == []
    
    def test_analyze_patterns_with_data(self):
        monitor = MetacognitiveMonitor()
        learner = MetaLearner(monitor)
        
        # 生成足够的数据
        for _ in range(15):
            monitor.monitor(create_sample_metrics(), {})
        
        patterns = learner.analyze_patterns()
        assert isinstance(patterns, list)
    
    def test_optimize_parameters_insufficient_data(self):
        monitor = MetacognitiveMonitor()
        learner = MetaLearner(monitor)
        
        for _ in range(10):
            monitor.monitor(create_sample_metrics(), {})
        
        params = learner.optimize_parameters()
        assert params == {}
    
    def test_generate_recommendations(self):
        monitor = MetacognitiveMonitor()
        learner = MetaLearner(monitor)
        
        # 生成一些过载状态 - 需要更明显的过载指标
        for _ in range(10):
            metrics = create_sample_metrics(
                load=0.95, 
                confidence=0.2,
                effort=0.9,
                attention=0.4
            )
            monitor.monitor(metrics, {})
        
        recommendations = learner.generate_recommendations()
        assert isinstance(recommendations, list)
        # 应该有过载相关的建议
        assert len(recommendations) > 0


class TestIntegration:
    """集成测试"""
    
    def test_full_monitoring_cycle(self):
        """测试完整的监控循环"""
        monitor = MetacognitiveMonitor(agent_id="integration_test")
        learner = MetaLearner(monitor)
        
        # 模拟一个学习会话
        states = [
            (create_sample_metrics(attention=0.7, load=0.5), {'performance': 0.7}),
            (create_sample_metrics(attention=0.8, load=0.6), {'performance': 0.8}),
            (create_sample_metrics(attention=0.9, load=0.7), {'performance': 0.85}),
            (create_sample_metrics(attention=0.6, load=0.85), {'performance': 0.5}),  # 开始过载
            (create_sample_metrics(attention=0.5, load=0.9), {'performance': 0.4}),  # 过载
        ]
        
        reports = []
        for metrics, context in states:
            report = monitor.monitor(metrics, context)
            reports.append(report)
        
        # 验证报告生成
        assert len(reports) == 5
        assert all('current_state' in r for r in reports)
        
        # 获取总结
        summary = monitor.get_session_summary()
        assert summary['total_monitoring_cycles'] == 5
        
        # 生成建议
        recommendations = learner.generate_recommendations()
        assert isinstance(recommendations, list)
    
    def test_adaptive_difficulty_adjustment(self):
        """测试自适应难度调整"""
        monitor = MetacognitiveMonitor()
        
        # 模拟表现波动
        performances = [0.9, 0.85, 0.8, 0.6, 0.4, 0.5, 0.7, 0.75]
        difficulties = []
        
        for perf in performances:
            metrics = create_sample_metrics()
            context = {'performance': perf}
            report = monitor.monitor(metrics, context)
            difficulties.append(report.get('recommended_difficulty', 0.5))
        
        # 难度应该随表现调整
        assert difficulties[0] > 0.5  # 初始好表现增加难度
        # 经过多次调整后，差表现会导致难度降低（相对于持续好表现的情况）
        assert difficulties[-1] < 0.6  # 最终难度不会太高
    
    def test_state_transitions(self):
        """测试状态转换"""
        monitor = MetacognitiveMonitor()
        
        # 从专注到流到过载 - 使用更明确的指标
        scenarios = [
            (create_sample_metrics(attention=0.7, load=0.5, engagement=0.6), 'FOCUSED'),
            (create_sample_metrics(attention=0.9, load=0.65, engagement=0.85, confidence=0.75, error=0.1), 'FLOW'),
            (create_sample_metrics(attention=0.4, load=0.95, confidence=0.2, effort=0.9), 'OVERLOADED'),
        ]
        
        detected_states = []
        for metrics, _ in scenarios:
            report = monitor.monitor(metrics, {})
            detected_states.append(report['current_state'])
        
        assert detected_states[0] == 'FOCUSED'
        assert detected_states[1] == 'FLOW'
        assert detected_states[2] == 'OVERLOADED'


class TestEdgeCases:
    """边界情况测试"""
    
    def test_extreme_metric_values(self):
        """测试极端指标值"""
        monitor = MetacognitiveMonitor()
        
        # 所有指标为 0
        metrics_zero = CognitiveMetrics()
        report = monitor.monitor(metrics_zero, {})
        assert report is not None
        
        # 所有指标为 1
        metrics_one = CognitiveMetrics(
            attention_level=1.0,
            working_memory_load=1.0,
            processing_speed=1.0,
            error_rate=1.0,
            response_time=1.0,
            confidence_level=1.0,
            mental_effort=1.0,
            engagement=1.0
        )
        report = monitor.monitor(metrics_one, {})
        assert report is not None
    
    def test_empty_context(self):
        """测试空上下文"""
        monitor = MetacognitiveMonitor()
        metrics = create_sample_metrics()
        
        report = monitor.monitor(metrics, {})
        assert report is not None
        assert report['cognitive_load'] >= 0
    
    def test_rapid_state_changes(self):
        """测试快速状态变化"""
        monitor = MetacognitiveMonitor()
        
        # 快速切换不同状态
        for i in range(20):
            if i % 4 == 0:
                metrics = create_sample_metrics(attention=0.9, load=0.6)  # FLOW
            elif i % 4 == 1:
                metrics = create_sample_metrics(load=0.9)  # OVERLOADED
            elif i % 4 == 2:
                metrics = create_sample_metrics(load=0.2, engagement=0.2)  # BORED
            else:
                metrics = create_sample_metrics(effort=0.8, confidence=0.3)  # ANXIOUS
            
            report = monitor.monitor(metrics, {})
            assert report is not None
        
        summary = monitor.get_session_summary()
        assert summary['total_monitoring_cycles'] == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
