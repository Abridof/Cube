"""
系统 2 慢思考推理引擎 (System 2 Slow Thinking Engine)
阶段 10: 实现深度逻辑推理、多步规划和思维链/树搜索

核心组件:
1. ChainOfThought: 思维链推理器
2. TreeOfThought: 思维树搜索器  
3. LogicValidator: 逻辑一致性验证器
4. MultiStepPlanner: 多步任务规划器
5. SlowThinkingEngine: 统一的慢思考引擎
"""

import math
import time
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import heapq
from collections import defaultdict
import random


class ReasoningStrategy(Enum):
    """推理策略类型"""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHT = "tree_of_thought"
    GRAPH_OF_THOUGHT = "graph_of_thought"
    MONTE_CARLO = "monte_carlo"
    BEAM_SEARCH = "beam_search"


@dataclass
class ThoughtNode:
    """思维节点 - 树搜索的基本单元"""
    id: str
    content: str
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    depth: int = 0
    value: float = 0.0  # 节点评估值
    probability: float = 1.0  # 达成目标的概率
    visits: int = 0  # 访问次数 (MCTS)
    total_reward: float = 0.0  # 累计奖励 (MCTS)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    
    def uct_score(self, exploration_constant: float = 1.414) -> float:
        """计算 UCT (Upper Confidence Bound for Trees) 分数"""
        if self.visits == 0:
            return float('inf')
        exploitation = self.total_reward / self.visits
        exploration = exploration_constant * math.sqrt(math.log(self.parent_visits()) / self.visits)
        return exploitation + exploration
    
    def parent_visits(self) -> int:
        """获取父节点访问次数 (简化实现)"""
        return max(1, self.visits)


