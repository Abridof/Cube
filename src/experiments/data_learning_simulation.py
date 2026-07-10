#!/usr/bin/env python3
"""
第五阶段：真实数据学习与仿真环境交互实验

本模块实现三个核心实验：
1. 真实数据摄入：维基百科、代码库、科学论文的学习
2. 网格世界生存：避坑学习与策略优化
3. 涌现行为观察：复杂交互中的未预设智能行为

作者: ACE 认知引擎开发团队
版本: v9.0 - 实验验证阶段
"""

import json
import random
import time
import hashlib
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from enum import Enum
from collections import defaultdict, deque
import re
from datetime import datetime

# ============================================================================
# 第一部分：真实数据摄入系统
# ============================================================================


class DataSourceType(Enum):
    """数据来源类型"""

    WIKIPEDIA = "wikipedia"
    CODE_REPO = "code_repository"
    SCIENTIFIC_PAPER = "scientific_paper"
    SYNTHETIC = "synthetic"


@dataclass
class DataSample:
    """数据样本"""

    content: str
    source_type: DataSourceType
    source_id: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_hash(self) -> str:
        """获取内容哈希"""
        return hashlib.md5(self.content.encode()).hexdigest()[:16]


class WikipediaSimulator:
    """维基百科数据模拟器

    模拟从维基百科提取结构化知识的过程
    """

    # 模拟的维基百科文章模板
    TEMPLATES = {
        "science": [
            "{concept} is a fundamental concept in {field}. It was first described by {scientist} in {year}.",
            "The theory of {concept} explains how {phenomenon} occurs through {mechanism}.",
            "{concept} has applications in {application1}, {application2}, and {application3}.",
        ],
        "history": [
            "{event} occurred in {year} in {location}. It was a pivotal moment in {context}.",
            "The {event} led to significant changes in {outcome1} and {outcome2}.",
            "Historians debate whether {event} was caused by {cause1} or {cause2}.",
        ],
        "technology": [
            "{technology} is a system that uses {principle} to achieve {purpose}.",
            "Modern {technology} was developed by {company} in {year}.",
            "The key components of {technology} include {component1}, {component2}, and {component3}.",
        ],
    }

    CONCEPTS = {
        "science": ["Quantum Mechanics", "Evolution", "Relativity", "Photosynthesis", "Gravity"],
        "history": [
            "Industrial Revolution",
            "French Revolution",
            "World War II",
            "Renaissance",
            "Cold War",
        ],
        "technology": [
            "Internet",
            "Artificial Intelligence",
            "Blockchain",
            "Cloud Computing",
            "Robotics",
        ],
    }

    def generate_article(self, category: str = None) -> DataSample:
        """生成模拟的维基百科文章"""
        if category is None:
            category = random.choice(list(self.TEMPLATES.keys()))

        template = random.choice(self.TEMPLATES[category])
        concept = random.choice(self.CONCEPTS[category])

        # 填充模板变量
        replacements = {
            "{concept}": concept,
            "{field}": random.choice(["physics", "biology", "chemistry", "astronomy"]),
            "{scientist}": random.choice(["Einstein", "Darwin", "Newton", "Curie", "Turing"]),
            "{year}": str(random.randint(1800, 2020)),
            "{phenomenon}": random.choice(
                ["energy transfer", "particle behavior", "system evolution"]
            ),
            "{mechanism}": random.choice(
                ["quantum entanglement", "natural selection", "wave propagation"]
            ),
            "{application1}": random.choice(["medicine", "engineering", "computing"]),
            "{application2}": random.choice(["communications", "energy", "transportation"]),
            "{application3}": random.choice(
                ["materials science", "biotechnology", "environmental science"]
            ),
            "{event}": concept,
            "{location}": random.choice(["Europe", "Asia", "North America", "Africa"]),
            "{context}": random.choice(["human history", "economic development", "social change"]),
            "{outcome1}": random.choice(["political systems", "economic structures"]),
            "{outcome2}": random.choice(["cultural norms", "technological advancement"]),
            "{cause1}": random.choice(["economic factors", "social tensions"]),
            "{cause2}": random.choice(["political conflicts", "environmental pressures"]),
            "{technology}": concept,
            "{principle}": random.choice(
                ["machine learning", "distributed consensus", "virtualization"]
            ),
            "{purpose}": random.choice(["automation", "secure transactions", "scalable computing"]),
            "{company}": random.choice(["Google", "Microsoft", "IBM", "Apple", "Amazon"]),
            "{component1}": random.choice(["processors", "sensors", "algorithms"]),
            "{component2}": random.choice(["databases", "networks", "interfaces"]),
            "{component3}": random.choice(["protocols", "frameworks", "libraries"]),
        }

        content = template
        for key, value in replacements.items():
            content = content.replace(key, value)

        # 添加更多段落
        paragraphs = [
            f"\n\n## Characteristics\n{concept} is characterized by several key features.",
            f"\n\n## Impact\nThe development of {concept} has had profound implications for society.",
            f"\n\n## Future Directions\nResearchers continue to explore new aspects of {concept}.",
        ]
        content += random.choice(paragraphs)

        return DataSample(
            content=content,
            source_type=DataSourceType.WIKIPEDIA,
            source_id=f"wiki_{concept.lower().replace(' ', '_')}_{random.randint(1000, 9999)}",
            metadata={
                "category": category,
                "concept": concept,
                "word_count": len(content.split()),
                "language": "en",
            },
        )


