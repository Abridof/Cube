"""
具身环境模块 (Embodied Environment Module)
Phase 6 - Step 2: 高保真仿真环境与多智能体社会

核心功能:
- ContinuousPhysicsEngine: 连续空间物理引擎
- EmbodiedAgent: 具身智能体(感知/行动/动机)
- MultiAgentSociety: 多智能体交互系统
- EmergenceAnalyzer: 涌现行为分析器
"""

import math
import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from enum import Enum
import json

# ============================================================================
# 基础数据结构
# ============================================================================


@dataclass
class Vector2D:
    """2D 向量类"""

    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        return Vector2D(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> "Vector2D":
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / mag, self.y / mag)

    def distance_to(self, other: "Vector2D") -> float:
        return (other - self).magnitude()

    def dot(self, other: "Vector2D") -> float:
        return self.x * other.x + self.y * other.y

    def to_dict(self) -> Dict:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: Dict) -> "Vector2D":
        return cls(data["x"], data["y"])


class ObjectType(Enum):
    """对象类型枚举"""

    AGENT = "agent"
    FOOD = "food"
    OBSTACLE = "obstacle"
    GOAL = "goal"
    OTHER_AGENT = "other_agent"


@dataclass
class GameObject:
    """游戏世界中的对象"""

    id: str
    position: Vector2D
    velocity: Vector2D = field(default_factory=Vector2D)
    acceleration: Vector2D = field(default_factory=Vector2D)
    radius: float = 1.0
    obj_type: ObjectType = ObjectType.OBSTACLE
    mass: float = 1.0
    active: bool = True

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "position": self.position.to_dict(),
            "velocity": self.velocity.to_dict(),
            "obj_type": self.obj_type.value,
        }


# ============================================================================
# 连续物理引擎
# ============================================================================


class ContinuousPhysicsEngine:
    """
    2D 连续空间物理引擎
    支持碰撞检测、重力、摩擦力和速度积分
    """

    def __init__(
        self,
        world_size: Tuple[float, float] = (100.0, 100.0),
        gravity: float = 0.0,
        friction: float = 0.98,
    ):
        self.world_size = Vector2D(*world_size)
        self.gravity = gravity
        self.friction = friction
        self.objects: Dict[str, GameObject] = {}

    def add_object(self, obj: GameObject):
        """添加对象到物理世界"""
        self.objects[obj.id] = obj

    def remove_object(self, obj_id: str):
        """从物理世界移除对象"""
        if obj_id in self.objects:
            del self.objects[obj_id]

    def update(self, dt: float = 0.016):
        """更新物理状态 (dt: 时间步长，默认~60FPS)"""
        for obj in self.objects.values():
            if not obj.active:
                continue

            # 应用重力
            obj.acceleration.y += self.gravity

            # 积分速度
            obj.velocity = obj.velocity + obj.acceleration * dt

            # 应用摩擦力
            obj.velocity = obj.velocity * self.friction

            # 积分位置
            obj.position = obj.position + obj.velocity * dt

            # 边界碰撞检测
            self._handle_boundary_collision(obj)

            # 重置加速度
            obj.acceleration = Vector2D(0, 0)

        # 物体间碰撞检测
        self._handle_object_collisions()

    def _handle_boundary_collision(self, obj: GameObject):
        """处理边界碰撞"""
        # 左右边界
        if obj.position.x - obj.radius < 0:
            obj.position.x = obj.radius
            obj.velocity.x *= -0.8
        elif obj.position.x + obj.radius > self.world_size.x:
            obj.position.x = self.world_size.x - obj.radius
            obj.velocity.x *= -0.8

        # 上下边界
        if obj.position.y - obj.radius < 0:
            obj.position.y = obj.radius
            obj.velocity.y *= -0.8
        elif obj.position.y + obj.radius > self.world_size.y:
            obj.position.y = self.world_size.y - obj.radius
            obj.velocity.y *= -0.8

    def _handle_object_collisions(self):
        """处理物体间碰撞"""
        objects_list = list(self.objects.values())
        for i in range(len(objects_list)):
            for j in range(i + 1, len(objects_list)):
                obj1 = objects_list[i]
                obj2 = objects_list[j]

                if not obj1.active or not obj2.active:
                    continue

                dist = obj1.position.distance_to(obj2.position)
                min_dist = obj1.radius + obj2.radius

                if dist < min_dist and dist > 0:
                    # 碰撞响应
                    normal = (obj2.position - obj1.position).normalize()

                    # 相对速度
                    rel_vel = obj1.velocity - obj2.velocity
                    vel_along_normal = rel_vel.dot(normal)

                    # 仅在接近时处理
                    if vel_along_normal > 0:
                        continue

                    # 弹性碰撞
                    restitution = 0.7
                    impulse_scalar = -(1 + restitution) * vel_along_normal
                    impulse_scalar /= 1 / obj1.mass + 1 / obj2.mass

                    impulse = normal * impulse_scalar
                    obj1.velocity = obj1.velocity + impulse * (1 / obj1.mass)
                    obj2.velocity = obj2.velocity - impulse * (1 / obj2.mass)

                    # 分离重叠
                    overlap = min_dist - dist
                    separation = normal * (overlap / 2)
                    obj1.position = obj1.position - separation
                    obj2.position = obj2.position + separation

    def check_line_of_sight(self, start: Vector2D, end: Vector2D) -> bool:
        """检查两点间是否有视线(无障碍物)"""
        # 简化的射线检测
        steps = int(start.distance_to(end) * 2)
        if steps == 0:
            return True

        direction = (end - start).normalize()

        for i in range(steps):
            point = start + direction * (i * 0.5)
            for obj in self.objects.values():
                if obj.obj_type == ObjectType.OBSTACLE and obj.active:
                    if point.distance_to(obj.position) < obj.radius:
                        return False
        return True

    def get_nearby_objects(self, position: Vector2D, radius: float) -> List[GameObject]:
        """获取指定半径内的所有对象"""
        nearby = []
        for obj in self.objects.values():
            if obj.active and position.distance_to(obj.position) < radius:
                nearby.append(obj)
        return nearby

    def to_dict(self) -> Dict:
        return {
            "world_size": self.world_size.to_dict(),
            "objects": [obj.to_dict() for obj in self.objects.values() if obj.active],
        }


