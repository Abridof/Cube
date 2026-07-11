"""
监控服务模块 v1.0
==================
提供系统健康检查、指标收集和告警功能

功能特性:
1. 实时性能监控 (CPU/内存/延迟)
2. 自定义指标收集
3. 健康检查端点
4. 告警规则引擎
5. 指标导出 (Prometheus 格式)

Author: AI Assistant (DevOps Engineer & SRE)
"""

import time
import threading
import json
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """指标类型枚举"""
    COUNTER = "counter"      # 只增不减的计数器
    GAUGE = "gauge"          # 可上下浮动的值
    HISTOGRAM = "histogram"  # 分布统计
    SUMMARY = "summary"      # 摘要统计


@dataclass
class MetricPoint:
    """单个指标数据点"""
    name: str
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
            "labels": self.labels,
            "type": self.metric_type.value,
        }


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric_name: str
    condition: Callable[[float], bool]  # 条件判断函数
    threshold: float
    severity: str = "warning"  # warning, critical, info
    cooldown_seconds: int = 300  # 冷却时间
    last_triggered: Optional[float] = None
    trigger_count: int = 0
    
    def should_trigger(self, value: float) -> bool:
        """检查是否应该触发告警"""
        now = time.time()
        
        # 检查冷却时间
        if self.last_triggered and (now - self.last_triggered) < self.cooldown_seconds:
            return False
        
        # 检查条件
        if self.condition(value):
            return True
        
        return False
    
    def trigger(self):
        """触发告警"""
        self.last_triggered = time.time()
        self.trigger_count += 1


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    component: str
    healthy: bool
    message: str
    latency_ms: float
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component,
            "healthy": self.healthy,
            "message": self.message,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
        }


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self._metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._lock = threading.Lock()
        self._max_points_per_metric = 1000  # 每个指标最多保留的点数
    
    def record(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        metric_type: MetricType = MetricType.GAUGE
    ):
        """记录指标数据点"""
        point = MetricPoint(
            name=name,
            value=value,
            timestamp=time.time(),
            labels=labels or {},
            metric_type=metric_type,
        )
        
        with self._lock:
            self._metrics[name].append(point)
            # 限制历史数据量
            if len(self._metrics[name]) > self._max_points_per_metric:
                self._metrics[name] = self._metrics[name][-self._max_points_per_metric:]
    
    def increment(self, name: str, amount: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """增加计数器"""
        self.record(name, amount, labels, MetricType.COUNTER)
    
    def get_latest(self, name: str, labels: Optional[Dict[str, str]] = None) -> Optional[float]:
        """获取最新指标值"""
        with self._lock:
            if name not in self._metrics:
                return None
            
            points = self._metrics[name]
            if not points:
                return None
            
            if labels:
                # 查找匹配标签的点
                for point in reversed(points):
                    if all(point.labels.get(k) == v for k, v in labels.items()):
                        return point.value
                return None
            else:
                return points[-1].value
    
    def get_history(
        self,
        name: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[MetricPoint]:
        """获取历史数据"""
        with self._lock:
            if name not in self._metrics:
                return []
            
            points = self._metrics[name]
            result = []
            
            for point in points:
                if start_time and point.timestamp < start_time:
                    continue
                if end_time and point.timestamp > end_time:
                    continue
                result.append(point)
            
            return result
    
    def get_all_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有指标"""
        with self._lock:
            return {
                name: [p.to_dict() for p in points]
                for name, points in self._metrics.items()
            }
    
    def export_prometheus(self) -> str:
        """导出为 Prometheus 格式"""
        lines = []
        
        with self._lock:
            for name, points in self._metrics.items():
                if not points:
                    continue
                
                # 添加 HELP 注释
                lines.append(f"# HELP {name} Metric {name}")
                lines.append(f"# TYPE {name} {points[0].metric_type.value}")
                
                # 添加最新的点
                latest = points[-1]
                if latest.labels:
                    label_str = ",".join(f'{k}="{v}"' for k, v in latest.labels.items())
                    lines.append(f"{name}{{{label_str}}} {latest.value}")
                else:
                    lines.append(f"{name} {latest.value}")
        
        return "\n".join(lines)
    
    def clear(self):
        """清空所有指标"""
        with self._lock:
            self._metrics.clear()


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self._checks: Dict[str, Callable[[], HealthCheckResult]] = {}
        self._last_results: Dict[str, HealthCheckResult] = {}
        self._lock = threading.Lock()
    
    def register_check(self, name: str, check_func: Callable[[], HealthCheckResult]):
        """注册健康检查"""
        with self._lock:
            self._checks[name] = check_func
    
    def unregister_check(self, name: str):
        """注销健康检查"""
        with self._lock:
            if name in self._checks:
                del self._checks[name]
    
    def run_check(self, name: str) -> HealthCheckResult:
        """运行单个健康检查"""
        if name not in self._checks:
            return HealthCheckResult(
                component=name,
                healthy=False,
                message="Check not registered",
                latency_ms=0,
            )
        
        start = time.time()
        try:
            result = self._checks[name]()
            result.latency_ms = (time.time() - start) * 1000
        except Exception as e:
            result = HealthCheckResult(
                component=name,
                healthy=False,
                message=f"Check failed: {str(e)}",
                latency_ms=(time.time() - start) * 1000,
            )
        
        with self._lock:
            self._last_results[name] = result
        
        return result
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """运行所有健康检查"""
        results = {}
        for name in self._checks:
            results[name] = self.run_check(name)
        return results
    
    def get_overall_health(self) -> Dict[str, Any]:
        """获取整体健康状态"""
        with self._lock:
            results = list(self._last_results.values())
        
        if not results:
            return {
                "healthy": True,
                "message": "No checks registered",
                "components": {},
            }
        
        healthy_count = sum(1 for r in results if r.healthy)
        total_count = len(results)
        
        return {
            "healthy": healthy_count == total_count,
            "message": f"{healthy_count}/{total_count} components healthy",
            "components": {r.component: r.to_dict() for r in results},
            "timestamp": time.time(),
        }


class AlertManager:
    """告警管理器"""
    
    def __init__(self):
        self._rules: Dict[str, AlertRule] = {}
        self._alerts: List[Dict[str, Any]] = []
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._lock = threading.Lock()
        self._max_alerts = 100
    
    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        with self._lock:
            self._rules[rule.name] = rule
    
    def remove_rule(self, name: str):
        """移除告警规则"""
        with self._lock:
            if name in self._rules:
                del self._rules[name]
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """添加告警回调"""
        self._callbacks.append(callback)
    
    def check_alerts(self, metrics_collector: MetricsCollector):
        """检查所有告警规则"""
        triggered_alerts = []
        
        with self._lock:
            for rule in self._rules.values():
                current_value = metrics_collector.get_latest(rule.metric_name)
                
                if current_value is not None and rule.should_trigger(current_value):
                    rule.trigger()
                    
                    alert = {
                        "rule_name": rule.name,
                        "metric_name": rule.metric_name,
                        "current_value": current_value,
                        "threshold": rule.threshold,
                        "severity": rule.severity,
                        "triggered_at": time.time(),
                        "trigger_count": rule.trigger_count,
                    }
                    
                    triggered_alerts.append(alert)
                    self._alerts.append(alert)
                    
                    # 限制告警数量
                    if len(self._alerts) > self._max_alerts:
                        self._alerts = self._alerts[-self._max_alerts:]
        
        # 触发回调
        for alert in triggered_alerts:
            for callback in self._callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"Alert callback failed: {e}")
        
        return triggered_alerts
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取最近的告警"""
        with self._lock:
            return self._alerts[-count:]
    
    def clear_alerts(self):
        """清空告警"""
        with self._lock:
            self._alerts.clear()


class MonitorService:
    """监控服务主类"""
    
    def __init__(self, service_name: str = "cognitive-engine"):
        self.service_name = service_name
        self.metrics = MetricsCollector()
        self.health_checker = HealthChecker()
        self.alert_manager = AlertManager()
        
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._check_interval = 10.0  # 秒
        
        # 注册默认的健康检查
        self._register_default_checks()
    
    def _register_default_checks(self):
        """注册默认健康检查"""
        def check_memory():
            import psutil
            mem = psutil.virtual_memory()
            usage_percent = mem.percent
            
            return HealthCheckResult(
                component="memory",
                healthy=usage_percent < 90,
                message=f"Memory usage: {usage_percent:.1f}%",
                latency_ms=0,
            )
        
        def check_disk():
            import psutil
            disk = psutil.disk_usage('/')
            usage_percent = disk.percent
            
            return HealthCheckResult(
                component="disk",
                healthy=usage_percent < 95,
                message=f"Disk usage: {usage_percent:.1f}%",
                latency_ms=0,
            )
        
        self.health_checker.register_check("memory", check_memory)
        self.health_checker.register_check("disk", check_disk)
    
    def record_metric(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        metric_type: MetricType = MetricType.GAUGE
    ):
        """记录指标"""
        full_name = f"{self.service_name}_{name}"
        self.metrics.record(full_name, value, labels, metric_type)
    
    def start_monitoring(self, interval: float = 10.0):
        """启动监控"""
        self._running = True
        self._check_interval = interval
        
        def monitor_loop():
            while self._running:
                # 运行健康检查
                self.health_checker.run_all_checks()
                
                # 检查告警
                self.alert_manager.check_alerts(self.metrics)
                
                # 记录系统指标
                try:
                    import psutil
                    self.record_metric("cpu_percent", psutil.cpu_percent())
                    self.record_metric("memory_percent", psutil.virtual_memory().percent)
                except ImportError:
                    pass
                
                time.sleep(self._check_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logger.info(f"Monitoring started for {self.service_name}")
    
    def stop_monitoring(self):
        """停止监控"""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        logger.info(f"Monitoring stopped for {self.service_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取监控状态"""
        health = self.health_checker.get_overall_health()
        recent_alerts = self.alert_manager.get_recent_alerts(5)
        
        return {
            "service_name": self.service_name,
            "health": health,
            "recent_alerts": recent_alerts,
            "monitoring_active": self._running,
            "timestamp": time.time(),
        }
    
    def export_metrics(self, format: str = "prometheus") -> str:
        """导出指标"""
        if format == "prometheus":
            return self.metrics.export_prometheus()
        elif format == "json":
            return json.dumps(self.metrics.get_all_metrics(), indent=2)
        else:
            raise ValueError(f"Unknown format: {format}")


# 便捷函数
def create_monitor(service_name: str = "cognitive-engine") -> MonitorService:
    """创建监控服务的便捷函数"""
    return MonitorService(service_name)


if __name__ == "__main__":
    # 测试示例
    print("=== Monitor Service Test ===\n")
    
    monitor = create_monitor("test-service")
    
    # 记录一些测试指标
    for i in range(10):
        monitor.record_metric("request_latency", 100 + i * 10)
        monitor.record_metric("requests_total", 1, metric_type=MetricType.COUNTER)
    
    # 添加告警规则
    monitor.alert_manager.add_rule(AlertRule(
        name="high_latency",
        metric_name="test-service_request_latency",
        condition=lambda x: x > 150,
        threshold=150,
        severity="warning",
    ))
    
    # 检查告警
    alerts = monitor.alert_manager.check_alerts(monitor.metrics)
    print(f"Triggered alerts: {len(alerts)}")
    
    # 获取状态
    status = monitor.get_status()
    print(f"\nService status: {json.dumps(status, indent=2)}")
    
    # 导出 Prometheus 格式
    print("\nPrometheus metrics:")
    print(monitor.export_metrics("prometheus"))
