#!/usr/bin/env python3
"""
Long Term Evolution - 7x24 小时自主演化引擎
Phase 9: 全系统集成与规模化验证

功能:
- 演化循环管理
- 课程生成器
- 知识巩固
- 变异引擎
- 指标收集
- 报告生成
"""

import os
import sys
import json
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import statistics
from pathlib import Path

# 尝试导入系统编排器
try:
    from system_orchestrator import SystemOrchestrator, Task, Priority
except ImportError:
    # 如果不在同一目录，使用模拟类
    class SystemOrchestrator:
        pass
    class Task:
        pass
    class Priority:
        NORMAL = 2

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EvolutionPhase(Enum):
    """演化阶段"""
    EXPLORATION = "exploration"
    LEARNING = "learning"
    REFLECTION = "reflection"
    MODIFICATION = "modification"
    VALIDATION = "validation"


@dataclass
class EvolutionCycle:
    """演化循环记录"""
    cycle_id: int
    start_time: float
    end_time: Optional[float] = None
    phase: EvolutionPhase = EvolutionPhase.EXPLORATION
    tasks_completed: int = 0
    knowledge_gained: int = 0
    modifications_applied: int = 0
    success_rate: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'cycle_id': self.cycle_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'phase': self.phase.value,
            'tasks_completed': self.tasks_completed,
            'knowledge_gained': self.knowledge_gained,
            'modifications_applied': self.modifications_applied,
            'success_rate': self.success_rate,
            'metrics': self.metrics
        }


@dataclass
class MetricSample:
    """指标样本"""
    timestamp: float
    metric_name: str
    value: float
    context: Dict[str, Any] = field(default_factory=dict)


class CurriculumGenerator:
    """课程生成器 - 根据当前能力生成渐进式学习任务"""
    
    def __init__(self):
        self.difficulty_levels = ['beginner', 'intermediate', 'advanced', 'expert']
        self.task_templates = {
            'perception': [
                {'type': 'image_analysis', 'complexity': 'low'},
                {'type': 'audio_processing', 'complexity': 'medium'},
                {'type': 'multimodal_fusion', 'complexity': 'high'}
            ],
            'reasoning': [
                {'type': 'simple_query', 'depth': 1},
                {'type': 'multi_hop_reasoning', 'depth': 3},
                {'type': 'counterfactual_analysis', 'depth': 5}
            ],
            'learning': [
                {'type': 'pattern_recognition', 'samples': 10},
                {'type': 'concept_formation', 'samples': 50},
                {'type': 'theory_induction', 'samples': 200}
            ]
        }
        
    def generate_task(self, current_ability: float, domain: str) -> Dict[str, Any]:
        """生成任务"""
        # 根据能力水平选择难度
        if current_ability < 0.3:
            level_idx = 0
        elif current_ability < 0.6:
            level_idx = 1
        elif current_ability < 0.8:
            level_idx = 2
        else:
            level_idx = 3
            
        difficulty = self.difficulty_levels[level_idx]
        
        # 从模板中选择任务
        if domain in self.task_templates:
            templates = self.task_templates[domain]
            template = templates[min(level_idx, len(templates)-1)]
        else:
            template = {'type': 'generic', 'complexity': 'medium'}
            
        return {
            'domain': domain,
            'difficulty': difficulty,
            'template': template,
            'generated_at': time.time()
        }
        
    def generate_curriculum(self, num_tasks: int = 10) -> List[Dict[str, Any]]:
        """生成课程"""
        curriculum = []
        domains = list(self.task_templates.keys())
        
        for i in range(num_tasks):
            domain = random.choice(domains)
            # 模拟能力增长
            ability = min(0.9, 0.2 + (i / num_tasks) * 0.7)
            task = self.generate_task(ability, domain)
            curriculum.append(task)
            
        return curriculum


class KnowledgeConsolidator:
    """知识巩固器 - 将短期记忆压缩为长期知识"""
    
    def __init__(self):
        self.short_term_memory: List[Dict] = []
        self.consolidation_threshold = 100  # 条
        
    def add_to_short_term(self, knowledge: Dict):
        """添加到短期记忆"""
        self.short_term_memory.append({
            'content': knowledge,
            'timestamp': time.time(),
            'access_count': 1
        })
        
    def consolidate(self) -> List[Dict]:
        """执行巩固"""
        if len(self.short_term_memory) < self.consolidation_threshold:
            return []
            
        # 按访问频率排序
        sorted_memory = sorted(
            self.short_term_memory,
            key=lambda x: x['access_count'],
            reverse=True
        )
        
        # 提取高频知识
        consolidated = []
        for item in sorted_memory[:50]:  # 保留前 50 个高频知识
            consolidated.append({
                'content': item['content'],
                'consolidated_at': time.time(),
                'strength': item['access_count']
            })
            
        # 清理短期记忆
        self.short_term_memory = sorted_memory[50:]
        
        logger.info(f"Consolidated {len(consolidated)} knowledge items")
        return consolidated


