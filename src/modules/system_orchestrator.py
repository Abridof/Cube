#!/usr/bin/env python3
"""
System Orchestrator - 统一调度所有认知模块
Phase 9: 全系统集成与规模化验证

功能:
- 模块注册与发现
- 资源管理 (CPU/GPU/内存)
- 事件总线 (发布/订阅)
- 认知流水线编排
- 健康监控
- 检查点管理
"""

import os
import sys
import json
import time
import threading
import queue
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Type, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import importlib
import traceback
import hashlib
import hmac
import json
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ModuleStatus(Enum):
    """模块状态枚举"""

    UNLOADED = "unloaded"
    LOADING = "loading"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"


class Priority(Enum):
    """任务优先级"""

    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

    def __lt__(self, other):
        if isinstance(other, Priority):
            return self.value < other.value
        return NotImplemented


@dataclass
class ModuleInfo:
    """模块信息"""

    name: str
    class_name: str
    module_path: str
    status: ModuleStatus = ModuleStatus.UNLOADED
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    instance: Any = None
    load_time: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "class_name": self.class_name,
            "module_path": self.module_path,
            "status": self.status.value,
            "version": self.version,
            "dependencies": self.dependencies,
            "config": self.config,
            "load_time": self.load_time,
            "error_message": self.error_message,
        }


@dataclass
class Event:
    """事件对象"""

    event_type: str
    source: str
    data: Any
    timestamp: float = field(default_factory=time.time)
    priority: Priority = Priority.NORMAL
    correlation_id: Optional[str] = None

    def __lt__(self, other):
        if isinstance(other, Event):
            return self.priority.value < other.priority.value
        return NotImplemented

    def to_dict(self) -> Dict:
        return {
            "event_type": self.event_type,
            "source": self.source,
            "data": self.data,
            "timestamp": self.timestamp,
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
        }