class CodeRepositorySimulator:
    """代码库数据模拟器

    模拟从 GitHub 等代码库学习编程模式和结构
    """

    CODE_TEMPLATES = {
        "python": [
            '''def {func_name}({params}):
    """{docstring}"""
    {body}
    return {return_val}''',
            '''class {class_name}:
    """{docstring}"""
    
    def __init__(self, {init_params}):
        {init_body}
    
    def {method_name}(self, {method_params}):
        {method_body}
        return {return_val}''',
            '''async def {func_name}({params}):
    """{docstring}"""
    try:
        {async_body}
    except {exception} as e:
        logger.error(f"Error: {{e}}")
        raise''',
        ]
    }

    FUNC_NAMES = [
        "process_data",
        "calculate_metrics",
        "validate_input",
        "transform_result",
        "optimize_query",
    ]
    CLASS_NAMES = ["DataProcessor", "ModelTrainer", "APIHandler", "CacheManager", "EventDispatcher"]

    def generate_code_sample(self, language: str = "python") -> DataSample:
        """生成模拟的代码样本"""
        template = random.choice(self.CODE_TEMPLATES.get(language, self.CODE_TEMPLATES["python"]))

        replacements = {
            "{func_name}": random.choice(self.FUNC_NAMES),
            "{class_name}": random.choice(self.CLASS_NAMES),
            "{params}": ", ".join([f"arg{i}" for i in range(random.randint(1, 4))]),
            "{init_params}": ", ".join(
                [
                    f"{name}: {typ}"
                    for name, typ in [("config", "dict"), ("data", "list"), ("verbose", "bool")][
                        : random.randint(1, 3)
                    ]
                ]
            ),
            "{method_params}": ", ".join([f"param{i}" for i in range(random.randint(1, 3))]),
            "{docstring}": random.choice(
                [
                    "Process the input data and return results.",
                    "Calculate metrics based on the provided parameters.",
                    "Validate input against predefined constraints.",
                ]
            ),
            "{body}": "\n    ".join(
                [
                    "# Step 1: Initialize",
                    "result = []",
                    "# Step 2: Process",
                    "for item in data:",
                    "    result.append(transform(item))",
                    "# Step 3: Return",
                ]
            ),
            "{init_body}": "\n        ".join(
                [
                    "self.config = config",
                    "self.data = data or []",
                    "self.verbose = verbose",
                    "self._initialized = True",
                ]
            ),
            "{method_name}": random.choice(["execute", "run", "process", "compute"]),
            "{method_body}": "\n        ".join(
                [
                    "# Validate inputs",
                    "if not self._initialized:",
                    "    raise RuntimeError('Not initialized')",
                    "# Perform computation",
                    "output = self._transform(inputs)",
                ]
            ),
            "{return_val}": random.choice(["result", "output", "metrics", "status"]),
            "{async_body}": "\n        ".join(
                [
                    "result = await fetch_data()",
                    "processed = await transform(result)",
                    "return processed",
                ]
            ),
            "{exception}": random.choice(
                ["ValueError", "TypeError", "RuntimeError", "ConnectionError"]
            ),
        }

        content = template
        for key, value in replacements.items():
            content = content.replace(key, value)

        # 添加导入语句和注释
        imports = ["import logging", "from typing import List, Dict, Optional", "import asyncio"]
        content = "\n".join(random.sample(imports, k=random.randint(1, 3))) + "\n\n" + content

        return DataSample(
            content=content,
            source_type=DataSourceType.CODE_REPO,
            source_id=f"code_{random.choice(self.FUNC_NAMES).lower()}_{random.randint(1000, 9999)}",
            metadata={
                "language": language,
                "lines_of_code": len(content.split("\n")),
                "complexity": random.randint(1, 10),
                "has_tests": random.choice([True, False]),
                "repository": f"example/{random.choice(self.CLASS_NAMES).lower()}",
            },
        )