# ============================================================================
# 具身智能体
# ============================================================================


class MotivationType(Enum):
    """动机类型"""

    CURIOSITY = "curiosity"  # 好奇心
    SURVIVAL = "survival"  # 生存欲
    SOCIAL = "social"  # 社交需求
    ACHIEVEMENT = "achievement"  # 成就需求


@dataclass
class InternalState:
    """智能体内部状态"""

    energy: float = 100.0
    health: float = 100.0
    curiosity_level: float = 50.0
    stress: float = 0.0
    last_prediction_error: float = 0.0

    def update(self, dt: float = 1.0):
        """随时间更新内部状态"""
        self.energy = max(0, self.energy - 0.1 * dt)
        self.curiosity_level = min(100, self.curiosity_level + 0.05 * dt)
        if self.energy < 30:
            self.stress = min(100, self.stress + 0.5 * dt)
        else:
            self.stress = max(0, self.stress - 0.2 * dt)


@dataclass
class Action:
    """智能体动作"""

    action_type: str
    parameters: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class EmbodiedAgent:
    """
    具身智能体
    具备感知、行动和内在动机系统
    """

    def __init__(
        self,
        agent_id: str,
        position: Vector2D,
        vision_range: float = 20.0,
        field_of_view: float = 360.0,
    ):
        self.id = agent_id
        self.internal_state = InternalState()
        self.vision_range = vision_range
        self.field_of_view = field_of_view

        # 物理实体
        self.game_object = GameObject(
            id=f"agent_{agent_id}",
            position=position,
            radius=2.0,
            obj_type=ObjectType.AGENT,
            mass=1.0,
        )

        # 认知组件
        self.known_objects: Dict[str, GameObject] = {}
        self.action_history: List[Action] = []
        self.prediction_model: Dict[str, float] = {}  # 简单的预测模型

        # 动机权重
        self.motivation_weights = {
            MotivationType.CURIOSITY: 0.4,
            MotivationType.SURVIVAL: 0.5,
            MotivationType.SOCIAL: 0.1,
            MotivationType.ACHIEVEMENT: 0.0,
        }

    def perceive(self, physics_engine: ContinuousPhysicsEngine) -> List[GameObject]:
        """感知周围环境"""
        visible_objects = []

        # 获取视野内的对象
        nearby = physics_engine.get_nearby_objects(self.game_object.position, self.vision_range)

        for obj in nearby:
            if obj.id == self.game_object.id:
                continue

            # 检查是否在视野角度内
            direction = (obj.position - self.game_object.position).normalize()
            forward = Vector2D(0, 1)  # 假设朝上为前方
            angle = math.acos(direction.dot(forward)) * 180 / math.pi

            if angle <= self.field_of_view / 2:
                # 检查视线是否被遮挡
                if physics_engine.check_line_of_sight(self.game_object.position, obj.position):
                    visible_objects.append(obj)
                    self.known_objects[obj.id] = obj

        return visible_objects

    def decide_action(self, perceived_objects: List[GameObject], dt: float = 1.0) -> Action:
        """基于内在动机决定行动"""
        self.internal_state.update(dt)

        # 计算各动机的驱动力
        drives = {}

        # 生存驱动 (低能量时寻找食物)
        if self.internal_state.energy < 40:
            food_objects = [o for o in perceived_objects if o.obj_type == ObjectType.FOOD]
            if food_objects:
                nearest_food = min(
                    food_objects, key=lambda x: x.position.distance_to(self.game_object.position)
                )
                drives[MotivationType.SURVIVAL] = (
                    1.0 - self.internal_state.energy / 100
                ) * self.motivation_weights[MotivationType.SURVIVAL]

        # 好奇驱动 (探索未知或预测误差大的区域)
        unknown_objects = [o for o in perceived_objects if o.id not in self.known_objects]
        if unknown_objects:
            drives[MotivationType.CURIOSITY] = (
                self.internal_state.curiosity_level / 100
            ) * self.motivation_weights[MotivationType.CURIOSITY]

        # 选择最强驱动
        if not drives:
            # 默认随机探索
            return self._generate_exploration_action()

        strongest_motivation = max(drives.keys(), key=lambda m: drives[m])

        # 根据动机生成行动
        if strongest_motivation == MotivationType.SURVIVAL:
            return self._generate_approach_action(
                [o for o in perceived_objects if o.obj_type == ObjectType.FOOD]
            )
        elif strongest_motivation == MotivationType.CURIOSITY:
            return self._generate_exploration_action(unknown_objects)
        else:
            return self._generate_exploration_action()

    def _generate_approach_action(self, targets: List[GameObject]) -> Action:
        """生成接近目标的行动"""
        if not targets:
            return self._generate_exploration_action()

        nearest = min(targets, key=lambda x: x.position.distance_to(self.game_object.position))

        direction = (nearest.position - self.game_object.position).normalize()
        force = direction * 5.0  # 施加力

        return Action(
            action_type="apply_force", parameters={"force_x": force.x, "force_y": force.y}
        )

    def _generate_exploration_action(self, interesting_objects: List[GameObject] = None) -> Action:
        """生成探索行动"""
        if interesting_objects:
            # 探索有趣的目标
            target = random.choice(interesting_objects)
            direction = (target.position - self.game_object.position).normalize()
        else:
            # 随机方向
            angle = random.uniform(0, 2 * math.pi)
            direction = Vector2D(math.cos(angle), math.sin(angle))

        force = direction * 3.0
        return Action(
            action_type="apply_force", parameters={"force_x": force.x, "force_y": force.y}
        )

    def execute_action(self, action: Action, physics_engine: ContinuousPhysicsEngine):
        """执行行动"""
        if action.action_type == "apply_force":
            fx = action.parameters.get("force_x", 0)
            fy = action.parameters.get("force_y", 0)
            self.game_object.acceleration = Vector2D(fx, fy)

        self.action_history.append(action)
        if len(self.action_history) > 100:
            self.action_history.pop(0)

    def update_prediction_model(self, actual_outcome: Dict):
        """更新预测模型 (基于实际结果)"""
        # 简化的学习：记录最后一次的预测误差
        expected = self.prediction_model.get("last_position", None)
        if expected:
            actual_pos = actual_outcome.get("position", self.game_object.position)
            error = Vector2D(
                actual_pos.x - expected.get("x", actual_pos.x),
                actual_pos.y - expected.get("y", actual_pos.y),
            ).magnitude()
            self.internal_state.last_prediction_error = error

        # 更新预测
        self.prediction_model["last_position"] = {
            "x": self.game_object.position.x,
            "y": self.game_object.position.y,
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "internal_state": {
                "energy": self.internal_state.energy,
                "health": self.internal_state.health,
                "curiosity_level": self.internal_state.curiosity_level,
                "stress": self.internal_state.stress,
            },
            "position": self.game_object.position.to_dict(),
            "known_objects_count": len(self.known_objects),
        }


