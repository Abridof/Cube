# AI Cognition Engine - 性能基准测试

"""
性能基准测试套件
用于评估系统各模块的性能表现
"""

import time
import statistics
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
import json


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    throughput: float  # ops/sec


class PerformanceBenchmark:
    """性能基准测试器"""
    
    def __init__(self, warmup_iterations: int = 3):
        self.warmup_iterations = warmup_iterations
        self.results: List[BenchmarkResult] = []
    
    def benchmark(
        self,
        func: Callable,
        name: str,
        iterations: int = 10,
        *args,
        **kwargs
    ) -> BenchmarkResult:
        """执行基准测试"""
        # Warmup
        for _ in range(self.warmup_iterations):
            func(*args, **kwargs)
        
        # Actual measurements
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func(*args, **kwargs)
            end = time.perf_counter()
            times.append(end - start)
        
        # Calculate statistics
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        throughput = iterations / total_time if total_time > 0 else 0.0
        
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            throughput=throughput
        )
        
        self.results.append(result)
        return result
    
    def report(self) -> str:
        """生成性能报告"""
        if not self.results:
            return "No benchmark results available."
        
        lines = ["=" * 70, "PERFORMANCE BENCHMARK REPORT", "=" * 70, ""]
        
        for result in self.results:
            lines.append(f"Test: {result.name}")
            lines.append(f"  Iterations:   {result.iterations}")
            lines.append(f"  Total Time:   {result.total_time:.4f}s")
            lines.append(f"  Avg Time:     {result.avg_time:.6f}s ± {result.std_dev:.6f}s")
            lines.append(f"  Min/Max:      {result.min_time:.6f}s / {result.max_time:.6f}s")
            lines.append(f"  Throughput:   {result.throughput:.2f} ops/sec")
            lines.append("")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def save_json(self, filepath: str):
        """保存结果为 JSON"""
        data = {
            "results": [
                {
                    "name": r.name,
                    "iterations": r.iterations,
                    "total_time": r.total_time,
                    "avg_time": r.avg_time,
                    "min_time": r.min_time,
                    "max_time": r.max_time,
                    "std_dev": r.std_dev,
                    "throughput": r.throughput
                }
                for r in self.results
            ]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def run_benchmarks():
    """运行所有基准测试"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.insert(0, '/workspace/src')
    
    benchmark = PerformanceBenchmark()
    
    # 示例：UCR Layer 性能测试
    try:
        from modules.ucr_layer import UnifiedRepresentationEngine
        
        def ucr_create_unit():
            engine = UnifiedRepresentationEngine()
            engine.create_unit("This is a test unit", content_type="text", domain="general")
        
        result = benchmark.benchmark(
            ucr_create_unit,
            "UCR_CreateUnit",
            iterations=20
        )
        print(f"✓ UCR Create Unit: {result.avg_time*1000:.2f}ms")
    except Exception as e:
        print(f"✗ UCR benchmark failed: {e}")
    
    # 示例：Knowledge Graph 性能测试
    try:
        from modules.knowledge_graph import KnowledgeGraph
        from modules.ucr_layer import CognitiveUnit
        
        def kg_add_node():
            kg = KnowledgeGraph()
            for i in range(10):
                unit = CognitiveUnit(
                    id=f"unit_{i}",
                    content=f"Test content {i}",
                    vector=[0.1] * 10,
                    symbolic_nodes={},
                    content_type="text"
                )
                kg.add_node(unit)
        
        result = benchmark.benchmark(
            kg_add_node,
            "KG_AddNodes",
            iterations=10
        )
        print(f"✓ KG Add Nodes: {result.avg_time*1000:.2f}ms")
    except Exception as e:
        print(f"✗ KG benchmark failed: {e}")
    
    # 示例：World Model 性能测试
    try:
        from modules.world_model import WorldModel
        
        def wm_observe():
            wm = WorldModel()
            for i in range(5):
                state_vars = {f"feature_{j}": float(i) for j in range(3)}
                wm.observe(state_vars)
        
        result = benchmark.benchmark(
            wm_observe,
            "WM_Observe",
            iterations=10
        )
        print(f"✓ WM Observe: {result.avg_time*1000:.2f}ms")
    except Exception as e:
        print(f"✗ WM benchmark failed: {e}")
    
    # 打印完整报告
    print("\n" + benchmark.report())
    
    # 保存结果
    benchmark.save_json("reports/benchmark_results.json")
    print("Results saved to reports/benchmark_results.json")
    
    return benchmark


if __name__ == "__main__":
    run_benchmarks()