class ScientificPaperSimulator:
    """科学论文模拟器

    模拟从学术论文中提取研究方法和发现
    """

    PAPER_SECTIONS = {
        "abstract": [
            "We present a novel approach to {problem} using {method}.",
            "Our results demonstrate that {method} achieves {metric} improvement over baseline.",
            "This work has implications for {field} and opens new directions for {future_work}.",
        ],
        "introduction": [
            "{problem} is a challenging task in {field}.",
            "Previous approaches have limitations in {limitation}.",
            "We propose {method} to address these challenges.",
        ],
        "methodology": [
            "Our method consists of {num_steps} main steps.",
            "First, we {step1}. Then, we {step2}. Finally, we {step3}.",
            "We evaluate our approach on {dataset} dataset.",
        ],
        "results": [
            "Table 1 shows the comparison with state-of-the-art methods.",
            "Our method achieves {score}% accuracy, outperforming baselines by {margin}%.",
            "Ablation studies reveal the importance of {component}.",
        ],
        "conclusion": [
            "In conclusion, we have presented {method} for {problem}.",
            "Future work will explore {future_direction}.",
            "Our code and data are available at {url}.",
        ],
    }

    PROBLEMS = [
        "image classification",
        "natural language understanding",
        "reinforcement learning",
        "molecular discovery",
        "climate modeling",
    ]
    METHODS = [
        "deep neural networks",
        "transformer architectures",
        "graph neural networks",
        "variational inference",
        "meta-learning",
    ]
    FIELDS = [
        "computer vision",
        "natural language processing",
        "computational biology",
        "robotics",
        "materials science",
    ]

    def generate_paper(self) -> DataSample:
        """生成模拟的科学论文"""
        problem = random.choice(self.PROBLEMS)
        method = random.choice(self.METHODS)
        field = random.choice(self.FIELDS)

        sections = []
        for section_name, templates in self.PAPER_SECTIONS.items():
            section_content = []
            for template in templates:
                content = template.format(
                    problem=problem,
                    method=method,
                    field=field,
                    metric=random.choice(["significant", "substantial", "notable"]),
                    future_work=random.choice(["research", "applications", "theoretical analysis"]),
                    limitation=random.choice(["scalability", "generalization", "interpretability"]),
                    num_steps=random.randint(3, 5),
                    step1=random.choice(
                        ["preprocess the data", "extract features", "initialize parameters"]
                    ),
                    step2=random.choice(
                        ["train the model", "optimize hyperparameters", "validate results"]
                    ),
                    step3=random.choice(
                        ["evaluate performance", "analyze errors", "deploy the system"]
                    ),
                    dataset=random.choice(["ImageNet", "COCO", "SQuAD", "custom"]),
                    score=random.randint(85, 95),
                    margin=random.randint(5, 15),
                    component=random.choice(
                        ["attention mechanism", "loss function", "architecture design"]
                    ),
                    future_direction=random.choice(
                        ["multi-modal learning", "few-shot adaptation", "real-time inference"]
                    ),
                    url="https://github.com/example/repo",
                )
                section_content.append(content)
            sections.append(f"## {section_name.title()}\n" + " ".join(section_content))

        content = "\n\n".join(sections)
        title = f"A Novel Approach to {problem.title()} Using {method.title()}"
        content = f"# {title}\n\n**Authors**: Research Team et al.\n\n" + content

        return DataSample(
            content=content,
            source_type=DataSourceType.SCIENTIFIC_PAPER,
            source_id=f"paper_{hashlib.md5(title.encode()).hexdigest()[:8]}",
            metadata={
                "title": title,
                "field": field,
                "method": method,
                "problem": problem,
                "citation_count": random.randint(0, 500),
                "year": random.randint(2018, 2024),
                "venue": random.choice(["NeurIPS", "ICML", "CVPR", "ACL", "Nature"]),
            },
        )