# ============================================================================
# 多智能体社会系统
# ============================================================================


@dataclass
class Message:
    """智能体间消息"""

    sender_id: str
    receiver_id: Optional[str]  # None 表示广播
    content: Dict
    timestamp: float = field(default_factory=time.time)


class MultiAgentSociety:
    """
    多智能体社会系统
    管理多个智能体的生命周期、通信和协作
    """

    def __init__(self, physics_engine: ContinuousPhysicsEngine):
        self.physics_engine = physics_engine
        self.agents: Dict[str, EmbodiedAgent] = {}
        self.message_queue: List[Message] = []
        self.collaboration_tasks: List[Dict] = []
        self.interaction_log: List[Dict] = []

    def add_agent(self, agent: EmbodiedAgent):
        """添加智能体到社会"""
        self.agents[agent.id] = agent
        self.physics_engine.add_object(agent.game_object)

    def remove_agent(self, agent_id: str):
        """移除智能体"""
        if agent_id in self.agents:
            self.physics_engine.remove_object(self.agents[agent_id].game_object.id)
            del self.agents[agent_id]

    def broadcast_message(self, sender_id: str, content: Dict):
        """广播消息给所有智能体"""
        msg = Message(sender_id=sender_id, receiver_id=None, content=content)
        self.message_queue.append(msg)

    def send_message(self, sender_id: str, receiver_id: str, content: Dict):
        """点对点发送消息"""
        msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
        self.message_queue.append(msg)

    def process_messages(self):
        """处理消息队列"""
        for msg in self.message_queue:
            if msg.receiver_id is None:
                # 广播：所有其他智能体接收
                for agent_id, agent in self.agents.items():
                    if agent_id != msg.sender_id:
                        self._deliver_message(agent, msg)
            else:
                # 点对点
                if msg.receiver_id in self.agents:
                    self._deliver_message(self.agents[msg.receiver_id], msg)

        self.message_queue.clear()

    def _deliver_message(self, agent: EmbodiedAgent, message: Message):
        """向智能体投递消息"""
        # 简化处理：记录日志
        self.interaction_log.append(
            {
                "type": "message",
                "from": message.sender_id,
                "to": agent.id,
                "content": message.content,
                "timestamp": message.timestamp,
            }
        )

    def add_collaboration_task(self, task: Dict):
        """添加协作任务"""
        self.collaboration_tasks.append(task)

    def step(self, dt: float = 1.0):
        """执行一个社会模拟步骤"""
        # 1. 每个智能体感知环境
        perceptions = {}
        for agent_id, agent in self.agents.items():
            perceptions[agent_id] = agent.perceive(self.physics_engine)

        # 2. 每个智能体决定行动
        actions = {}
        for agent_id, agent in self.agents.items():
            actions[agent_id] = agent.decide_action(perceptions[agent_id], dt)

        # 3. 执行行动
        for agent_id, action in actions.items():
            self.agents[agent_id].execute_action(action, self.physics_engine)

        # 4. 更新物理世界
        self.physics_engine.update(dt)

        # 5. 更新预测模型
        for agent_id, agent in self.agents.items():
            agent.update_prediction_model({"position": agent.game_object.position})

        # 6. 处理消息
        self.process_messages()

        # 7. 记录交互
        self.interaction_log.append(
            {
                "type": "step",
                "timestamp": time.time(),
                "agents_count": len(self.agents),
                "messages_processed": len(self.message_queue),
            }
        )

    def get_statistics(self) -> Dict:
        """获取社会统计信息"""
        return {
            "agent_count": len(self.agents),
            "total_interactions": len(self.interaction_log),
            "pending_messages": len(self.message_queue),
            "active_tasks": len(self.collaboration_tasks),
        }

    def to_dict(self) -> Dict:
        return {
            "agents": [a.to_dict() for a in self.agents.values()],
            "statistics": self.get_statistics(),
        }


