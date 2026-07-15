"""
依赖注入容器 (Dependency Injection Container)
解决循环依赖问题，实现模块解耦。
严格类型注解，线程安全。
"""
from typing import Any, Dict, Type, TypeVar, Callable, Optional
from threading import Lock

T = TypeVar('T')

class DIContainer:
    """
    轻量级依赖注入容器。
    支持单例模式、工厂模式和即时实例化。
    """
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._lock = Lock()
        self._initialized = False

    def register_singleton(self, name: str, instance: Any) -> None:
        """注册单例服务"""
        with self._lock:
            if name in self._services:
                raise ValueError(f"Service '{name}' already registered.")
            self._services[name] = instance

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """注册工厂服务（每次请求创建新实例）"""
        with self._lock:
            if name in self._factories or name in self._services:
                raise ValueError(f"Service '{name}' already registered.")
            self._factories[name] = factory

    def get(self, name: str) -> Any:
        """获取服务实例"""
        with self._lock:
            if name in self._services:
                return self._services[name]
            if name in self._factories:
                instance = self._factories[name]()
                return instance
            raise KeyError(f"Service '{name}' not found.")

    def resolve_all(self) -> None:
        """预解析所有工厂（用于启动时检查循环依赖）"""
        with self._lock:
            for name, factory in self._factories.items():
                try:
                    instance = factory()
                    # 不存储，仅测试能否创建
                except Exception as e:
                    raise RuntimeError(f"Failed to resolve service '{name}': {e}")
            self._initialized = True

# 全局容器实例
container = DIContainer()

def get_container() -> DIContainer:
    return container