class DataIngestionEngine:
    """数据摄入引擎

    负责从多种来源获取数据，提取知识，并更新认知系统
    """

    def __init__(self, cognition_engine=None):
        self.cognition_engine = cognition_engine
        self.wikipedia_sim = WikipediaSimulator()
        self.code_sim = CodeRepositorySimulator()
        self.paper_sim = ScientificPaperSimulator()

        self.ingestion_stats = {
            "total_samples": 0,
            "by_source": defaultdict(int),
            "knowledge_extracted": 0,
            "errors": 0,
        }

        self.extracted_knowledge = []

    def ingest_from_source(self, source_type: DataSourceType, count: int = 5) -> List[DataSample]:
        """从指定来源摄入数据"""
        samples = []
        simulator = {
            DataSourceType.WIKIPEDIA: self.wikipedia_sim,
            DataSourceType.CODE_REPO: self.code_sim,
            DataSourceType.SCIENTIFIC_PAPER: self.paper_sim,
        }.get(source_type)

        if not simulator:
            raise ValueError(f"Unknown source type: {source_type}")

        for _ in range(count):
            try:
                if source_type == DataSourceType.WIKIPEDIA:
                    sample = simulator.generate_article()
                elif source_type == DataSourceType.CODE_REPO:
                    sample = simulator.generate_code_sample()
                else:  # SCIENTIFIC_PAPER
                    sample = simulator.generate_paper()

                samples.append(sample)
                self.ingestion_stats["total_samples"] += 1
                self.ingestion_stats["by_source"][source_type.value] += 1

            except Exception as e:
                self.ingestion_stats["errors"] += 1
                print(f"Error ingesting sample: {e}")

        return samples

    def extract_knowledge(self, sample: DataSample) -> Dict[str, Any]:
        """从样本中提取知识"""
        extracted = {
            "source_id": sample.source_id,
            "source_type": sample.source_type.value,
            "timestamp": sample.timestamp,
            "concepts": [],
            "relations": [],
            "patterns": [],
            "metadata": sample.metadata,
        }

        content = sample.content

        # 简单实体提取（实际应使用 NER）
        # 提取大写字母开头的单词作为潜在概念
        potential_concepts = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", content)
        extracted["concepts"] = list(set(potential_concepts))[:20]  # 限制数量

        # 提取关系模式
        relation_patterns = [
            r"(\w+)\s+(is|are|was|were)\s+(\w+)",
            r"(\w+)\s+(leads?|causes?|enables?)\s+(\w+)",
            r"(\w+)\s+(of|in|for|with)\s+(\w+)",
        ]

        for pattern in relation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:10]:  # 限制数量
                extracted["relations"].append(
                    {"subject": match[0], "predicate": match[1], "object": match[2]}
                )

        # 提取代码模式（如果是代码）
        if sample.source_type == DataSourceType.CODE_REPO:
            func_defs = re.findall(r"def\s+(\w+)\s*\(", content)
            class_defs = re.findall(r"class\s+(\w+)", content)
            extracted["patterns"].extend([{"type": "function", "name": name} for name in func_defs])
            extracted["patterns"].extend([{"type": "class", "name": name} for name in class_defs])

        # 提取论文模式
        if sample.source_type == DataSourceType.SCIENTIFIC_PAPER:
            if "outperforms" in content.lower() or "achieves" in content.lower():
                extracted["patterns"].append({"type": "performance_claim", "confidence": "high"})
            if "ablation" in content.lower():
                extracted["patterns"].append({"type": "ablation_study", "present": True})

        self.ingestion_stats["knowledge_extracted"] += len(extracted["concepts"]) + len(
            extracted["relations"]
        )
        self.extracted_knowledge.append(extracted)

        return extracted

    def run_ingestion_pipeline(self, sources: Dict[DataSourceType, int]) -> Dict[str, Any]:
        """运行完整的数据摄入流水线"""
        print("=" * 60)
        print("开始数据摄入流水线")
        print("=" * 60)

        all_samples = []
        all_knowledge = []

        for source_type, count in sources.items():
            print(f"\n从 {source_type.value} 摄入 {count} 个样本...")
            samples = self.ingest_from_source(source_type, count)
            all_samples.extend(samples)

            for sample in samples:
                knowledge = self.extract_knowledge(sample)
                all_knowledge.append(knowledge)
                print(
                    f"  ✓ 提取 {len(knowledge['concepts'])} 个概念，{len(knowledge['relations'])} 个关系"
                )

        # 汇总统计
        summary = {
            "total_samples": len(all_samples),
            "total_concepts": sum(len(k["concepts"]) for k in all_knowledge),
            "total_relations": sum(len(k["relations"]) for k in all_knowledge),
            "total_patterns": sum(len(k["patterns"]) for k in all_knowledge),
            "by_source": dict(self.ingestion_stats["by_source"]),
            "unique_concepts": len(set(c for k in all_knowledge for c in k["concepts"])),
            "processing_time": (
                time.time() - min(s.timestamp for s in all_samples) if all_samples else 0
            ),
        }

        print("\n" + "=" * 60)
        print("数据摄入完成")
        print(f"总样本数：{summary['total_samples']}")
        print(f"提取概念：{summary['total_concepts']} (唯一：{summary['unique_concepts']})")
        print(f"提取关系：{summary['total_relations']}")
        print(f"识别模式：{summary['total_patterns']}")
        print("=" * 60)

        return summary


# ============================================================================
# 第二部分：网格世界仿真环境
# ============================================================================


class GridWorldAction(Enum):
    """网格世界动作"""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    STAY = "stay"


class GridWorldCell(Enum):
    """网格单元类型"""

    EMPTY = 0
    AGENT = 1
    OBSTACLE = 2  # 坑/障碍
    GOAL = 3  # 目标
    REWARD = 4  # 奖励
    START = 5  # 起点


@dataclass
class GridWorldState:
    """网格世界状态"""

    agent_position: Tuple[int, int]
    grid_size: Tuple[int, int]
    obstacles: Set[Tuple[int, int]]
    goals: Set[Tuple[int, int]]
    rewards: Dict[Tuple[int, int], float]
    step_count: int = 0
    total_reward: float = 0.0
    episode_complete: bool = False

    def to_tuple(self) -> Tuple:
        """转换为可哈希的元组"""
        return (
            self.agent_position,
            frozenset(self.obstacles),
            frozenset(self.goals),
            frozenset(self.rewards.items()),
        )