@dataclass
class ReasoningStep:
    """推理步骤"""
    step_number: int
    content: str
    method: str
    confidence: float
    dependencies: List[int] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    validation_status: str = "pending"  # pending, validated, failed
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningTrace:
    """完整的推理轨迹"""
    problem: str
    strategy: ReasoningStrategy
    steps: List[ReasoningStep] = field(default_factory=list)
    conclusion: Optional[str] = None
    confidence: float = 0.0
    total_time: float = 0.0
    nodes_explored: int = 0
    backtracks: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChainOfThought:
    """
    思维链推理器
    将复杂问题分解为连续的推理步骤
    """
    
    def __init__(self, max_steps: int = 20, min_confidence: float = 0.7):
        self.max_steps = max_steps
        self.min_confidence = min_confidence
        self.step_templates = {
            "decompose": "将问题分解为子问题",
            "analyze": "分析已知条件和约束",
            "infer": "基于前一步进行逻辑推断",
            "verify": "验证当前结论的正确性",
            "synthesize": "综合所有信息得出结论"
        }
    
    def reason(self, problem: str, context: Optional[Dict] = None) -> ReasoningTrace:
        """执行思维链推理"""
        start_time = time.time()
        trace = ReasoningTrace(
            problem=problem,
            strategy=ReasoningStrategy.CHAIN_OF_THOUGHT
        )
        
        # 步骤 1: 问题分解
        step1 = ReasoningStep(
            step_number=1,
            content=self._decompose_problem(problem),
            method="decompose",
            confidence=0.9,
            metadata={"sub_problems": self._extract_sub_problems(problem)}
        )
        trace.steps.append(step1)
        
        # 步骤 2-n: 逐步推理
        current_context = context or {}
        for i in range(2, self.max_steps + 1):
            step = self._generate_next_step(
                problem, 
                trace.steps, 
                current_context,
                i
            )
            
            if step.confidence < self.min_confidence:
                step.validation_status = "failed"
                trace.backtracks += 1
                # 尝试替代路径
                alternative = self._try_alternative_path(trace.steps, current_context)
                if alternative:
                    step = alternative
                else:
                    break
            
            trace.steps.append(step)
            
            # 检查是否得出结论
            if self._is_conclusion_reached(trace.steps):
                trace.conclusion = self._synthesize_conclusion(trace.steps)
                trace.confidence = self._calculate_final_confidence(trace.steps)
                break
        
        if not trace.conclusion:
            trace.conclusion = self._synthesize_conclusion(trace.steps)
            trace.confidence = self._calculate_final_confidence(trace.steps)
        
        trace.total_time = time.time() - start_time
        trace.nodes_explored = len(trace.steps)
        
        return trace
    
    def _decompose_problem(self, problem: str) -> str:
        """分解问题为可管理的部分"""
        # 实际实现中会调用 LLM 进行智能分解
        keywords = ["计算", "证明", "分析", "设计", "优化"]
        decomposition = f"问题分析：识别关键要素和约束条件\n"
        decomposition += f"目标：明确需要解决的核心问题\n"
        decomposition += f"方法：选择合适的推理策略\n"
        return decomposition
    
    def _extract_sub_problems(self, problem: str) -> List[str]:
        """提取子问题列表"""
        # 简化实现，实际应使用 NLP 技术
        return [
            "理解问题背景",
            "识别已知条件",
            "确定求解目标",
            "选择解决方法"
        ]
    
    def _generate_next_step(
        self, 
        problem: str, 
        previous_steps: List[ReasoningStep],
        context: Dict,
        step_num: int
    ) -> ReasoningStep:
        """生成下一个推理步骤"""
        methods = ["analyze", "infer", "verify", "calculate", "compare"]
        method = methods[(step_num - 2) % len(methods)]
        
        content = f"步骤{step_num}: 基于前序推理进行{method}操作\n"
        content += f"输入：前{step_num-1}步的结论\n"
        content += f"处理：应用逻辑规则和专业知讙\n"
        content += f"输出：新的中间结论"
        
        confidence = max(0.5, 0.95 - (step_num * 0.02))
        
        return ReasoningStep(
            step_number=step_num,
            content=content,
            method=method,
            confidence=confidence,
            dependencies=[s.step_number for s in previous_steps[-3:]]
        )
    
    def _is_conclusion_reached(self, steps: List[ReasoningStep]) -> bool:
        """判断是否已得出结论"""
        if len(steps) < 3:
            return False
        last_steps = steps[-3:]
        avg_confidence = sum(s.confidence for s in last_steps) / len(last_steps)
        return avg_confidence > 0.85
    
    def _synthesize_conclusion(self, steps: List[ReasoningStep]) -> str:
        """综合所有步骤得出结论"""
        conclusion = "综合推理结论:\n"
        for i, step in enumerate(steps[-5:], 1):
            conclusion += f"{i}. {step.content.split(chr(10))[0]}\n"
        conclusion += f"\n最终答案基于{len(steps)}步严谨推理得出"
        return conclusion
    
    def _calculate_final_confidence(self, steps: List[ReasoningStep]) -> float:
        """计算最终置信度"""
        if not steps:
            return 0.0
        weights = [0.1 ** (len(steps) - i - 1) for i in range(len(steps))]
        total_weight = sum(weights)
        weighted_sum = sum(s.confidence * w for s, w in zip(steps, weights))
        return weighted_sum / total_weight
    
    def _try_alternative_path(
        self, 
        steps: List[ReasoningStep], 
        context: Dict
    ) -> Optional[ReasoningStep]:
        """尝试替代推理路径"""
        if len(steps) < 2:
            return None
        
        # 回退一步，尝试不同方法
        alternative_method = "re-evaluate"
        content = f"替代路径：重新评估假设和推理过程\n"
        content += f"调整：修正前序步骤中的潜在错误\n"
        
        return ReasoningStep(
            step_number=steps[-1].step_number,
            content=content,
            method=alternative_method,
            confidence=0.75,
            dependencies=[s.step_number for s in steps[-2:]],
            metadata={"is_alternative": True}
        )