class MutationEngine:
    """变异引擎 - 安全地应用代码修改建议"""
    
    def __init__(self, sandbox_enabled: bool = True):
        self.sandbox_enabled = sandbox_enabled
        self.applied_mutations: List[Dict] = []
        self.rejected_mutations: List[Dict] = []
        
    def apply_mutation(self, mutation: Dict, validate_func: callable) -> bool:
        """应用变异"""
        # 验证变异
        if not validate_func(mutation):
            self.rejected_mutations.append({
                'mutation': mutation,
                'reason': 'validation_failed',
                'timestamp': time.time()
            })
            return False
            
        # 在沙箱中测试（简化版）
        if self.sandbox_enabled:
            # 模拟沙箱测试
            success = random.random() > 0.1  # 90% 成功率
        else:
            success = True
            
        if success:
            self.applied_mutations.append({
                'mutation': mutation,
                'applied_at': time.time(),
                'status': 'success'
            })
            return True
        else:
            self.rejected_mutations.append({
                'mutation': mutation,
                'reason': 'sandbox_test_failed',
                'timestamp': time.time()
            })
            return False
            
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'applied_count': len(self.applied_mutations),
            'rejected_count': len(self.rejected_mutations),
            'success_rate': len(self.applied_mutations) / 
                           (len(self.applied_mutations) + len(self.rejected_mutations))
                           if (len(self.applied_mutations) + len(self.rejected_mutations)) > 0 
                           else 0.0
        }


class MetricCollector:
    """指标收集器"""
    
    def __init__(self):
        self.samples: List[MetricSample] = []
        self._lock = threading.Lock()
        
    def record(self, metric_name: str, value: float, context: Optional[Dict] = None):
        """记录指标"""
        with self._lock:
            sample = MetricSample(
                timestamp=time.time(),
                metric_name=metric_name,
                value=value,
                context=context or {}
            )
            self.samples.append(sample)
            
    def get_metrics(self, metric_name: Optional[str] = None, 
                   time_range: Optional[Tuple[float, float]] = None) -> List[MetricSample]:
        """获取指标"""
        with self._lock:
            filtered = self.samples
            
            if metric_name:
                filtered = [s for s in filtered if s.metric_name == metric_name]
                
            if time_range:
                start, end = time_range
                filtered = [s for s in filtered if start <= s.timestamp <= end]
                
            return filtered
            
    def compute_statistics(self, metric_name: str) -> Dict[str, float]:
        """计算统计信息"""
        samples = self.get_metrics(metric_name)
        if not samples:
            return {}
            
        values = [s.value for s in samples]
        return {
            'count': len(values),
            'mean': statistics.mean(values),
            'std': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'latest': values[-1]
        }


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, report_dir: str = "./reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_daily_report(self, cycles: List[EvolutionCycle], 
                             metrics: MetricCollector) -> str:
        """生成日报"""
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"daily_report_{today}.md"
        filepath = self.report_dir / filename
        
        # 计算汇总统计
        total_tasks = sum(c.tasks_completed for c in cycles)
        total_knowledge = sum(c.knowledge_gained for c in cycles)
        avg_success_rate = statistics.mean([c.success_rate for c in cycles]) if cycles else 0
        
        content = f"""# Daily Evolution Report - {today}

## Summary
- **Total Cycles**: {len(cycles)}
- **Tasks Completed**: {total_tasks}
- **Knowledge Gained**: {total_knowledge}
- **Average Success Rate**: {avg_success_rate*100:.1f}%

## Cycle Details
"""
        
        for cycle in cycles[-10:]:  # 最近 10 个循环
            content += f"\n### Cycle {cycle.cycle_id}\n"
            content += f"- Phase: {cycle.phase.value}\n"
            content += f"- Tasks: {cycle.tasks_completed}\n"
            content += f"- Success Rate: {cycle.success_rate*100:.1f}%\n"
            
        # 添加指标统计
        content += "\n## Key Metrics\n"
        for metric_name in ['task_success', 'knowledge_growth', 'mutation_success']:
            stats = metrics.compute_statistics(metric_name)
            if stats:
                content += f"\n### {metric_name}\n"
                content += f"- Mean: {stats.get('mean', 0):.3f}\n"
                content += f"- Std: {stats.get('std', 0):.3f}\n"
                content += f"- Latest: {stats.get('latest', 0):.3f}\n"
                
        with open(filepath, 'w') as f:
            f.write(content)
            
        logger.info(f"Daily report generated: {filepath}")
        return str(filepath)
        
    def generate_weekly_report(self, daily_reports: List[str]) -> str:
        """生成周报"""
        week_start = datetime.now() - timedelta(days=7)
        filename = f"weekly_report_{week_start.strftime('%Y%m%d')}.md"
        filepath = self.report_dir / filename
        
        content = f"""# Weekly Evolution Report
**Period**: {week_start.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}

## Overview
This report summarizes the autonomous evolution of the cognitive engine over the past week.

## Daily Reports
"""
        
        for report_path in daily_reports:
            content += f"- [{Path(report_path).name}]({report_path})\n"
            
        content += """
## Emergent Behaviors
[Analysis of emergent behaviors observed during the week]

## Recommendations
[Suggestions for next week's evolution focus]
"""
        
        with open(filepath, 'w') as f:
            f.write(content)
            
        logger.info(f"Weekly report generated: {filepath}")
        return str(filepath)