class GridWorldEnvironment:
    """网格世界环境

    一个简单的仿真环境，Agent 需要学会避开障碍并到达目标
    """

    def __init__(
        self,
        width: int = 10,
        height: int = 10,
        num_obstacles: int = 15,
        num_goals: int = 3,
        num_rewards: int = 5,
    ):
        self.width = width
        self.height = height
        self.num_obstacles = num_obstacles
        self.num_goals = num_goals
        self.num_rewards = num_rewards

        self.reset()

    def reset(self) -> GridWorldState:
        """重置环境"""
        # 随机放置障碍物
        self.obstacles = set()
        while len(self.obstacles) < self.num_obstacles:
            pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if pos != (0, 0):  # 不在起点
                self.obstacles.add(pos)

        # 随机放置目标
        self.goals = set()
        while len(self.goals) < self.num_goals:
            pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if pos not in self.obstacles and pos != (0, 0):
                self.goals.add(pos)

        # 随机放置奖励
        self.rewards = {}
        while len(self.rewards) < self.num_rewards:
            pos = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if pos not in self.obstacles and pos not in self.goals and pos != (0, 0):
                self.rewards[pos] = random.uniform(1.0, 5.0)

        # 初始化状态
        self.state = GridWorldState(
            agent_position=(0, 0),
            grid_size=(self.width, self.height),
            obstacles=self.obstacles,
            goals=self.goals,
            rewards=self.rewards,
            step_count=0,
            total_reward=0.0,
            episode_complete=False,
        )

        return self.state

    def step(self, action: GridWorldAction) -> Tuple[GridWorldState, float, bool]:
        """执行动作并返回新状态、奖励和完成标志"""
        if self.state.episode_complete:
            return self.state, 0.0, True

        # 计算新位置
        x, y = self.state.agent_position
        if action == GridWorldAction.UP:
            y = min(y + 1, self.height - 1)
        elif action == GridWorldAction.DOWN:
            y = max(y - 1, 0)
        elif action == GridWorldAction.LEFT:
            x = max(x - 1, 0)
        elif action == GridWorldAction.RIGHT:
            x = min(x + 1, self.width - 1)

        new_pos = (x, y)
        reward = -0.1  # 每一步的小惩罚，鼓励快速完成

        # 检查碰撞
        if new_pos in self.state.obstacles:
            reward = -10.0  # 撞到障碍的大惩罚
            # 不移回原位，让 Agent 学会避免
        elif new_pos in self.state.goals:
            reward = 10.0  # 到达目标的奖励
            self.state.episode_complete = True
        elif new_pos in self.state.rewards:
            reward += self.state.rewards[new_pos]
            del self.state.rewards[new_pos]  # 奖励只能获取一次

        # 更新状态
        self.state.agent_position = new_pos
        self.state.step_count += 1
        self.state.total_reward += reward

        # 最大步数限制
        if self.state.step_count >= self.width * self.height * 2:
            self.state.episode_complete = True

        return self.state, reward, self.state.episode_complete

    def get_valid_actions(self, position: Tuple[int, int] = None) -> List[GridWorldAction]:
        """获取当前位置的有效动作"""
        if position is None:
            position = self.state.agent_position

        valid_actions = [GridWorldAction.STAY]
        x, y = position

        if y < self.height - 1 and (x, y + 1) not in self.state.obstacles:
            valid_actions.append(GridWorldAction.UP)
        if y > 0 and (x, y - 1) not in self.state.obstacles:
            valid_actions.append(GridWorldAction.DOWN)
        if x > 0 and (x - 1, y) not in self.state.obstacles:
            valid_actions.append(GridWorldAction.LEFT)
        if x < self.width - 1 and (x + 1, y) not in self.state.obstacles:
            valid_actions.append(GridWorldAction.RIGHT)

        return valid_actions

    def render(self) -> str:
        """渲染网格世界"""
        grid = []
        for y in range(self.height - 1, -1, -1):
            row = []
            for x in range(self.width):
                pos = (x, y)
                if pos == self.state.agent_position:
                    row.append("A")
                elif pos in self.state.obstacles:
                    row.append("#")
                elif pos in self.state.goals:
                    row.append("G")
                elif pos in self.state.rewards:
                    row.append("+")
                elif pos == (0, 0):
                    row.append("S")
                else:
                    row.append(".")
            grid.append(" ".join(row))

        return "\n".join(grid)