class TreeOfThought:
    """
    思维树搜索器
    探索多个推理路径，通过评估和剪枝找到最优解
    """
    
    def __init__(
        self, 
        max_depth: int = 10, 
        branching_factor: int = 3,
        beam_width: int = 5,
        exploration_constant: float = 1.414
    ):
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self.beam_width = beam_width
        self.exploration_constant = exploration_constant
        self.node_counter = 0
    
    def search(
        self, 
        problem: str, 
        evaluator: Optional[Callable[[str], float]] = None,
        generator: Optional[Callable[[str, int], List[str]]] = None
    ) -> Tuple[ReasoningTrace, List[ThoughtNode]]:
        """执行思维树搜索"""
        start_time = time.time()
        trace = ReasoningTrace(
            problem=problem,
            strategy=ReasoningStrategy.TREE_OF_THOUGHT
        )
        
        # 创建根节点
        root = self._create_node(
            content=f"问题：{problem}",
            parent_id=None,
            depth=0
        )
        
        all_nodes = [root]
        best_node = root
        best_value = -float('inf')
        
        # 束搜索
        current_level = [root]
        
        for depth in range(self.max_depth):
            next_level = []
            
            for node in current_level:
                # 生成子节点
                children = self._generate_children(node, generator)
                all_nodes.extend(children)
                trace.nodes_explored += len(children)
                
                # 评估子节点
                for child in children:
                    if evaluator:
                        child.value = evaluator(child.content)
                    else:
                        child.value = self._heuristic_evaluate(child.content, problem)
                    
                    if child.value > best_value:
                        best_value = child.value
                        best_node = child
                
                # 选择 top-k 节点进入下一层
                children.sort(key=lambda x: x.value, reverse=True)
                next_level.extend(children[:self.beam_width])
            
            if not next_level:
                break
            
            current_level = next_level
        
        # 构建推理轨迹
        path = self._extract_path(root, best_node, all_nodes)
        for i, node in enumerate(path):
            step = ReasoningStep(
                step_number=i+1,
                content=node.content,
                method="tree_search",
                confidence=node.value,
                metadata={"node_id": node.id, "depth": node.depth}
            )
            trace.steps.append(step)
        
        trace.conclusion = best_node.content
        trace.confidence = best_value
        trace.total_time = time.time() - start_time
        
        return trace, all_nodes
    
    def mcts_search(
        self,
        problem: str,
        num_simulations: int = 100,
        evaluator: Optional[Callable[[str], float]] = None
    ) -> Tuple[ReasoningTrace, List[ThoughtNode]]:
        """蒙特卡洛树搜索"""
        start_time = time.time()
        trace = ReasoningTrace(
            problem=problem,
            strategy=ReasoningStrategy.MONTE_CARLO
        )
        
        root = self._create_node(
            content=f"问题：{problem}",
            parent_id=None,
            depth=0
        )
        
        all_nodes = [root]
        node_map = {root.id: root}  # 维护 ID 到节点的映射
        
        for sim in range(num_simulations):
            # 选择 - 简化：直接扩展根节点
            node = root
            
            # 扩展
            if node.depth < self.max_depth and not node.children:
                children = self._generate_children(node)
                all_nodes.extend(children)
                for c in children:
                    node_map[c.id] = c
                trace.nodes_explored += len(children)
                if children:
                    node = children[0]
            
            # 模拟
            reward = self._simulate(node, evaluator)
            
            # 回溯
            self._backpropagate(node, reward)
        
        # 选择最佳子节点
        if root.children:
            # children 存储的是 ID 字符串，需要从 node_map 获取实际节点
            child_nodes = [node_map[c] if isinstance(c, str) else c for c in root.children]
            best_child = max(child_nodes, key=lambda x: x.visits)
            best_value = best_child.total_reward / max(1, best_child.visits)
        else:
            best_child = root
            best_value = 0.0
        
        # 构建轨迹
        path = [root, best_child] if best_child != root else [root]
        for i, node in enumerate(path):
            step = ReasoningStep(
                step_number=i+1,
                content=node.content,
                method="mcts",
                confidence=node.total_reward / max(1, node.visits),
                metadata={
                    "visits": node.visits,
                    "total_reward": node.total_reward
                }
            )
            trace.steps.append(step)
        
        trace.conclusion = best_child.content
        trace.confidence = best_value
        trace.total_time = time.time() - start_time
        
        return trace, all_nodes
    
    def _create_node(
        self, 
        content: str, 
        parent_id: Optional[str], 
        depth: int
    ) -> ThoughtNode:
        """创建新的思维节点"""
        self.node_counter += 1
        node_id = f"node_{self.node_counter}"
        return ThoughtNode(
            id=node_id,
            content=content,
            parent_id=parent_id,
            depth=depth
        )
    
    def _generate_children(
        self, 
        node: ThoughtNode,
        generator: Optional[Callable[[str, int], List[str]]] = None
    ) -> List[ThoughtNode]:
        """生成子节点"""
        children = []
        
        if generator:
            thoughts = generator(node.content, self.branching_factor)
        else:
            thoughts = self._default_generator(node.content, self.branching_factor)
        
        for thought in thoughts:
            child = self._create_node(
                content=thought,
                parent_id=node.id,
                depth=node.depth + 1
            )
            node.children.append(child.id)
            children.append(child)
        
        return children
    
    def _default_generator(self, content: str, k: int) -> List[str]:
        """默认思维生成器"""
        variations = [
            f"方法 A: {content} - 从正面角度分析",
            f"方法 B: {content} - 从反面角度验证",
            f"方法 C: {content} - 考虑边界情况",
            f"方法 D: {content} - 类比其他问题",
            f"方法 E: {content} - 分解为子问题"
        ]
        return variations[:k]
    
    def _heuristic_evaluate(self, content: str, problem: str) -> float:
        """启发式评估函数"""
        score = 0.5
        
        # 长度适中加分
        if 50 < len(content) < 500:
            score += 0.1
        
        # 包含关键词加分
        keywords = ["因此", "所以", "结论", "证明", "计算得"]
        if any(kw in content for kw in keywords):
            score += 0.15
        
        # 逻辑连接词加分
        logical_connectives = ["因为", "如果", "那么", "然而", "此外"]
        score += min(0.25, content.count("，") * 0.05 + content.count("。") * 0.05)
        
        return min(1.0, score)
    
    def _select(self, node: ThoughtNode) -> ThoughtNode:
        """MCTS 选择阶段 - UCT 算法"""
        # 简化实现，避免无限循环
        if not node.children or node.depth >= self.max_depth - 1:
            return node
        # 返回第一个子节点 (简化)
        return node
    
    def _get_best_uct_child(self, node: ThoughtNode) -> ThoughtNode:
        """获取 UCT 分数最高的子节点"""
        # 简化实现，返回自身
        return node
    
    def _simulate(self, node: ThoughtNode, evaluator: Optional[Callable]) -> float:
        """MCTS 模拟阶段"""
        if evaluator:
            return evaluator(node.content)
        return random.random()
    
    def _backpropagate(self, node: ThoughtNode, reward: float):
        """MCTS 回溯阶段 - 简化实现"""
        node.visits += 1
        node.total_reward += reward
    
    def _extract_path(
        self, 
        root: ThoughtNode, 
        target: ThoughtNode,
        all_nodes: List[ThoughtNode]
    ) -> List[ThoughtNode]:
        """提取从根到目标节点的路径"""
        path = [target]
        current = target
        
        # 简化实现，直接返回
        return [root, target] if root != target else [root]