# ============================================================================
# 涌现行为分析器
# ============================================================================


class EmergenceAnalyzer:
    """
    涌现行为分析器
    使用信息论指标量化群体行为的复杂性
    """

    def __init__(self):
        self.behavior_history: List[Dict] = []

    def record_behavior(self, agents_states: List[Dict]):
        """记录智能体群体状态"""
        self.behavior_history.append({"timestamp": time.time(), "states": agents_states})

    def calculate_shannon_entropy(self, data: List) -> float:
        """计算香农熵"""
        if not data:
            return 0.0

        # 统计频率
        freq = {}
        for item in data:
            key = str(item)
            freq[key] = freq.get(key, 0) + 1

        # 计算熵
        total = len(data)
        entropy = 0.0
        for count in freq.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)

        return entropy

    def calculate_mutual_information(self, series_a: List, series_b: List) -> float:
        """计算互信息 (衡量两个序列的相关性)"""
        if len(series_a) != len(series_b) or not series_a:
            return 0.0

        # 联合分布
        joint_freq = {}
        for a, b in zip(series_a, series_b):
            key = (str(a), str(b))
            joint_freq[key] = joint_freq.get(key, 0) + 1

        # 边缘分布
        freq_a = {}
        freq_b = {}
        for a in series_a:
            freq_a[str(a)] = freq_a.get(str(a), 0) + 1
        for b in series_b:
            freq_b[str(b)] = freq_b.get(str(b), 0) + 1

        total = len(series_a)
        mi = 0.0

        for (a, b), joint_count in joint_freq.items():
            p_ab = joint_count / total
            p_a = freq_a[a] / total
            p_b = freq_b[b] / total

            if p_ab > 0 and p_a > 0 and p_b > 0:
                mi += p_ab * math.log2(p_ab / (p_a * p_b))

        return mi

    def analyze_emergence(self) -> Dict:
        """分析涌现行为"""
        if len(self.behavior_history) < 2:
            return {"status": "insufficient_data"}

        # 提取位置序列
        positions_over_time = []
        for record in self.behavior_history[-50:]:  # 最近 50 帧
            frame_positions = []
            for state in record["states"]:
                pos = (state["position"]["x"], state["position"]["y"])
                frame_positions.append(pos)
            positions_over_time.append(frame_positions)

        # 计算群体分散度
        dispersions = []
        for frame in positions_over_time:
            if len(frame) < 2:
                continue
            center_x = sum(p[0] for p in frame) / len(frame)
            center_y = sum(p[1] for p in frame) / len(frame)
            dispersion = sum((p[0] - center_x) ** 2 + (p[1] - center_y) ** 2 for p in frame) / len(
                frame
            )
            dispersions.append(dispersion)

        # 计算熵
        entropy = self.calculate_shannon_entropy(dispersions)

        # 分析协调性 (如果有多智能体)
        coordination = 0.0
        if len(positions_over_time) > 1 and len(positions_over_time[0]) > 1:
            # 比较不同智能体的运动模式
            agent_0_x = [f[0][0] for f in positions_over_time]
            agent_1_x = [f[1][0] for f in positions_over_time if len(f) > 1]
            if agent_1_x:
                coordination = self.calculate_mutual_information(
                    agent_0_x, agent_1_x[: len(agent_0_x)]
                )

        return {
            "status": "analyzed",
            "entropy": entropy,
            "coordination": coordination,
            "avg_dispersion": sum(dispersions) / len(dispersions) if dispersions else 0,
            "frames_analyzed": len(positions_over_time),
        }

    def detect_emergent_patterns(self) -> List[Dict]:
        """检测涌现模式"""
        patterns = []

        if len(self.behavior_history) < 10:
            return patterns

        # 检测聚集行为
        recent = self.behavior_history[-10:]
        dispersions = []
        for record in recent:
            positions = [(s["position"]["x"], s["position"]["y"]) for s in record["states"]]
            if len(positions) < 2:
                continue
            center_x = sum(p[0] for p in positions) / len(positions)
            center_y = sum(p[1] for p in positions) / len(positions)
            disp = sum((p[0] - center_x) ** 2 + (p[1] - center_y) ** 2 for p in positions) / len(
                positions
            )
            dispersions.append(disp)

        if len(dispersions) >= 5:
            trend = sum(
                dispersions[i + 1] - dispersions[i] for i in range(len(dispersions) - 1)
            ) / (len(dispersions) - 1)

            if trend < -0.5:
                patterns.append(
                    {
                        "type": "aggregation",
                        "confidence": abs(trend) / 2,
                        "description": "智能体正在聚集",
                    }
                )
            elif trend > 0.5:
                patterns.append(
                    {"type": "dispersion", "confidence": trend / 2, "description": "智能体正在分散"}
                )

        return patterns