@dataclass
class Task:
    """任务对象"""

    task_id: str
    task_type: str
    payload: Any
    priority: Priority = Priority.NORMAL
    created_at: float = field(default_factory=time.time)
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    def __lt__(self, other):
        if isinstance(other, Task):
            return (self.priority.value, self.created_at) < (other.priority.value, other.created_at)
        return NotImplemented

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "payload": self.payload,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class EventBus:
    """发布/订阅模式的事件总线"""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue = queue.PriorityQueue()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
        logger.info(f"Subscribed to event type: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅"""
        with self._lock:
            if event_type in self._subscribers:
                self._subscribers[event_type].remove(callback)

    def publish(self, event: Event):
        """发布事件"""
        priority_value = event.priority.value
        self._queue.put((priority_value, event))
        logger.debug(f"Published event: {event.event_type}")

    def start(self):
        """启动事件处理线程"""
        self._running = True
        self._thread = threading.Thread(target=self._process_events, daemon=True)
        self._thread.start()
        logger.info("Event bus started")

    def stop(self):
        """停止事件处理"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("Event bus stopped")

    def _process_events(self):
        """处理事件队列"""
        while self._running:
            try:
                _, event = self._queue.get(timeout=1.0)
                self._dispatch_event(event)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    def _dispatch_event(self, event: Event):
        """分派事件给订阅者"""
        with self._lock:
            callbacks = self._subscribers.get(event.event_type, [])
            callbacks.extend(self._subscribers.get("*", []))  # 通配符订阅

        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")


class ResourceManager:
    """资源管理器"""

    def __init__(self, max_cpu: int = 4, max_memory_mb: int = 4096):
        self.max_cpu = max_cpu
        self.max_memory_mb = max_memory_mb
        self.allocated_cpu = 0
        self.allocated_memory_mb = 0
        self._lock = threading.Lock()

    def allocate(self, cpu: int = 1, memory_mb: int = 512) -> bool:
        """分配资源"""
        with self._lock:
            if (
                self.allocated_cpu + cpu <= self.max_cpu
                and self.allocated_memory_mb + memory_mb <= self.max_memory_mb
            ):
                self.allocated_cpu += cpu
                self.allocated_memory_mb += memory_mb
                return True
            return False

    def release(self, cpu: int = 1, memory_mb: int = 512):
        """释放资源"""
        with self._lock:
            self.allocated_cpu = max(0, self.allocated_cpu - cpu)
            self.allocated_memory_mb = max(0, self.allocated_memory_mb - memory_mb)

    def get_usage(self) -> Dict[str, float]:
        """获取资源使用率"""
        return {
            "cpu_usage": self.allocated_cpu / self.max_cpu if self.max_cpu > 0 else 0,
            "memory_usage": (
                self.allocated_memory_mb / self.max_memory_mb if self.max_memory_mb > 0 else 0
            ),
        }


class HealthMonitor:
    """健康监控器"""

    def __init__(self, orchestrator: "SystemOrchestrator"):
        self.orchestrator = orchestrator
        self.check_interval = 5.0  # 秒
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """启动监控"""
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("Health monitor started")

    def stop(self):
        """停止监控"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                self._check_modules()
                self._check_resources()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Health check error: {e}")

    def _check_modules(self):
        """检查模块健康状态"""
        for name, info in self.orchestrator.modules.items():
            if info.status == ModuleStatus.RUNNING:
                # 简单的健康检查：确认实例存在
                if info.instance is None:
                    logger.warning(f"Module {name} instance is None while status is RUNNING")
                    info.status = ModuleStatus.ERROR

    def _check_resources(self):
        """检查资源状态"""
        usage = self.orchestrator.resource_manager.get_usage()
        if usage["cpu_usage"] > 0.9:
            logger.warning(f"High CPU usage: {usage['cpu_usage']*100:.1f}%")
        if usage["memory_usage"] > 0.9:
            logger.warning(f"High memory usage: {usage['memory_usage']*100:.1f}%")


class CheckpointSecurityError(Exception):
    """检查点安全异常"""
    pass


class RestrictedJSONEncoder(json.JSONEncoder):
    """受限的 JSON 编码器，只允许安全类型"""
    
    SAFE_TYPES = (str, int, float, bool, list, dict, type(None))
    
    def default(self, obj):
        if isinstance(obj, self.SAFE_TYPES):
            return super().default(obj)
        # 将非安全类型转换为字符串表示
        return f"<{type(obj).__name__}:{str(obj)}>"


class CheckpointManager:
    """检查点管理器 - 使用 JSON 替代 Pickle 以避免 RCE 漏洞"""

    # 检查点文件版本
    CHECKPOINT_VERSION = "1.0"
    
    def __init__(self, checkpoint_dir: str = "./checkpoints", secret_key: Optional[str] = None):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        # HMAC 密钥（生产环境应从环境变量加载）
        self._secret_key = (secret_key or os.environ.get("CHECKPOINT_SECRET_KEY", "dev-secret-key-change-in-production")).encode()

    def _compute_hmac(self, data: bytes) -> bytes:
        """计算数据的 HMAC 签名"""
        return hmac.new(self._secret_key, data, hashlib.sha256).digest()

    def save_checkpoint(self, state: Dict[str, Any], name: str = "auto") -> str:
        """保存检查点为 JSON 格式并添加 HMAC 签名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.json"
        filepath = self.checkpoint_dir / filename

        # 序列化为 JSON
        json_data = json.dumps(
            {
                "version": self.CHECKPOINT_VERSION,
                "timestamp": timestamp,
                "state": state
            },
            cls=RestrictedJSONEncoder,
            indent=2
        ).encode('utf-8')

        # 计算 HMAC 签名 (SHA256 = 32 bytes)
        signature = self._compute_hmac(json_data)

        # 写入文件：先写签名 (32 字节), 再写数据
        with open(filepath, "wb") as f:
            f.write(signature)
            f.write(json_data)

        logger.info(f"Checkpoint saved: {filepath} (with HMAC signature)")
        return str(filepath)

    def load_checkpoint(self, filepath: str) -> Dict[str, Any]:
        """加载检查点并验证 HMAC 签名"""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {filepath}")

        with open(path, "rb") as f:
            # 读取签名 (32 字节，SHA256)
            stored_signature = f.read(32)
            if len(stored_signature) != 32:
                raise CheckpointSecurityError(f"Invalid checkpoint format: missing signature in {filepath}")
            
            # 读取数据
            json_data = f.read()
        
        # 验证 HMAC 签名
        expected_signature = self._compute_hmac(json_data)
        if not hmac.compare_digest(stored_signature, expected_signature):
            raise CheckpointSecurityError(f"Checkpoint integrity check failed: {filepath} (possible tampering)")

        # 解析 JSON
        try:
            data = json.loads(json_data.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise CheckpointSecurityError(f"Invalid checkpoint JSON in {filepath}: {e}")

        # 验证版本
        version = data.get("version")
        if version != self.CHECKPOINT_VERSION:
            logger.warning(f"Checkpoint version mismatch: expected {self.CHECKPOINT_VERSION}, got {version}")

        logger.info(f"Checkpoint loaded: {filepath} (HMAC verified)")
        return data.get("state", {})

    def list_checkpoints(self) -> List[str]:
        """列出所有检查点"""
        return [str(p) for p in self.checkpoint_dir.glob("*.json")]


class CognitivePipeline:
    """认知流水线编排器"""

    def __init__(self, orchestrator: "SystemOrchestrator"):
        self.orchestrator = orchestrator
        self.stages: List[str] = []

    def add_stage(self, module_name: str):
        """添加流水线阶段"""
        self.stages.append(module_name)
        return self

    def execute(self, input_data: Any) -> Any:
        """执行流水线"""
        current_data = input_data

        for stage in self.stages:
            if stage not in self.orchestrator.modules:
                raise ValueError(f"Module {stage} not found")

            module_info = self.orchestrator.modules[stage]
            if module_info.status != ModuleStatus.READY:
                raise RuntimeError(f"Module {stage} not ready")

            # 调用模块的处理方法
            try:
                if hasattr(module_info.instance, "process"):
                    current_data = module_info.instance.process(current_data)
                elif hasattr(module_info.instance, "execute"):
                    current_data = module_info.instance.execute(current_data)
                else:
                    logger.warning(f"Module {stage} has no process or execute method")
            except Exception as e:
                logger.error(f"Error in stage {stage}: {e}")
                raise

        return current_data


class SystemOrchestrator:
    """系统编排器 - 核心类"""

    def __init__(self, config_path: Optional[str] = None):
        self.modules: Dict[str, ModuleInfo] = {}
        self.event_bus = EventBus()
        self.resource_manager = ResourceManager()
        self.health_monitor = HealthMonitor(self)
        self.checkpoint_manager = CheckpointManager()
        self.pipeline = CognitivePipeline(self)

        self._task_queue = queue.PriorityQueue()
        self._workers: List[threading.Thread] = []
        self._running = False
        self._num_workers = 4

        # 加载配置
        self.config = self._load_config(config_path)

        # 注册内置模块
        self._register_builtin_modules()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            "max_cpu": 4,
            "max_memory_mb": 4096,
            "num_workers": 4,
            "checkpoint_interval": 300,  # 5分钟
            "modules": {},
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                user_config = json.load(f)
                default_config.update(user_config)

        return default_config

    def _register_builtin_modules(self):
        """注册内置模块"""
        # 定义核心模块列表
        builtin_modules = [
            ModuleInfo(
                name="ucr_layer", class_name="UnifiedRepresentationEngine", module_path="ucr_layer"
            ),
            ModuleInfo(
                name="knowledge_graph", class_name="KnowledgeGraph", module_path="knowledge_graph"
            ),
            ModuleInfo(
                name="multimodal_perception",
                class_name="MultimodalFusionEngine",
                module_path="multimodal_perception",
            ),
            ModuleInfo(name="world_model", class_name="WorldModel", module_path="world_model"),
            ModuleInfo(
                name="neural_backend",
                class_name="NeuralSymbolicLearner",
                module_path="neural_backend",
            ),
            ModuleInfo(
                name="cognitive_loop",
                class_name="CognitiveLoopController",
                module_path="cognitive_loop",
            ),
            ModuleInfo(
                name="embodied_environment",
                class_name="MultiAgentSociety",
                module_path="embodied_environment",
            ),
            ModuleInfo(
                name="self_reflection",
                class_name="SelfReflectionEngine",
                module_path="self_reflection",
            ),
        ]

        for module in builtin_modules:
            self.modules[module.name] = module

    def register_module(self, module_info: ModuleInfo):
        """注册模块"""
        self.modules[module_info.name] = module_info
        logger.info(f"Registered module: {module_info.name}")

    def load_module(self, module_name: str) -> bool:
        """加载模块"""
        if module_name not in self.modules:
            logger.error(f"Module {module_name} not found")
            return False

        module_info = self.modules[module_name]

        try:
            module_info.status = ModuleStatus.LOADING
            start_time = time.time()

            # 动态导入模块
            module = importlib.import_module(module_info.module_path)
            module_class = getattr(module, module_info.class_name)

            # 实例化
            instance = module_class(**module_info.config)
            module_info.instance = instance
            module_info.load_time = time.time() - start_time
            module_info.status = ModuleStatus.READY

            logger.info(f"Loaded module: {module_name} ({module_info.load_time:.3f}s)")

            # 发布模块加载事件
            self.event_bus.publish(
                Event(
                    event_type="module.loaded",
                    source="orchestrator",
                    data={"module_name": module_name},
                )
            )

            return True

        except Exception as e:
            module_info.status = ModuleStatus.ERROR
            module_info.error_message = str(e)
            logger.error(f"Failed to load module {module_name}: {e}")
            traceback.print_exc()
            return False

    def load_all_modules(self) -> Dict[str, bool]:
        """加载所有模块"""
        results = {}
        for name in self.modules:
            results[name] = self.load_module(name)
        return results

    def start(self):
        """启动系统"""
        logger.info("Starting system orchestrator...")

        # 启动事件总线
        self.event_bus.start()

        # 启动健康监控
        self.health_monitor.start()

        # 启动工作线程
        self._running = True
        for i in range(self._num_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self._workers.append(worker)

        # 将所有模块设置为运行状态
        for name, info in self.modules.items():
            if info.status == ModuleStatus.READY:
                info.status = ModuleStatus.RUNNING

        logger.info("System orchestrator started")

    def stop(self):
        """停止系统"""
        logger.info("Stopping system orchestrator...")

        self._running = False

        # 停止健康监控
        self.health_monitor.stop()

        # 停止事件总线
        self.event_bus.stop()

        # 等待工作线程结束
        for worker in self._workers:
            worker.join(timeout=5.0)

        # 设置模块状态为未加载
        for info in self.modules.values():
            info.status = ModuleStatus.UNLOADED

        logger.info("System orchestrator stopped")

    def submit_task(self, task: Task):
        """提交任务"""
        # 处理优先级（可能是 Enum 或 int）
        if hasattr(task.priority, "value"):
            priority_value = task.priority.value
        else:
            priority_value = task.priority
        self._task_queue.put((priority_value, task))
        logger.debug(f"Task submitted: {task.task_id}")

    def _worker_loop(self):
        """工作线程循环"""
        while self._running:
            try:
                _, task = self._task_queue.get(timeout=1.0)
                self._execute_task(task)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")

    def _execute_task(self, task: Task):
        """执行任务"""
        task.status = "running"
        task.started_at = time.time()

        try:
            # 根据任务类型路由到相应模块
            if task.task_type.startswith("perception"):
                result = self._run_perception_task(task)
            elif task.task_type.startswith("reasoning"):
                result = self._run_reasoning_task(task)
            elif task.task_type.startswith("learning"):
                result = self._run_learning_task(task)
            elif task.task_type.startswith("reflection"):
                result = self._run_reflection_task(task)
            else:
                result = self._run_generic_task(task)

            task.result = result
            task.status = "completed"

        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            logger.error(f"Task {task.task_id} failed: {e}")

        finally:
            task.completed_at = time.time()

    def _run_perception_task(self, task: Task) -> Any:
        """运行感知任务"""
        if "multimodal_perception" not in self.modules:
            raise RuntimeError("Multimodal perception module not loaded")

        module = self.modules["multimodal_perception"].instance
        return module.process(task.payload)

    def _run_reasoning_task(self, task: Task) -> Any:
        """运行推理任务"""
        if "knowledge_graph" not in self.modules:
            raise RuntimeError("Knowledge graph module not loaded")

        module = self.modules["knowledge_graph"].instance
        return module.query(task.payload)

    def _run_learning_task(self, task: Task) -> Any:
        """运行学习任务"""
        if "neural_backend" not in self.modules:
            raise RuntimeError("Neural backend module not loaded")

        module = self.modules["neural_backend"].instance
        return module.learn(task.payload)

    def _run_reflection_task(self, task: Task) -> Any:
        """运行反思任务"""
        if "self_reflection" not in self.modules:
            raise RuntimeError("Self reflection module not loaded")

        module = self.modules["self_reflection"].instance
        return module.reflect(task.payload)

    def _run_generic_task(self, task: Task) -> Any:
        """运行通用任务"""
        # 默认返回输入数据
        return task.payload

    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            "timestamp": datetime.now().isoformat(),
            "running": self._running,
            "modules": {name: info.to_dict() for name, info in self.modules.items()},
            "resources": self.resource_manager.get_usage(),
            "queue_size": self._task_queue.qsize(),
            "workers": len(self._workers),
        }

    def save_state(self, name: str = "auto") -> str:
        """保存系统状态"""
        state = {
            "modules": {name: info.to_dict() for name, info in self.modules.items()},
            "config": self.config,
            "timestamp": time.time(),
        }
        return self.checkpoint_manager.save_checkpoint(state, name)

    def load_state(self, filepath: str):
        """加载系统状态"""
        state = self.checkpoint_manager.load_checkpoint(filepath)
        self.config = state.get("config", self.config)
        # 注意：这里不恢复模块实例，需要重新加载
        logger.info(f"State loaded from {filepath}")


def main():
    """主函数 - 演示系统编排器"""
    print("=" * 60)
    print("System Orchestrator - Phase 9 Demo")
    print("=" * 60)

    # 创建编排器
    orchestrator = SystemOrchestrator()

    # 加载所有模块
    print("\nLoading modules...")
    results = orchestrator.load_all_modules()

    success_count = sum(1 for v in results.values() if v)
    print(f"Loaded {success_count}/{len(results)} modules successfully")

    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {name}")

    # 启动系统
    print("\nStarting system...")
    orchestrator.start()

    # 等待片刻
    time.sleep(2)

    # 获取状态
    status = orchestrator.get_status()
    print(f"\nSystem Status:")
    print(f"  Running: {status['running']}")
    print(f"  Modules: {len(status['modules'])}")
    print(
        f"  Resource Usage: CPU={status['resources']['cpu_usage']*100:.1f}%, Memory={status['resources']['memory_usage']*100:.1f}%"
    )

    # 提交示例任务
    print("\nSubmitting tasks...")
    for i in range(5):
        task = Task(
            task_id=f"task_{i}",
            task_type="reasoning.query",
            payload={"query": f"Test query {i}"},
            priority=Priority.NORMAL,
        )
        orchestrator.submit_task(task)

    # 等待任务完成
    time.sleep(2)

    # 保存检查点
    checkpoint_path = orchestrator.save_state("demo")
    print(f"\nCheckpoint saved: {checkpoint_path}")

    # 停止系统
    print("\nStopping system...")
    orchestrator.stop()

    print("\nDemo completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