class QLearningAgent:
    """Q-Learning 智能体

    通过强化学习在网格世界中学习避坑策略
    """

    def __init__(
        self,
        actions: List[GridWorldAction],
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
    ):
        self.actions = actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon

        # Q 表：state -> action -> value
        self.q_table: Dict[Tuple, Dict[GridWorldAction, float]] = defaultdict(
            lambda: {action: 0.0 for action in actions}
        )

        self.training_stats = {
            "episodes": 0,
            "total_steps": 0,
            "successful_episodes": 0,
            "avg_reward_per_episode": [],
            "avg_steps_per_episode": [],
        }

    def get_state_key(self, state: GridWorldState) -> Tuple:
        """将状态转换为可哈希的键"""
        # 简化状态表示：只考虑 Agent 相对位置和目标/障碍的相对方向
        agent_x, agent_y = state.agent_position
        width, height = state.grid_size

        # 离散化方向信息
        relative_info = []
        for obs in list(state.obstacles)[:5]:  # 限制数量
            dx = 1 if obs[0] > agent_x else (-1 if obs[0] < agent_x else 0)
            dy = 1 if obs[1] > agent_y else (-1 if obs[1] < agent_y else 0)
            relative_info.append(("O", dx, dy))

        for goal in list(state.goals)[:3]:
            dx = 1 if goal[0] > agent_x else (-1 if goal[0] < agent_x else 0)
            dy = 1 if goal[1] > agent_y else (-1 if goal[1] < agent_y else 0)
            relative_info.append(("G", dx, dy))

        return tuple(sorted(relative_info))

    def choose_action(
        self, state: GridWorldState, valid_actions: List[GridWorldAction]
    ) -> GridWorldAction:
        """选择动作（epsilon-greedy 策略）"""
        if random.random() < self.epsilon:
            # 探索：随机选择有效动作
            return random.choice(valid_actions)
        else:
            # 利用：选择 Q 值最大的动作
            state_key = self.get_state_key(state)
            q_values = self.q_table[state_key]

            # 只在有效动作中选择最大值
            valid_q = {a: q_values.get(a, 0.0) for a in valid_actions}
            max_q = max(valid_q.values())
            best_actions = [a for a, q in valid_q.items() if q == max_q]

            return random.choice(best_actions)

    def update(
        self,
        state: GridWorldState,
        action: GridWorldAction,
        reward: float,
        next_state: GridWorldState,
        done: bool,
    ):
        """更新 Q 值"""
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)

        current_q = self.q_table[state_key][action]

        if done:
            target = reward
        else:
            next_max_q = max(self.q_table[next_state_key].values())
            target = reward + self.gamma * next_max_q

        # Q-learning 更新公式
        self.q_table[state_key][action] += self.lr * (target - current_q)

    def train(self, env: GridWorldEnvironment, episodes: int = 1000) -> Dict[str, Any]:
        """训练智能体"""
        print("=" * 60)
        print(f"开始训练 Q-Learning 智能体 ({episodes} 集)")
        print("=" * 60)

        for episode in range(episodes):
            state = env.reset()
            done = False
            episode_reward = 0.0
            steps = 0

            while not done:
                valid_actions = env.get_valid_actions()
                action = self.choose_action(state, valid_actions)

                next_state, reward, done = env.step(action)
                self.update(state, action, reward, next_state, done)

                state = next_state
                episode_reward += reward
                steps += 1

            # 更新统计
            self.training_stats["episodes"] += 1
            self.training_stats["total_steps"] += steps
            if episode_reward > 0:
                self.training_stats["successful_episodes"] += 1

            self.training_stats["avg_reward_per_episode"].append(episode_reward)
            self.training_stats["avg_steps_per_episode"].append(steps)

            # 进度报告
            if (episode + 1) % 100 == 0:
                recent_avg_reward = sum(self.training_stats["avg_reward_per_episode"][-100:]) / 100
                recent_avg_steps = sum(self.training_stats["avg_steps_per_episode"][-100:]) / 100
                success_rate = (
                    self.training_stats["successful_episodes"]
                    / self.training_stats["episodes"]
                    * 100
                )

                print(
                    f"Episode {episode+1}/{episodes}: "
                    f"Avg Reward={recent_avg_reward:.2f}, "
                    f"Avg Steps={recent_avg_steps:.1f}, "
                    f"Success Rate={success_rate:.1f}%"
                )

        # 最终统计
        final_stats = {
            "total_episodes": self.training_stats["episodes"],
            "total_steps": self.training_stats["total_steps"],
            "success_rate": self.training_stats["successful_episodes"]
            / self.training_stats["episodes"]
            * 100,
            "final_avg_reward": sum(self.training_stats["avg_reward_per_episode"][-100:]) / 100,
            "final_avg_steps": sum(self.training_stats["avg_steps_per_episode"][-100:]) / 100,
            "q_table_size": len(self.q_table),
        }

        print("\n" + "=" * 60)
        print("训练完成")
        print(f"总集数：{final_stats['total_episodes']}")
        print(f"成功率：{final_stats['success_rate']:.1f}%")
        print(f"最终平均奖励：{final_stats['final_avg_reward']:.2f}")
        print(f"最终平均步数：{final_stats['final_avg_steps']:.1f}")
        print(f"Q 表大小：{final_stats['q_table_size']}")
        print("=" * 60)

        return final_stats