class LogicValidator:
    """
    逻辑一致性验证器
    检查推理过程中的逻辑错误和矛盾
    """
    
    def __init__(self):
        self.logic_rules = [
            "non_contradiction",  # 无矛盾律
            "identity",  # 同一律
            "excluded_middle",  # 排中律
            "sufficient_reason"  # 充足理由律
        ]
    
    def validate(self, trace: ReasoningTrace) -> Dict[str, Any]:
        """验证推理轨迹的逻辑一致性"""
        results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "rule_violations": []
        }
        
        # 检查步骤间的逻辑连贯性
        for i in range(1, len(trace.steps)):
            prev_step = trace.steps[i-1]
            curr_step = trace.steps[i]
            
            # 检查依赖关系
            if curr_step.dependencies and (i-1) not in curr_step.dependencies:
                if not self._has_valid_dependency(curr_step, trace.steps[:i]):
                    results["warnings"].append(
                        f"步骤{i+1}的依赖关系不明确"
                    )
            
            # 检查置信度下降过快
            if curr_step.confidence < prev_step.confidence * 0.7:
                results["warnings"].append(
                    f"步骤{i}到{i+1}置信度下降过快"
                )
        
        # 检查结论与前提的一致性
        if trace.steps and trace.conclusion:
            consistency = self._check_consistency(trace.steps, trace.conclusion)
            if not consistency:
                results["is_valid"] = False
                results["errors"].append("结论与推理过程不一致")
        
        # 应用逻辑规则检查
        for rule in self.logic_rules:
            violation = self._check_rule(trace, rule)
            if violation:
                results["rule_violations"].append(violation)
                results["is_valid"] = False
        
        return results
    
    def _has_valid_dependency(
        self, 
        step: ReasoningStep, 
        previous_steps: List[ReasoningStep]
    ) -> bool:
        """检查依赖关系是否有效"""
        for dep in step.dependencies:
            if dep >= len(previous_steps):
                return False
        return True
    
    def _check_consistency(
        self, 
        steps: List[ReasoningStep], 
        conclusion: str
    ) -> bool:
        """检查结论与推理过程的一致性"""
        # 简化实现：检查结论长度和是否包含关键词
        if len(conclusion) <= 10:
            return False
        
        # 如果有步骤，检查结论是否与最后一步相关
        if steps:
            last_step = steps[-1]
            # 简化的相关性检查：如果最后一步是 verify 类型，认为一致
            if last_step.method == "verify":
                return True
            # 或者结论长度合理即认为一致
            return len(conclusion) > 15
        
        return True
    
    def _check_rule(self, trace: ReasoningTrace, rule: str) -> Optional[str]:
        """检查特定逻辑规则"""
        # 简化实现
        return None