class LongTermEvolution:
    """长期演化引擎 - 核心类"""
    
    def __init__(self, orchestrator: Optional[SystemOrchestrator] = None):
        self.orchestrator = orchestrator
        self.curriculum_generator = CurriculumGenerator()
        self.knowledge_consolidator = KnowledgeConsolidator()
        self.mutation_engine = MutationEngine()
        self.metric_collector = MetricCollector()
        self.report_generator = ReportGenerator()
        
        self.current_cycle = 0
        self.running = False
        self._thread: Optional[threading.Thread] = None
        
        self.evolution_history: List[EvolutionCycle] = []
        self.config = {
            'cycle_duration_seconds': 60,  # 每个循环 60 秒（演示用，实际可更长）
            'tasks_per_cycle': 10,
            'consolidation_interval': 5,  # 每 5 个循环巩固一次
            'report_interval_hours': 24
        }
        
    def start(self, simulated_days: int = 7):
        """启动演化引擎"""
        logger.info(f"Starting long-term evolution ({simulated_days} simulated days)")
        self.running = True
        self._thread = threading.Thread(
            target=self._evolution_loop,
            args=(simulated_days,),
            daemon=True
        )
        self._thread.start()
        
    def stop(self):
        """停止演化引擎"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=10.0)
        logger.info("Long-term evolution stopped")
        
    def _evolution_loop(self, simulated_days: int):
        """演化循环"""
        start_time = time.time()
        seconds_per_day = 10  # 模拟：10 秒 = 1 天
        total_runtime = simulated_days * seconds_per_day
        
        logger.info(f"Evolution loop started (runtime: {total_runtime}s)")
        
        while self.running and (time.time() - start_time) < total_runtime:
            cycle = self._run_evolution_cycle()
            self.evolution_history.append(cycle)
            
            # 定期巩固知识
            if self.current_cycle % self.config['consolidation_interval'] == 0:
                self._consolidate_knowledge()
                
            # 定期生成报告
            elapsed_hours = (time.time() - start_time) / 3600
            if elapsed_hours >= self.config['report_interval_hours'] / 24:
                self._generate_reports()
                
        logger.info(f"Evolution loop completed ({self.current_cycle} cycles)")
        
    def _run_evolution_cycle(self) -> EvolutionCycle:
        """运行单个演化循环"""
        self.current_cycle += 1
        cycle = EvolutionCycle(cycle_id=self.current_cycle, start_time=time.time())
        
        logger.info(f"Starting cycle {cycle.cycle_id}")
        
        # Phase 1: Exploration
        cycle.phase = EvolutionPhase.EXPLORATION
        curriculum = self.curriculum_generator.generate_curriculum(
            self.config['tasks_per_cycle']
        )
        
        tasks_completed = 0
        successes = 0
        
        for task_config in curriculum:
            if not self.running:
                break
                
            # 创建并执行任务
            task = Task(
                task_id=f"cycle_{cycle.cycle_id}_task_{tasks_completed}",
                task_type=f"{task_config['domain']}.execute",
                payload=task_config,
                priority=Priority.NORMAL
            )
            
            # 如果有编排器，提交任务
            if self.orchestrator:
                self.orchestrator.submit_task(task)
                # 等待任务完成（简化处理）
                time.sleep(0.1)
                
            tasks_completed += 1
            # 模拟成功概率随能力增长
            success_prob = min(0.9, 0.4 + (cycle.cycle_id / 100) * 0.5)
            if random.random() < success_prob:
                successes += 1
                cycle.knowledge_gained += random.randint(1, 5)
                
        cycle.tasks_completed = tasks_completed
        cycle.success_rate = successes / tasks_completed if tasks_completed > 0 else 0
        
        # 记录指标
        self.metric_collector.record('task_success', cycle.success_rate, 
                                    {'cycle': cycle.cycle_id})
        self.metric_collector.record('knowledge_growth', cycle.knowledge_gained,
                                    {'cycle': cycle.cycle_id})
        
        # Phase 2: Reflection
        cycle.phase = EvolutionPhase.REFLECTION
        if cycle.success_rate < 0.6:
            # 生成改进假设
            cycle.metrics['improvement_needed'] = True
            
        # Phase 3: Modification (如果需要)
        cycle.phase = EvolutionPhase.MODIFICATION
        if cycle.metrics.get('improvement_needed'):
            mutation = {
                'type': 'parameter_tuning',
                'target': 'learning_rate',
                'change': '+0.01'
            }
            
            if self.mutation_engine.apply_mutation(mutation, lambda x: True):
                cycle.modifications_applied += 1
                
        mutation_stats = self.mutation_engine.get_statistics()
        self.metric_collector.record('mutation_success', mutation_stats['success_rate'])
        
        # 完成循环
        cycle.end_time = time.time()
        cycle.phase = EvolutionPhase.VALIDATION
        
        logger.info(f"Cycle {cycle.cycle_id} completed: "
                   f"tasks={cycle.tasks_completed}, "
                   f"success_rate={cycle.success_rate*100:.1f}%, "
                   f"knowledge={cycle.knowledge_gained}")
                   
        return cycle
        
    def _consolidate_knowledge(self):
        """巩固知识"""
        logger.info("Consolidating knowledge...")
        consolidated = self.knowledge_consolidator.consolidate()
        if consolidated:
            logger.info(f"Consolidated {len(consolidated)} knowledge items")
            
    def _generate_reports(self):
        """生成报告"""
        logger.info("Generating reports...")
        
        # 日报
        daily_report = self.report_generator.generate_daily_report(
            self.evolution_history,
            self.metric_collector
        )
        
        # 如果有足够的历史数据，生成周报
        if len(self.evolution_history) > 50:
            weekly_report = self.report_generator.generate_weekly_report([daily_report])
            
    def get_status(self) -> Dict[str, Any]:
        """获取演化状态"""
        return {
            'running': self.running,
            'current_cycle': self.current_cycle,
            'total_cycles': len(self.evolution_history),
            'total_knowledge_gained': sum(c.knowledge_gained for c in self.evolution_history),
            'average_success_rate': statistics.mean([c.success_rate for c in self.evolution_history]) 
                                   if self.evolution_history else 0,
            'mutation_statistics': self.mutation_engine.get_statistics(),
            'recent_cycles': [c.to_dict() for c in self.evolution_history[-5:]]
        }


def main():
    """主函数 - 演示长期演化"""
    print("=" * 60)
    print("Long Term Evolution - Phase 9 Demo")
    print("=" * 60)
    
    # 创建演化引擎（不带编排器，独立运行）
    evolution = LongTermEvolution()
    
    # 启动演化（模拟 7 天，实际运行约 70 秒）
    print("\nStarting evolution (simulating 7 days)...")
    evolution.start(simulated_days=7)
    
    # 等待演化完成
    try:
        while evolution.running:
            time.sleep(5)
            status = evolution.get_status()
            print(f"Cycle {status['current_cycle']}: "
                  f"Success Rate={status['average_success_rate']*100:.1f}%, "
                  f"Knowledge={status['total_knowledge_gained']}")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        evolution.stop()
        
    # 打印最终状态
    final_status = evolution.get_status()
    print("\n" + "=" * 60)
    print("Final Status:")
    print(f"  Total Cycles: {final_status['total_cycles']}")
    print(f"  Total Knowledge: {final_status['total_knowledge_gained']}")
    print(f"  Average Success Rate: {final_status['average_success_rate']*100:.1f}%")
    print(f"  Mutation Success Rate: {final_status['mutation_statistics']['success_rate']*100:.1f}%")
    
    print("\nDemo completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