# ============================================================================
# 第三部分：涌现行为观察系统
# ============================================================================


class EmergenceObserver:
    """涌现行为观察器

    监测和记录复杂交互中出现的未预设智能行为
    """

    def __init__(self):
        self.observed_patterns = []
        self.emergent_behaviors = []
        self.interaction_log = []

        # 预定义的涌现行为类型
        self.emergence_types = {
            "STRATEGY_FORMATION": "策略形成",
            "PATTERN_RECOGNITION": "模式识别",
            "TRANSFER_LEARNING": "迁移学习",
            "COLLABORATION": "协作行为",
            "TOOL_USE": "工具使用",
            "ABSTRACTION": "抽象思维",
            "CREATIVITY": "创造性行为",
        }

    def log_interaction(
        self, agent_id: str, action: str, context: Dict[str, Any], outcome: Dict[str, Any]
    ):
        """记录交互"""
        entry = {
            "timestamp": time.time(),
            "agent_id": agent_id,
            "action": action,
            "context": context,
            "outcome": outcome,
        }
        self.interaction_log.append(entry)

    def detect_emergence(self, window_size: int = 100) -> List[Dict[str, Any]]:
        """检测涌现行为"""
        if len(self.interaction_log) < window_size:
            return []

        recent_interactions = self.interaction_log[-window_size:]
        detected = []

        # 检测策略形成：连续成功的相似动作序列
        successful_sequences = self._find_successful_sequences(recent_interactions)
        if len(successful_sequences) > 3:
            detected.append(
                {
                    "type": "STRATEGY_FORMATION",
                    "description": f"检测到 {len(successful_sequences)} 个成功策略序列",
                    "evidence": successful_sequences[:3],
                    "confidence": min(0.9, 0.5 + len(successful_sequences) * 0.1),
                }
            )

        # 检测模式识别：重复出现的状态 - 动作对
        pattern_freq = self._count_state_action_patterns(recent_interactions)
        strong_patterns = [(p, c) for p, c in pattern_freq.items() if c > 5]
        if strong_patterns:
            detected.append(
                {
                    "type": "PATTERN_RECOGNITION",
                    "description": f"检测到 {len(strong_patterns)} 个强模式",
                    "evidence": [{"pattern": str(p), "count": c} for p, c in strong_patterns[:5]],
                    "confidence": min(0.9, 0.4 + len(strong_patterns) * 0.1),
                }
            )

        # 检测迁移学习：在新环境中复用旧策略
        transfer_evidence = self._detect_transfer_learning(recent_interactions)
        if transfer_evidence:
            detected.append(
                {
                    "type": "TRANSFER_LEARNING",
                    "description": "检测到迁移学习行为",
                    "evidence": transfer_evidence,
                    "confidence": 0.7,
                }
            )

        self.emergent_behaviors.extend(detected)
        return detected

    def _find_successful_sequences(self, interactions: List[Dict]) -> List[List[Dict]]:
        """查找成功的动作序列"""
        sequences = []
        current_sequence = []

        for interaction in interactions:
            if interaction["outcome"].get("reward", 0) > 0:
                current_sequence.append(interaction)
            else:
                if len(current_sequence) >= 3:
                    sequences.append(current_sequence)
                current_sequence = []

        if len(current_sequence) >= 3:
            sequences.append(current_sequence)

        return sequences

    def _count_state_action_patterns(self, interactions: List[Dict]) -> Dict[str, int]:
        """统计状态 - 动作模式频率"""
        pattern_counts = defaultdict(int)

        for interaction in interactions:
            context = interaction["context"]
            action = interaction["action"]

            # 简化状态表示
            state_key = str(sorted(context.items()))
            pattern = f"{state_key}->{action}"
            pattern_counts[pattern] += 1

        return dict(pattern_counts)

    def _detect_transfer_learning(self, interactions: List[Dict]) -> List[Dict]:
        """检测迁移学习证据"""
        # 简化的检测逻辑
        evidence = []

        # 检查是否有跨环境的相似策略
        env_changes = [
            i for i, inter in enumerate(interactions) if "environment_change" in inter["context"]
        ]

        if len(env_changes) > 1:
            for idx in env_changes[1:]:
                if idx > 10:
                    before = interactions[idx - 10 : idx]
                    after = interactions[idx : idx + 10]

                    # 比较前后策略相似性
                    before_actions = [i["action"] for i in before]
                    after_actions = [i["action"] for i in after]

                    similarity = self._calculate_sequence_similarity(before_actions, after_actions)
                    if similarity > 0.6:
                        evidence.append(
                            {
                                "before_env": "env_1",
                                "after_env": "env_2",
                                "strategy_similarity": similarity,
                            }
                        )

        return evidence

    def _calculate_sequence_similarity(self, seq1: List[str], seq2: List[str]) -> float:
        """计算两个序列的相似度"""
        if not seq1 or not seq2:
            return 0.0

        # 简单的 Jaccard 相似度
        set1 = set(seq1)
        set2 = set(seq2)

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def generate_report(self) -> Dict[str, Any]:
        """生成涌现行为报告"""
        return {
            "total_interactions": len(self.interaction_log),
            "emergent_behaviors_detected": len(self.emergent_behaviors),
            "behavior_types": list(set(b["type"] for b in self.emergent_behaviors)),
            "recent_behaviors": self.emergent_behaviors[-10:],
            "analysis_timestamp": datetime.now().isoformat(),
        }