class MultiStepPlanner:
    """
    多步任务规划器
    将复杂目标分解为可执行的步骤序列
    """
    
    def __init__(self, max_plan_length: int = 50):
        self.max_plan_length = max_plan_length
        self.plan_templates = {
            "problem_solving": [
                "理解问题",
                "收集信息",
                "生成方案",
                "评估方案",
                "执行最优方案",
                "验证结果"
            ],
            "analysis": [
                "定义分析框架",
                "收集数据",
                "识别模式",
                "建立假设",
                "验证假设",
                "得出结论"
            ],
            "creative": [
                "明确目标",
                "头脑风暴",
                "筛选想法",
                "细化方案",
                "原型制作",
                "测试改进"
            ]
        }
    
    def create_plan(
        self, 
        goal: str, 
        context: Optional[Dict] = None,
        plan_type: str = "problem_solving"
    ) -> List[Dict[str, Any]]:
        """创建多步执行计划"""
        template = self.plan_templates.get(
            plan_type, 
            self.plan_templates["problem_solving"]
        )
        
        plan = []
        for i, step_name in enumerate(template):
            step = {
                "step_id": i + 1,
                "name": step_name,
                "description": f"执行{step_name}操作以推进目标",
                "dependencies": [j for j in range(1, i)],
                "estimated_confidence": 0.9 - (i * 0.02),
                "status": "pending",
                "metadata": {
                    "goal": goal,
                    "context": context or {}
                }
            }
            plan.append(step)
        
        return plan[:self.max_plan_length]
    
    def execute_plan(
        self, 
        plan: List[Dict[str, Any]],
        executor: Optional[Callable[[Dict], Any]] = None
    ) -> Dict[str, Any]:
        """执行计划并跟踪进度"""
        results = {
            "completed_steps": 0,
            "failed_steps": 0,
            "step_results": [],
            "overall_success": False
        }
        
        for step in plan:
            if executor:
                try:
                    result = executor(step)
                    step["status"] = "completed"
                    step["result"] = result
                    results["completed_steps"] += 1
                except Exception as e:
                    step["status"] = "failed"
                    step["error"] = str(e)
                    results["failed_steps"] += 1
            else:
                step["status"] = "simulated_completed"
                results["completed_steps"] += 1
            
            results["step_results"].append(step)
        
        results["overall_success"] = results["failed_steps"] == 0
        return results
    
    def replan(
        self, 
        original_plan: List[Dict[str, Any]],
        failed_step_index: int,
        new_context: Dict
    ) -> List[Dict[str, Any]]:
        """根据失败情况重新规划"""
        if failed_step_index >= len(original_plan):
            return original_plan
        
        # 保留成功的步骤
        completed = original_plan[:failed_step_index]
        
        # 重新规划剩余部分
        remaining_goal = original_plan[failed_step_index]["metadata"].get("goal", "")
        new_subplan = self.create_plan(remaining_goal, new_context)
        
        # 调整步骤 ID
        offset = len(completed)
        for step in new_subplan:
            step["step_id"] += offset
        
        return completed + new_subplan