# ============================================================================
# 主程序与演示
# ============================================================================


def run_demo():
    """运行具身环境演示"""
    print("=" * 60)
    print("具身环境演示 - Embodied Environment Demo")
    print("=" * 60)

    # 创建物理世界
    physics = ContinuousPhysicsEngine(world_size=(100, 100))

    # 添加一些障碍物和目标
    for i in range(5):
        obs = GameObject(
            id=f"obs_{i}",
            position=Vector2D(random.uniform(10, 90), random.uniform(10, 90)),
            radius=3.0,
            obj_type=ObjectType.OBSTACLE,
        )
        physics.add_object(obs)

    for i in range(3):
        food = GameObject(
            id=f"food_{i}",
            position=Vector2D(random.uniform(10, 90), random.uniform(10, 90)),
            radius=1.5,
            obj_type=ObjectType.FOOD,
        )
        physics.add_object(food)

    # 创建多智能体社会
    society = MultiAgentSociety(physics)

    # 添加 3 个智能体
    for i in range(3):
        agent = EmbodiedAgent(
            agent_id=f"agent_{i}",
            position=Vector2D(random.uniform(20, 80), random.uniform(20, 80)),
            vision_range=25.0,
        )
        society.add_agent(agent)
        print(
            f"✓ 创建智能体 {agent.id} 在位置 ({agent.game_object.position.x:.1f}, {agent.game_object.position.y:.1f})"
        )

    # 创建分析器
    analyzer = EmergenceAnalyzer()

    print("\n开始模拟 (100 步)...")
    print("-" * 60)

    # 运行模拟
    for step in range(100):
        society.step(dt=0.5)

        # 每 20 步记录一次用于分析
        if step % 20 == 0:
            states = [a.to_dict() for a in society.agents.values()]
            analyzer.record_behavior(states)

            # 打印状态
            energies = [a.internal_state.energy for a in society.agents.values()]
            print(
                f"Step {step:3d}: 平均能量={sum(energies)/len(energies):.1f}, "
                f"交互数={len(society.interaction_log)}"
            )

    # 分析涌现行为
    print("\n" + "=" * 60)
    print("涌现行为分析结果:")
    print("-" * 60)

    analysis = analyzer.analyze_emergence()
    print(f"状态：{analysis.get('status', 'N/A')}")
    if analysis.get("status") == "analyzed":
        print(f"香农熵：{analysis['entropy']:.4f}")
        print(f"协调性 (互信息): {analysis['coordination']:.4f}")
        print(f"平均分散度：{analysis['avg_dispersion']:.2f}")
        print(f"分析帧数：{analysis['frames_analyzed']}")

    patterns = analyzer.detect_emergent_patterns()
    if patterns:
        print("\n检测到的涌现模式:")
        for p in patterns:
            print(f"  - {p['type']}: {p['description']} " f"(置信度：{p['confidence']:.2f})")
    else:
        print("\n未检测到明显的涌现模式")

    print("\n" + "=" * 60)
    print("演示完成!")

    return society, analyzer


if __name__ == "__main__":
    society, analyzer = run_demo()