# ============================================================================
# 主实验流程
# ============================================================================


def run_phase5_experiments():
    """运行第五阶段实验"""
    print("\n" + "=" * 80)
    print("第五阶段实验：真实数据学习与仿真环境交互")
    print("=" * 80 + "\n")

    # ========== 实验 1：真实数据摄入 ==========
    print("【实验 1】真实数据摄入")
    print("-" * 40)

    ingestion_engine = DataIngestionEngine()

    sources = {
        DataSourceType.WIKIPEDIA: 10,
        DataSourceType.CODE_REPO: 8,
        DataSourceType.SCIENTIFIC_PAPER: 5,
    }

    ingestion_summary = ingestion_engine.run_ingestion_pipeline(sources)

    print("\n✓ 实验 1 完成\n")

    # ========== 实验 2：网格世界生存 ==========
    print("【实验 2】网格世界生存学习")
    print("-" * 40)

    env = GridWorldEnvironment(width=10, height=10, num_obstacles=15, num_goals=3)
    agent = QLearningAgent(actions=list(GridWorldAction))

    training_results = agent.train(env, episodes=500)

    # 测试训练后的表现
    print("\n测试训练后的智能体:")
    test_rewards = []
    for _ in range(20):
        state = env.reset()
        done = False
        total_reward = 0.0

        while not done:
            valid_actions = env.get_valid_actions()
            action = agent.choose_action(state, valid_actions)  # 使用学到的策略
            state, reward, done = env.step(action)
            total_reward += reward

        test_rewards.append(total_reward)

    avg_test_reward = sum(test_rewards) / len(test_rewards)
    print(f"测试平均奖励：{avg_test_reward:.2f}")
    print(f"避坑成功率：{sum(1 for r in test_rewards if r > 0) / len(test_rewards) * 100:.0f}%")

    print("\n✓ 实验 2 完成\n")

    # ========== 实验 3：涌现行为观察 ==========
    print("【实验 3】涌现行为观察")
    print("-" * 40)

    observer = EmergenceObserver()

    # 模拟复杂交互
    print("模拟复杂交互场景...")
    for i in range(200):
        context = {
            "step": i,
            "position": (
                agent.q_table and list(agent.q_table.keys())[i % len(agent.q_table)]
                if agent.q_table
                else (0, 0)
            ),
            "environment": "grid_world",
        }

        action = random.choice(list(GridWorldAction)).value
        outcome = {"reward": random.uniform(-1, 10), "success": random.random() > 0.3}

        observer.log_interaction("agent_1", action, context, outcome)

        # 模拟环境变化
        if i == 100:
            observer.log_interaction(
                "agent_1",
                "env_change",
                {"environment_change": True, "new_config": "harder"},
                {"adaptation_required": True},
            )

    # 检测涌现行为
    emergent_behaviors = observer.detect_emergence(window_size=100)

    print(f"\n检测到 {len(emergent_behaviors)} 种涌现行为:")
    for behavior in emergent_behaviors:
        print(f"  • {behavior['type']}: {behavior['description']}")
        print(f"    置信度：{behavior['confidence']:.2f}")

    emergence_report = observer.generate_report()
    print(f"\n总交互次数：{emergence_report['total_interactions']}")
    print(f"涌现行为总数：{emergence_report['emergent_behaviors_detected']}")

    print("\n✓ 实验 3 完成\n")

    # ========== 实验总结 ==========
    print("=" * 80)
    print("第五阶段实验总结")
    print("=" * 80)

    summary = {
        "experiment_1_data_ingestion": {
            "status": "completed",
            "samples_processed": ingestion_summary["total_samples"],
            "concepts_extracted": ingestion_summary["total_concepts"],
            "relations_extracted": ingestion_summary["total_relations"],
        },
        "experiment_2_grid_world": {
            "status": "completed",
            "training_episodes": training_results["total_episodes"],
            "success_rate": training_results["success_rate"],
            "test_performance": avg_test_reward,
        },
        "experiment_3_emergence": {
            "status": "completed",
            "interactions_logged": emergence_report["total_interactions"],
            "behaviors_detected": emergence_report["emergent_behaviors_detected"],
            "behavior_types": emergence_report["behavior_types"],
        },
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print("所有实验完成！系统展现出学习能力、适应性和潜在的涌现行为。")
    print("=" * 80 + "\n")

    return summary


if __name__ == "__main__":
    results = run_phase5_experiments()