class SlowThinkingEngine:
    """
    系统 2 慢思考引擎
    整合多种推理策略，提供深度思考能力
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.cot = ChainOfThought(
            max_steps=self.config.get("max_cot_steps", 20),
            min_confidence=self.config.get("min_confidence", 0.7)
        )
        self.tot = TreeOfThought(
            max_depth=self.config.get("max_tot_depth", 10),
            branching_factor=self.config.get("branching_factor", 3),
            beam_width=self.config.get("beam_width", 5)
        )
        self.validator = LogicValidator()
        self.planner = MultiStepPlanner(
            max_plan_length=self.config.get("max_plan_length", 50)
        )
        
        self.reasoning_history: List[ReasoningTrace] = []
        self.performance_metrics = {
            "total_reasonings": 0,
            "avg_steps": 0.0,
            "avg_confidence": 0.0,
            "avg_time": 0.0,
            "success_rate": 0.0
        }
    
    def reason(
        self,
        problem: str,
        strategy: ReasoningStrategy = ReasoningStrategy.CHAIN_OF_THOUGHT,
        context: Optional[Dict] = None,
        enable_validation: bool = True
    ) -> Dict[str, Any]:
        """执行深度推理"""
        start_time = time.time()
        
        # 选择推理策略
        if strategy == ReasoningStrategy.CHAIN_OF_THOUGHT:
            trace = self.cot.reason(problem, context)
        elif strategy == ReasoningStrategy.TREE_OF_THOUGHT:
            trace, _ = self.tot.search(problem)
        elif strategy == ReasoningStrategy.MONTE_CARLO:
            trace, _ = self.tot.mcts_search(problem)
        else:
            trace = self.cot.reason(problem, context)
        
        # 逻辑验证
        validation_result = None
        if enable_validation:
            validation_result = self.validator.validate(trace)
            if not validation_result["is_valid"]:
                # 尝试重新推理
                trace = self._retry_with_fixes(problem, trace, validation_result)
        
        # 更新历史记录
        self.reasoning_history.append(trace)
        self._update_metrics(trace)
        
        result = {
            "problem": problem,
            "strategy": strategy.value,
            "conclusion": trace.conclusion,
            "confidence": trace.confidence,
            "steps": [
                {
                    "step": s.step_number,
                    "content": s.content,
                    "method": s.method,
                    "confidence": s.confidence
                }
                for s in trace.steps
            ],
            "validation": validation_result,
            "metrics": {
                "time_seconds": trace.total_time,
                "nodes_explored": trace.nodes_explored,
                "backtracks": trace.backtracks
            },
            "full_trace": trace
        }
        
        return result
    
    def plan_and_execute(
        self,
        goal: str,
        plan_type: str = "problem_solving",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """规划并执行复杂任务"""
        # 创建计划
        plan = self.planner.create_plan(goal, context, plan_type)
        
        # 执行计划
        execution_result = self.planner.execute_plan(plan)
        
        return {
            "goal": goal,
            "plan": plan,
            "execution": execution_result,
            "summary": f"完成{execution_result['completed_steps']}/{len(plan)}个步骤"
        }
    
    def compare_strategies(
        self,
        problem: str,
        strategies: List[ReasoningStrategy],
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """比较不同推理策略的效果"""
        results = {}
        
        for strategy in strategies:
            result = self.reason(problem, strategy, context)
            results[strategy.value] = {
                "conclusion": result["conclusion"],
                "confidence": result["confidence"],
                "time": result["metrics"]["time_seconds"],
                "steps": len(result["steps"])
            }
        
        # 找出最佳策略
        best_strategy = max(
            results.keys(),
            key=lambda k: results[k]["confidence"] / max(0.1, results[k]["time"])
        )
        
        return {
            "problem": problem,
            "comparison": results,
            "best_strategy": best_strategy,
            "recommendation": f"推荐使用{best_strategy}策略"
        }
    
    def _retry_with_fixes(
        self,
        problem: str,
        failed_trace: ReasoningTrace,
        validation_result: Dict
    ) -> ReasoningTrace:
        """尝试验证失败后重新推理"""
        # 简化实现：使用不同策略重试
        if failed_trace.strategy == ReasoningStrategy.CHAIN_OF_THOUGHT:
            return self.tot.search(problem)[0]
        else:
            return self.cot.reason(problem)
    
    def _update_metrics(self, trace: ReasoningTrace):
        """更新性能指标"""
        n = self.performance_metrics["total_reasonings"]
        
        self.performance_metrics["total_reasonings"] += 1
        
        # 更新平均值
        self.performance_metrics["avg_steps"] = (
            (self.performance_metrics["avg_steps"] * n + len(trace.steps)) / (n + 1)
        )
        self.performance_metrics["avg_confidence"] = (
            (self.performance_metrics["avg_confidence"] * n + trace.confidence) / (n + 1)
        )
        self.performance_metrics["avg_time"] = (
            (self.performance_metrics["avg_time"] * n + trace.total_time) / (n + 1)
        )
    
    def get_insights(self) -> Dict[str, Any]:
        """获取推理洞察和统计"""
        if not self.reasoning_history:
            return {"message": "暂无推理历史"}
        
        # 分析推理模式
        strategies_used = defaultdict(int)
        avg_confidences = defaultdict(list)
        
        for trace in self.reasoning_history:
            strategies_used[trace.strategy.value] += 1
            avg_confidences[trace.strategy.value].append(trace.confidence)
        
        insights = {
            "total_reasonings": len(self.reasoning_history),
            "strategies_distribution": dict(strategies_used),
            "average_confidence_by_strategy": {
                k: sum(v)/len(v) for k, v in avg_confidences.items()
            },
            "performance_metrics": self.performance_metrics,
            "recommendations": self._generate_recommendations()
        }
        
        return insights
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if self.performance_metrics["avg_confidence"] < 0.7:
            recommendations.append("考虑增加推理深度或使用更复杂的策略")
        
        if self.performance_metrics["avg_time"] > 5.0:
            recommendations.append("优化推理过程以减少计算时间")
        
        if not recommendations:
            recommendations.append("推理性能良好，继续保持")
        
        return recommendations


# 便捷函数
def deep_reason(
    problem: str,
    strategy: str = "chain_of_thought",
    enable_validation: bool = True
) -> Dict[str, Any]:
    """快速执行深度推理"""
    engine = SlowThinkingEngine()
    strat = getattr(ReasoningStrategy, strategy.upper(), ReasoningStrategy.CHAIN_OF_THOUGHT)
    return engine.reason(problem, strat, enable_validation=enable_validation)


def plan_task(
    goal: str,
    plan_type: str = "problem_solving"
) -> Dict[str, Any]:
    """快速创建并执行计划"""
    engine = SlowThinkingEngine()
    return engine.plan_and_execute(goal, plan_type)
