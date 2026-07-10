"""
阶段 15：社会认知与心智理论 (Social Cognition & Theory of Mind)

实现对他人的信念、意图、情感和知识状态的推断能力，
支持多智能体交互、欺骗检测、共情推理和社会学习。

核心组件:
- MentalState: 心智状态表示（信念、欲望、意图）
- TheoryOfMindEngine: 心智理论引擎
- EmpathyModule: 共情推理模块
- IntentionRecognizer: 意图识别器
- SocialLearningEngine: 社会学习引擎
- DeceptionDetector: 欺骗检测器
- PerspectiveTaker: 视角采择器
- SocialNetworkModel: 社会网络模型
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any, TypeVar
from enum import Enum, auto
import random
import math
from collections import defaultdict
import copy

# ==================== 基础数据结构 ====================


class EmotionType(Enum):
    """基本情绪类型（基于 Ekman 的六种基本情绪）"""

    JOY = auto()  # 快乐
    SADNESS = auto()  # 悲伤
    ANGER = auto()  # 愤怒
    FEAR = auto()  # 恐惧
    SURPRISE = auto()  # 惊讶
    DISGUST = auto()  # 厌恶
    # 复合情绪
    PRIDE = auto()  # 自豪
    GUILT = auto()  # 内疚
    SHAME = auto()  # 羞愧
    ENVY = auto()  # 嫉妒
    GRATITUDE = auto()  # 感激
    CONTEMPT = auto()  # 轻蔑
    HOPE = auto()  # 希望
    DISAPPOINTMENT = auto()  # 失望
    RELIEF = auto()  # 宽慰
    REGRET = auto()  # 后悔


class IntentionType(Enum):
    """意图类型"""

    COOPERATE = auto()  # 合作
    COMPETE = auto()  # 竞争
    HELP = auto()  # 帮助
    HARM = auto()  # 伤害
    DECEIVE = auto()  # 欺骗
    PERSUADE = auto()  # 说服
    INFORM = auto()  # 告知
    REQUEST = auto()  # 请求
    COMMAND = auto()  # 命令
    PROMISE = auto()  # 承诺
    THREATEN = auto()  # 威胁
    APOLOGIZE = auto()  # 道歉
    BLUFF = auto()  # 虚张声势
    MANIPULATE = auto()  # 操纵
    EXPLORE = auto()  # 探索
    AVOID = auto()  # 回避


# 为兼容性添加别名
IntentionType.FEAR = IntentionType.AVOID


class BeliefStrength(Enum):
    """信念强度"""

    CERTAIN = 1.0  # 确定
    VERY_LIKELY = 0.9  # 非常可能
    LIKELY = 0.7  # 可能
    POSSIBLE = 0.5  # 有可能
    UNLIKELY = 0.3  # 不太可能
    VERY_UNLIKELY = 0.1  # 很不可能
    IMPOSSIBLE = 0.0  # 不可能


@dataclass
class Emotion:
    """情绪表示"""

    emotion_type: EmotionType
    intensity: float = 0.5  # 强度 0.0-1.0
    valence: float = 0.0  # 效价 -1.0(负面) 到 1.0(正面)
    arousal: float = 0.5  # 唤醒度 0.0-1.0
    object: Optional[str] = None  # 情绪对象
    cause: Optional[str] = None  # 情绪原因

    def __post_init__(self):
        if self.valence == 0.0:
            self.valence = self._default_valence()
        if self.arousal == 0.5:
            self.arousal = self._default_arousal()

    def _default_valence(self) -> float:
        positive_emotions = {
            EmotionType.JOY,
            EmotionType.PRIDE,
            EmotionType.GRATITUDE,
            EmotionType.HOPE,
            EmotionType.RELIEF,
        }
        negative_emotions = {
            EmotionType.SADNESS,
            EmotionType.ANGER,
            EmotionType.FEAR,
            EmotionType.DISGUST,
            EmotionType.GUILT,
            EmotionType.SHAME,
            EmotionType.ENVY,
            EmotionType.CONTEMPT,
            EmotionType.DISAPPOINTMENT,
            EmotionType.REGRET,
        }
        if self.emotion_type in positive_emotions:
            return 0.8
        elif self.emotion_type in negative_emotions:
            return -0.8
        return 0.0

    def _default_arousal(self) -> float:
        high_arousal = {
            EmotionType.ANGER,
            EmotionType.FEAR,
            EmotionType.SURPRISE,
            EmotionType.JOY,
            EmotionType.DISGUST,
        }
        low_arousal = {
            EmotionType.SADNESS,
            EmotionType.GUILT,
            EmotionType.SHAME,
            EmotionType.RELIEF,
            EmotionType.DISAPPOINTMENT,
        }
        if self.emotion_type in high_arousal:
            return 0.7
        elif self.emotion_type in low_arousal:
            return 0.3
        return 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.emotion_type.name,
            "intensity": self.intensity,
            "valence": self.valence,
            "arousal": self.arousal,
            "object": self.object,
            "cause": self.cause,
        }


@dataclass
class Belief:
    """信念表示"""

    content: str  # 信念内容
    strength: BeliefStrength = BeliefStrength.POSSIBLE
    source: Optional[str] = None  # 信念来源
    timestamp: int = 0  # 形成时间
    is_common_knowledge: bool = False  # 是否为共同知识
    justification: Optional[str] = None  # 理由

    @property
    def confidence(self) -> float:
        return self.strength.value

    def update_strength(
        self, new_evidence_strength: float, evidence_reliability: float = 0.8
    ) -> None:
        """根据新证据更新信念强度"""
        current = self.confidence
        weighted_evidence = new_evidence_strength * evidence_reliability
        updated = current + (weighted_evidence - current) * 0.3
        self.strength = self._float_to_strength(updated)

    def _float_to_strength(self, value: float) -> BeliefStrength:
        if value >= 0.95:
            return BeliefStrength.CERTAIN
        elif value >= 0.8:
            return BeliefStrength.VERY_LIKELY
        elif value >= 0.6:
            return BeliefStrength.LIKELY
        elif value >= 0.4:
            return BeliefStrength.POSSIBLE
        elif value >= 0.2:
            return BeliefStrength.UNLIKELY
        elif value > 0.0:
            return BeliefStrength.VERY_UNLIKELY
        else:
            return BeliefStrength.IMPOSSIBLE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "strength": self.strength.name,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp,
            "is_common_knowledge": self.is_common_knowledge,
        }


@dataclass
class Desire:
    """欲望/目标表示"""

    content: str
    priority: float = 0.5  # 优先级 0.0-1.0
    urgency: float = 0.5  # 紧急程度 0.0-1.0
    is_achieved: bool = False
    achievement_conditions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "priority": self.priority,
            "urgency": self.urgency,
            "is_achieved": self.is_achieved,
        }


@dataclass
class Intention:
    """意图表示"""

    intention_type: IntentionType
    target: str  # 意图目标
    target_agent: Optional[str] = None  # 目标对象（其他智能体）
    plan: List[str] = field(default_factory=list)  # 实现计划
    commitment_level: float = 0.5  # 承诺程度 0.0-1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.intention_type.name,
            "target": self.target,
            "target_agent": self.target_agent,
            "plan": self.plan,
            "commitment": self.commitment_level,
        }


@dataclass
class MentalState:
    """完整的心智状态（BDI 架构：Belief-Desire-Intention）"""

    agent_id: str
    beliefs: Dict[str, Belief] = field(default_factory=dict)
    desires: Dict[str, Desire] = field(default_factory=dict)
    intentions: Dict[str, Intention] = field(default_factory=dict)
    emotions: List[Emotion] = field(default_factory=list)
    knowledge_state: Dict[str, bool] = field(default_factory=dict)  # 知道什么
    attention_focus: Optional[str] = None  # 注意力焦点

    def add_belief(
        self,
        content: str,
        strength: BeliefStrength = BeliefStrength.POSSIBLE,
        source: Optional[str] = None,
    ) -> None:
        belief = Belief(content=content, strength=strength, source=source)
        self.beliefs[content] = belief

    def add_desire(self, content: str, priority: float = 0.5) -> None:
        desire = Desire(content=content, priority=priority)
        self.desires[content] = desire

    def add_intention(
        self, intention_type: IntentionType, target: str, target_agent: Optional[str] = None
    ) -> None:
        key = f"{intention_type.name}_{target}"
        intention = Intention(
            intention_type=intention_type, target=target, target_agent=target_agent
        )
        self.intentions[key] = intention

    def add_emotion(self, emotion: Emotion) -> None:
        self.emotions.append(emotion)

    def get_dominant_emotion(self) -> Optional[Emotion]:
        if not self.emotions:
            return None
        return max(self.emotions, key=lambda e: e.intensity)

    def get_emotional_valence(self) -> float:
        if not self.emotions:
            return 0.0
        total_intensity = sum(e.intensity for e in self.emotions)
        if total_intensity == 0:
            return 0.0
        weighted_valence = sum(e.valence * e.intensity for e in self.emotions)
        return weighted_valence / total_intensity

    def is_consistent(self) -> Tuple[bool, List[str]]:
        """检查心智状态的一致性"""
        inconsistencies = []

        # 检查信念冲突
        belief_contents = list(self.beliefs.keys())
        for i, b1 in enumerate(belief_contents):
            for b2 in belief_contents[i + 1 :]:
                if self._are_contradictory(b1, b2):
                    inconsistencies.append(f"Contradictory beliefs: {b1} vs {b2}")

        # 检查意图与信念的冲突
        for intention in self.intentions.values():
            for belief in self.beliefs.values():
                if belief.confidence > 0.8 and self._intention_conflicts_belief(intention, belief):
                    inconsistencies.append(
                        f"Intention '{intention.target}' conflicts with belief '{belief.content}'"
                    )

        return len(inconsistencies) == 0, inconsistencies

    def _are_contradictory(self, belief1: str, belief2: str) -> bool:
        """简单的矛盾检测"""
        negations = ["not ", "no ", "never ", "cannot ", "can't ", "won't "]
        b1_lower = belief1.lower()
        b2_lower = belief2.lower()

        for neg in negations:
            if b1_lower == neg + b2_lower or b2_lower == neg + b1_lower:
                return True

        return False

    def _intention_conflicts_belief(self, intention: Intention, belief: Belief) -> bool:
        """检查意图是否与信念冲突"""
        if intention.intention_type == IntentionType.AVOID:
            return intention.target in belief.content

        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "beliefs": {k: v.to_dict() for k, v in self.beliefs.items()},
            "desires": {k: v.to_dict() for k, v in self.desires.items()},
            "intentions": {k: v.to_dict() for k, v in self.intentions.items()},
            "emotions": [e.to_dict() for e in self.emotions],
            "dominant_emotion": (
                self.get_dominant_emotion().to_dict() if self.get_dominant_emotion() else None
            ),
            "emotional_valence": self.get_emotional_valence(),
        }


# ==================== 心智理论引擎 ====================


class TheoryOfMindEngine:
    """
    心智理论引擎：推断他人的心智状态

    支持多级心智理论：
    - 零阶：理解他人有信念和欲望
    - 一阶：理解他人相信 X
    - 二阶：理解他人相信我相信 X
    - 更高阶：递归推理
    """

    def __init__(self, max_order: int = 3):
        self.max_order = max_order
        self.agent_models: Dict[str, MentalState] = {}
        self.self_model: Optional[MentalState] = None
        self.interaction_history: List[Dict[str, Any]] = []
        self.inference_cache: Dict[str, Any] = {}

    def register_agent(self, agent_id: str, initial_state: Optional[MentalState] = None) -> None:
        """注册一个智能体并初始化其心智模型"""
        if initial_state:
            self.agent_models[agent_id] = initial_state
        else:
            self.agent_models[agent_id] = MentalState(agent_id=agent_id)

    def set_self_model(self, mental_state: MentalState) -> None:
        """设置自我的心智模型"""
        self.self_model = mental_state

    def infer_belief(self, agent_id: str, proposition: str, evidence: List[str] = None) -> Belief:
        """推断某智能体对某个命题的信念"""
        if agent_id not in self.agent_models:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent_state = self.agent_models[agent_id]

        # 检查是否已有该信念
        if proposition in agent_state.beliefs:
            return agent_state.beliefs[proposition]

        # 基于证据推断
        inferred_strength = self._infer_belief_strength(agent_state, proposition, evidence or [])

        inferred_belief = Belief(
            content=proposition,
            strength=self._float_to_strength(inferred_strength),
            source="inference",
        )

        # 缓存推断结果
        cache_key = f"belief_{agent_id}_{proposition}"
        self.inference_cache[cache_key] = inferred_belief

        return inferred_belief

    def infer_intention(
        self, agent_id: str, observed_actions: List[str], context: Optional[str] = None
    ) -> Optional[Intention]:
        """从观察到的行为推断意图"""
        if agent_id not in self.agent_models:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent_state = self.agent_models[agent_id]

        # 基于行动模式识别意图
        intention_scores: Dict[IntentionType, float] = defaultdict(float)

        action_patterns = {
            IntentionType.COOPERATE: ["help", "share", "collaborate", "assist"],
            IntentionType.COMPETE: ["challenge", "oppose", "contest", "rival"],
            IntentionType.HELP: ["aid", "support", "rescue", "facilitate"],
            IntentionType.HARM: ["attack", "hurt", "damage", "threaten"],
            IntentionType.DECEIVE: ["lie", "mislead", "conceal", "fabricate"],
            IntentionType.PERSUADE: ["convince", "argue", "influence", "sway"],
            IntentionType.INFORM: ["tell", "explain", "describe", "notify"],
            IntentionType.REQUEST: ["ask", "request", "beg", "solicit"],
            IntentionType.AVOID: ["evade", "escape", "dodge", "withdraw"],
        }

        for action in observed_actions:
            action_lower = action.lower()
            for intention_type, patterns in action_patterns.items():
                for pattern in patterns:
                    if pattern in action_lower:
                        intention_scores[intention_type] += 0.3

        # 考虑上下文
        if context:
            context_lower = context.lower()
            if "competition" in context_lower or "contest" in context_lower:
                intention_scores[IntentionType.COMPETE] += 0.5
            if "emergency" in context_lower or "crisis" in context_lower:
                intention_scores[IntentionType.HELP] += 0.5
            if "negotiation" in context_lower:
                intention_scores[IntentionType.PERSUADE] += 0.4

        if not intention_scores:
            return None

        # 选择得分最高的意图
        best_intention_type = max(intention_scores, key=intention_scores.get)
        confidence = min(intention_scores[best_intention_type], 1.0)

        inferred_intention = Intention(
            intention_type=best_intention_type,
            target=observed_actions[-1] if observed_actions else "unknown",
            target_agent=agent_id,
            commitment_level=confidence,
        )

        return inferred_intention

    def infer_emotion(
        self, agent_id: str, situation: str, agent_goals: List[str] = None
    ) -> List[Emotion]:
        """基于情境推断他人的情绪"""
        if agent_id not in self.agent_models:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent_state = self.agent_models[agent_id]
        inferred_emotions = []

        # 情境 - 情绪映射规则
        situation_keywords = {
            EmotionType.JOY: ["success", "win", "achieve", "celebrate", "gift", "praise"],
            EmotionType.SADNESS: ["loss", "fail", "death", "reject", "disappoint"],
            EmotionType.ANGER: ["insult", "betray", "unfair", "obstacle", "frustrate"],
            EmotionType.FEAR: ["danger", "threat", "risk", "uncertain", "scary"],
            EmotionType.SURPRISE: ["unexpected", "sudden", "shock", "astonish"],
            EmotionType.DISGUST: ["dirty", "contaminate", "repulsive", "vile"],
            EmotionType.GUILT: ["wrong", "harm", "mistake", "regret"],
            EmotionType.PRIDE: ["accomplish", "excel", "honor", "recognition"],
            EmotionType.SHAME: ["humiliate", "expose", "embarrass", "dishonor"],
            EmotionType.ENVY: ["envy", "jealous", "covet", "resent"],
            EmotionType.GRATITUDE: ["grateful", "thank", "appreciate", "kindness"],
            EmotionType.HOPE: ["hope", "expect", "anticipate", "wish"],
        }

        situation_lower = situation.lower()

        for emotion_type, keywords in situation_keywords.items():
            match_count = sum(1 for kw in keywords if kw in situation_lower)
            if match_count > 0:
                intensity = min(match_count * 0.3, 1.0)

                # 考虑目标达成情况
                if agent_goals:
                    goal_achievement = self._assess_goal_achievement(situation, agent_goals)
                    if goal_achievement > 0.5 and emotion_type in [
                        EmotionType.JOY,
                        EmotionType.PRIDE,
                        EmotionType.RELIEF,
                    ]:
                        intensity = min(intensity + 0.2, 1.0)
                    elif goal_achievement < 0.3 and emotion_type in [
                        EmotionType.SADNESS,
                        EmotionType.ANGER,
                        EmotionType.DISAPPOINTMENT,
                    ]:
                        intensity = min(intensity + 0.2, 1.0)

                emotion = Emotion(emotion_type=emotion_type, intensity=intensity, cause=situation)
                inferred_emotions.append(emotion)

        return inferred_emotions

    def second_order_inference(self, observer_id: str, target_id: str, proposition: str) -> Belief:
        """二阶推断：observer 认为 target 相信什么"""
        if observer_id not in self.agent_models:
            raise ValueError(f"Unknown observer: {observer_id}")
        if target_id not in self.agent_models:
            raise ValueError(f"Unknown target: {target_id}")

        observer_state = self.agent_models[observer_id]

        # observer 对 target 心智模型的推断
        # 这需要考虑 observer 所知道的关于 target 的信息
        target_model_as_seen_by_observer = self._construct_perspective(observer_state, target_id)

        # 在该视角下推断 target 的信念
        if proposition in target_model_as_seen_by_observer.beliefs:
            return target_model_as_seen_by_observer.beliefs[proposition]

        # 默认推断
        return Belief(
            content=proposition,
            strength=BeliefStrength.POSSIBLE,
            source=f"second_order_inference_{observer_id}_about_{target_id}",
        )

    def false_belief_test(
        self, agent_id: str, actual_state: str, agent_observation: str
    ) -> Tuple[Belief, bool]:
        """
        错误信念测试（Sally-Anne 测试变体）

        返回：(推断的信念，是否是错误信念)
        """
        if agent_id not in self.agent_models:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent_state = self.agent_models[agent_id]

        # 基于 agent 的观察推断其信念
        inferred_belief = Belief(
            content=agent_observation, strength=BeliefStrength.LIKELY, source="observation"
        )

        # 检查是否是错误信念
        is_false_belief = agent_observation != actual_state

        return inferred_belief, is_false_belief

    def perspective_taking(self, agent_id: str, scenario: str) -> Dict[str, Any]:
        """
        视角采择：从特定智能体的角度理解情境

        返回该智能体可能看到、知道和感受到的内容
        """
        if agent_id not in self.agent_models:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent_state = self.agent_models[agent_id]

        # 构建该智能体的视角
        perspective = {
            "agent_id": agent_id,
            "visible_information": self._get_visible_information(agent_state, scenario),
            "hidden_information": self._get_hidden_information(agent_state, scenario),
            "likely_beliefs": self._infer_likely_beliefs(agent_state, scenario),
            "likely_emotions": self.infer_emotion(agent_id, scenario),
            "knowledge_gaps": self._identify_knowledge_gaps(agent_state, scenario),
        }

        return perspective

    def update_agent_model(
        self, agent_id: str, new_observation: str, new_action: Optional[str] = None
    ) -> None:
        """根据新的观察更新对智能体的心智模型"""
        if agent_id not in self.agent_models:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent_state = self.agent_models[agent_id]

        # 记录交互历史
        self.interaction_history.append(
            {
                "agent_id": agent_id,
                "observation": new_observation,
                "action": new_action,
                "timestamp": len(self.interaction_history),
            }
        )

        # 基于新观察更新信念
        self._update_beliefs_from_observation(agent_state, new_observation)

        # 如果有新行动，更新意图推断
        if new_action:
            self._update_intentions_from_action(agent_state, new_action)

    def _infer_belief_strength(
        self, agent_state: MentalState, proposition: str, evidence: List[str]
    ) -> float:
        """推断信念强度"""
        base_strength = 0.5

        # 考虑 agent 的专业领域
        expertise_bonus = self._check_expertise_relevance(agent_state, proposition)
        base_strength += expertise_bonus

        # 考虑证据质量
        for ev in evidence:
            ev_strength = self._evaluate_evidence_quality(ev)
            base_strength += ev_strength * 0.1

        return min(max(base_strength, 0.0), 1.0)

    def _float_to_strength(self, value: float) -> BeliefStrength:
        if value >= 0.95:
            return BeliefStrength.CERTAIN
        elif value >= 0.8:
            return BeliefStrength.VERY_LIKELY
        elif value >= 0.6:
            return BeliefStrength.LIKELY
        elif value >= 0.4:
            return BeliefStrength.POSSIBLE
        elif value >= 0.2:
            return BeliefStrength.UNLIKELY
        elif value > 0.0:
            return BeliefStrength.VERY_UNLIKELY
        else:
            return BeliefStrength.IMPOSSIBLE

    def _check_expertise_relevance(self, agent_state: MentalState, proposition: str) -> float:
        """检查命题是否与 agent 的专业领域相关"""
        # 简化实现：基于信念内容判断
        expertise_domains = {
            "science": ["physics", "chemistry", "biology", "experiment"],
            "medicine": ["health", "disease", "treatment", "symptom"],
            "technology": ["computer", "software", "algorithm", "data"],
        }

        prop_lower = proposition.lower()
        for domain, keywords in expertise_domains.items():
            if any(kw in prop_lower for kw in keywords):
                # 检查 agent 是否有相关信念
                for belief_content in agent_state.beliefs.keys():
                    if any(kw in belief_content.lower() for kw in keywords):
                        return 0.2

        return 0.0

    def _evaluate_evidence_quality(self, evidence: str) -> float:
        """评估证据质量"""
        quality_indicators = {
            "direct observation": 0.9,
            "firsthand": 0.8,
            "reliable source": 0.7,
            "documented": 0.7,
            "corroborated": 0.8,
            "hearsay": 0.3,
            "rumor": 0.2,
            "speculation": 0.3,
        }

        evidence_lower = evidence.lower()
        for indicator, quality in quality_indicators.items():
            if indicator in evidence_lower:
                return quality

        return 0.5  # 默认中等质量

    def _assess_goal_achievement(self, situation: str, goals: List[str]) -> float:
        """评估目标达成程度"""
        achievement_keywords = ["achieved", "accomplished", "completed", "succeeded"]
        failure_keywords = ["failed", "lost", "missed", "unable"]

        situation_lower = situation.lower()

        achieved = sum(1 for kw in achievement_keywords if kw in situation_lower)
        failed = sum(1 for kw in failure_keywords if kw in situation_lower)

        total = achieved + failed
        if total == 0:
            return 0.5

        return achieved / total

    def _construct_perspective(self, observer_state: MentalState, target_id: str) -> MentalState:
        """构建观察者视角下的目标心智模型"""
        # 创建一个简化的目标心智模型，基于观察者的知识
        perspective_state = MentalState(agent_id=target_id)

        # 只包含观察者认为 target 知道的内容
        for belief_content, belief in observer_state.beliefs.items():
            if observer_state.knowledge_state.get(f"{target_id}_knows_{belief_content}", False):
                perspective_state.beliefs[belief_content] = belief

        return perspective_state

    def _get_visible_information(self, agent_state: MentalState, scenario: str) -> List[str]:
        """获取从该智能体视角可见的信息"""
        visible = []

        # 基于注意力和信念确定可见信息
        if agent_state.attention_focus:
            visible.append(f"Focusing on: {agent_state.attention_focus}")

        for belief_content, belief in list(agent_state.beliefs.items())[:5]:
            if belief.confidence > 0.5:
                visible.append(belief_content)

        return visible

    def _get_hidden_information(self, agent_state: MentalState, scenario: str) -> List[str]:
        """获取该智能体不知道的信息"""
        hidden = []

        # 低置信度的信念可能是隐藏信息
        for belief_content, belief in agent_state.beliefs.items():
            if belief.confidence < 0.3:
                hidden.append(belief_content)

        return hidden

    def _infer_likely_beliefs(self, agent_state: MentalState, scenario: str) -> List[str]:
        """推断可能的信念"""
        likely = []

        for belief_content, belief in agent_state.beliefs.items():
            if belief.confidence >= 0.6:
                likely.append(belief_content)

        return likely

    def _identify_knowledge_gaps(self, agent_state: MentalState, scenario: str) -> List[str]:
        """识别知识空白"""
        gaps = []

        # 查找 agent 没有形成信念的重要方面
        important_topics = ["cause", "effect", "motivation", "consequence"]
        for topic in important_topics:
            if not any(topic in content for content in agent_state.beliefs.keys()):
                gaps.append(f"Uncertainty about {topic}")

        return gaps

    def _update_beliefs_from_observation(self, agent_state: MentalState, observation: str) -> None:
        """从观察更新信念"""
        # 简化实现：将观察作为新信念添加
        agent_state.add_belief(observation, BeliefStrength.LIKELY, source="observation")

    def _update_intentions_from_action(self, agent_state: MentalState, action: str) -> None:
        """从行动更新意图"""
        # 基于行动推断并更新意图
        action_lower = action.lower()

        if "help" in action_lower or "assist" in action_lower:
            agent_state.add_intention(IntentionType.HELP, action)
        elif "attack" in action_lower or "harm" in action_lower:
            agent_state.add_intention(IntentionType.HARM, action)
        elif "lie" in action_lower or "deceive" in action_lower:
            agent_state.add_intention(IntentionType.DECEIVE, action)


# ==================== 共情推理模块 ====================


class EmpathyModule:
    """
    共情推理模块：理解和分享他人的情感体验

    包含：
    - 情感共鸣（affective empathy）
    - 认知共情（cognitive empathy）
    - 共情关注（empathic concern）
    """

    def __init__(self):
        self.empathy_levels: Dict[str, float] = {}  # 对不同智能体的共情水平
        self.emotional_contagion_rate = 0.6  # 情绪传染率
        self.perspective_taking_ability = 0.8  # 视角采择能力

    def set_empathy_level(self, target_agent: str, level: float) -> None:
        """设置对特定智能体的共情水平"""
        self.empathy_levels[target_agent] = min(max(level, 0.0), 1.0)

    def resonate_emotion(self, observed_emotion: Emotion, relationship: str = "neutral") -> Emotion:
        """
        情感共鸣：感受他人的情绪

        关系调节因子：
        - friend/family: 增强共鸣
        - stranger: 基准共鸣
        - enemy: 减弱或反向共鸣
        """
        relationship_factors = {
            "family": 1.3,
            "friend": 1.2,
            "colleague": 1.0,
            "stranger": 0.8,
            "rival": 0.5,
            "enemy": -0.3,
            "neutral": 0.8,
        }

        factor = relationship_factors.get(relationship, 0.8)

        resonated_intensity = observed_emotion.intensity * self.emotional_contagion_rate * factor
        resonated_intensity = min(max(resonated_intensity, 0.0), 1.0)

        # 如果是负面关系，可能会产生相反的情绪
        if factor < 0:
            opposite_emotion = self._get_opposite_emotion(observed_emotion.emotion_type)
            return Emotion(
                emotion_type=opposite_emotion,
                intensity=abs(resonated_intensity),
                valence=-observed_emotion.valence,
                arousal=observed_emotion.arousal,
                object=observed_emotion.object,
                cause=f"Resonating with {observed_emotion.cause}",
            )

        return Emotion(
            emotion_type=observed_emotion.emotion_type,
            intensity=resonated_intensity,
            valence=observed_emotion.valence,
            arousal=observed_emotion.arousal,
            object=observed_emotion.object,
            cause=f"Empathizing with {observed_emotion.cause}",
        )

    def cognitive_empathy(self, target_mental_state: MentalState, situation: str) -> Dict[str, Any]:
        """
        认知共情：理解他人的心理状态

        返回对他人状态的理解报告
        """
        understanding = {
            "emotional_state": target_mental_state.get_dominant_emotion(),
            "emotional_valence": target_mental_state.get_emotional_valence(),
            "primary_concerns": list(target_mental_state.desires.keys())[:3],
            "key_beliefs": [
                b.content for b in target_mental_state.beliefs.values() if b.confidence > 0.7
            ][:3],
            "potential_stressors": self._identify_stressors(target_mental_state, situation),
            "coping_needs": self._assess_coping_needs(target_mental_state),
        }

        return understanding

    def empathic_concern(self, target_state: MentalState) -> List[str]:
        """
        共情关注：产生帮助他人的动机

        返回建议的帮助行为
        """
        concerns = []

        dominant_emotion = target_state.get_dominant_emotion()
        valence = target_state.get_emotional_valence()

        if valence < -0.3:  # 负面情绪
            if dominant_emotion and dominant_emotion.emotion_type == EmotionType.SADNESS:
                concerns.extend(["Offer emotional support", "Provide comfort", "Listen actively"])
            elif dominant_emotion and dominant_emotion.emotion_type == EmotionType.FEAR:
                concerns.extend(
                    ["Provide reassurance", "Help assess actual risk", "Offer protection"]
                )
            elif dominant_emotion and dominant_emotion.emotion_type == EmotionType.ANGER:
                concerns.extend(
                    [
                        "Allow expression of feelings",
                        "Help identify underlying issues",
                        "Suggest constructive outlets",
                    ]
                )

        # 检查未满足的欲望
        for desire in target_state.desires.values():
            if not desire.is_achieved and desire.priority > 0.7:
                concerns.append(f"Assist in achieving: {desire.content}")

        return concerns

    def simulate_emotional_impact(self, event: str, target_state: MentalState) -> List[Emotion]:
        """
        模拟某事件对目标的情感影响

        预测目标会产生什么情绪
        """
        predicted_emotions = []

        # 基于事件的性质
        positive_events = ["success", "achievement", "praise", "reward", "reunion"]
        negative_events = ["failure", "loss", "criticism", "punishment", "separation"]
        threatening_events = ["danger", "risk", "uncertainty", "conflict"]

        event_lower = event.lower()

        # 积极事件
        for pos_event in positive_events:
            if pos_event in event_lower:
                # 检查是否与目标的欲望一致
                for desire in target_state.desires.values():
                    if desire.is_achieved or pos_event in desire.content.lower():
                        predicted_emotions.append(
                            Emotion(emotion_type=EmotionType.JOY, intensity=0.7, cause=event)
                        )
                        break
                else:
                    predicted_emotions.append(
                        Emotion(emotion_type=EmotionType.JOY, intensity=0.5, cause=event)
                    )

        # 消极事件
        for neg_event in negative_events:
            if neg_event in event_lower:
                predicted_emotions.append(
                    Emotion(emotion_type=EmotionType.SADNESS, intensity=0.6, cause=event)
                )

        # 威胁性事件
        for threat_event in threatening_events:
            if threat_event in event_lower:
                predicted_emotions.append(
                    Emotion(emotion_type=EmotionType.FEAR, intensity=0.7, cause=event)
                )

        return predicted_emotions

    def _get_opposite_emotion(self, emotion_type: EmotionType) -> EmotionType:
        """获取相反的情绪"""
        opposites = {
            EmotionType.JOY: EmotionType.SADNESS,
            EmotionType.SADNESS: EmotionType.JOY,
            EmotionType.ANGER: EmotionType.RELIEF,
            EmotionType.FEAR: EmotionType.HOPE,
            EmotionType.DISGUST: EmotionType.GRATITUDE,
        }
        return opposites.get(emotion_type, EmotionType.SURPRISE)

    def _identify_stressors(self, mental_state: MentalState, situation: str) -> List[str]:
        """识别压力源"""
        stressors = []

        # 高优先级的未满足欲望
        for desire in mental_state.desires.values():
            if not desire.is_achieved and desire.priority > 0.7:
                stressors.append(f"Unmet desire: {desire.content}")

        # 相互冲突的信念
        is_consistent, inconsistencies = mental_state.is_consistent()
        if not is_consistent:
            stressors.extend(inconsistencies[:2])

        # 负面情绪
        if mental_state.get_emotional_valence() < -0.3:
            stressors.append("Negative emotional state")

        return stressors

    def _assess_coping_needs(self, mental_state: MentalState) -> List[str]:
        """评估应对需求"""
        needs = []

        dominant_emotion = mental_state.get_dominant_emotion()

        if dominant_emotion:
            if dominant_emotion.intensity > 0.7:
                needs.append("Emotional regulation support")

            if dominant_emotion.emotion_type in [EmotionType.FEAR, EmotionType.ANGER]:
                needs.append("Stress management techniques")

        # 检查信念不确定性
        uncertain_beliefs = [b for b in mental_state.beliefs.values() if b.confidence < 0.4]
        if len(uncertain_beliefs) > 2:
            needs.append("Information clarification")

        return needs


# ==================== 意图识别器 ====================


class IntentionRecognizer:
    """
    意图识别器：从言语和行为中识别意图

    使用多层分析：
    1. 字面意义分析
    2. 语境分析
    3. 说话者特征分析
    4. 历史行为模式分析
    """

    def __init__(self):
        self.speech_act_patterns: Dict[str, IntentionType] = {
            "promise": IntentionType.PROMISE,
            "threat": IntentionType.THREATEN,
            "request": IntentionType.REQUEST,
            "command": IntentionType.COMMAND,
            "apology": IntentionType.APOLOGIZE,
            "offer": IntentionType.HELP,
            "warning": IntentionType.INFORM,
            "boast": IntentionType.COMPETE,
            "flattery": IntentionType.MANIPULATE,
        }

        self.behavioral_patterns: Dict[str, List[IntentionType]] = {
            "approaching": [IntentionType.COOPERATE, IntentionType.HELP, IntentionType.COMPETE],
            "avoiding": [IntentionType.AVOID, IntentionType.FEAR],
            "sharing": [IntentionType.COOPERATE, IntentionType.HELP],
            "hoarding": [IntentionType.COMPETE],
            "lying": [IntentionType.DECEIVE],
            "helping": [IntentionType.HELP],
        }

        self.context_weights: Dict[str, Dict[IntentionType, float]] = {
            "cooperative_context": {
                IntentionType.COOPERATE: 1.3,
                IntentionType.HELP: 1.2,
                IntentionType.COMPETE: 0.5,
            },
            "competitive_context": {
                IntentionType.COMPETE: 1.4,
                IntentionType.DECEIVE: 1.2,
                IntentionType.COOPERATE: 0.6,
            },
            "emergency_context": {
                IntentionType.HELP: 1.5,
                IntentionType.AVOID: 0.7,
            },
            "negotiation_context": {
                IntentionType.PERSUADE: 1.4,
                IntentionType.MANIPULATE: 1.1,
                IntentionType.DECEIVE: 1.0,
            },
        }

    def recognize_from_speech(self, utterance: str, context: str = "") -> Dict[str, Any]:
        """从言语识别意图"""
        utterance_lower = utterance.lower()

        intention_scores: Dict[IntentionType, float] = defaultdict(float)
        detected_speech_act = None

        # 言语行为识别
        for speech_act, intention in self.speech_act_patterns.items():
            if speech_act in utterance_lower:
                intention_scores[intention] += 0.6
                detected_speech_act = speech_act

        # 关键词匹配
        keyword_patterns = {
            IntentionType.REQUEST: ["can you", "could you", "please", "would you"],
            IntentionType.COMMAND: ["must", "have to", "need to", "do this"],
            IntentionType.PROMISE: ["I will", "I promise", "I guarantee"],
            IntentionType.THREATEN: ["or else", "otherwise", "you will regret"],
            IntentionType.APOLOGIZE: ["sorry", "apologize", "my fault"],
            IntentionType.INFORM: ["let me tell you", "did you know", "actually"],
            IntentionType.PERSUADE: ["you should", "it would be better", "consider"],
        }

        for intention, keywords in keyword_patterns.items():
            matches = sum(1 for kw in keywords if kw in utterance_lower)
            if matches > 0:
                intention_scores[intention] += matches * 0.2

        # 语境加权
        context_lower = context.lower()
        for ctx_name, weights in self.context_weights.items():
            if ctx_name.replace("_", " ") in context_lower:
                for intention, weight in weights.items():
                    intention_scores[intention] *= weight

        # 归一化并排序
        total = sum(intention_scores.values())
        if total > 0:
            for intention in intention_scores:
                intention_scores[intention] /= total

        sorted_intentions = sorted(intention_scores.items(), key=lambda x: x[1], reverse=True)

        result = {
            "primary_intention": sorted_intentions[0][0] if sorted_intentions else None,
            "confidence": sorted_intentions[0][1] if sorted_intentions else 0.0,
            "all_intentions": dict(sorted_intentions),
            "speech_act": detected_speech_act,
        }

        return result

    def recognize_from_behavior(self, actions: List[str], context: str = "") -> Dict[str, Any]:
        """从行为识别意图"""
        intention_scores: Dict[IntentionType, float] = defaultdict(float)

        for action in actions:
            action_lower = action.lower()

            # 行为模式匹配
            for behavior, intentions in self.behavioral_patterns.items():
                if behavior in action_lower:
                    for intention in intentions:
                        intention_scores[intention] += 0.3

            # 具体行动分析
            if "give" in action_lower or "share" in action_lower:
                intention_scores[IntentionType.HELP] += 0.4
                intention_scores[IntentionType.COOPERATE] += 0.3
            elif "take" in action_lower or "seize" in action_lower:
                intention_scores[IntentionType.COMPETE] += 0.4
            elif "hide" in action_lower or "conceal" in action_lower:
                intention_scores[IntentionType.DECEIVE] += 0.5
            elif "run" in action_lower or "flee" in action_lower:
                intention_scores[IntentionType.AVOID] += 0.5

        # 语境加权
        context_lower = context.lower()
        for ctx_name, weights in self.context_weights.items():
            if ctx_name.replace("_", " ") in context_lower:
                for intention, weight in weights.items():
                    intention_scores[intention] *= weight

        # 归一化
        total = sum(intention_scores.values())
        if total > 0:
            for intention in intention_scores:
                intention_scores[intention] /= total

        sorted_intentions = sorted(intention_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "primary_intention": sorted_intentions[0][0] if sorted_intentions else None,
            "confidence": sorted_intentions[0][1] if sorted_intentions else 0.0,
            "all_intentions": dict(sorted_intentions),
        }

    def recognize_combined(
        self,
        utterance: Optional[str],
        actions: List[str],
        context: str,
        speaker_profile: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """综合言语、行为和语境识别意图"""
        speech_result = {}
        behavior_result = {}

        if utterance:
            speech_result = self.recognize_from_speech(utterance, context)

        behavior_result = self.recognize_from_behavior(actions, context)

        # 融合结果
        combined_scores: Dict[IntentionType, float] = defaultdict(float)

        # 言语权重略高（通常更明确）
        speech_weight = 0.6
        behavior_weight = 0.4

        if speech_result:
            for intention, score in speech_result.get("all_intentions", {}).items():
                combined_scores[intention] += score * speech_weight

        if behavior_result:
            for intention, score in behavior_result.get("all_intentions", {}).items():
                combined_scores[intention] += score * behavior_weight

        # 说话者特征调整
        if speaker_profile:
            honesty = speaker_profile.get("honesty", 0.5)
            aggressiveness = speaker_profile.get("aggressiveness", 0.5)

            if honesty < 0.3:  # 不诚实的说话者
                combined_scores[IntentionType.DECEIVE] *= 1.5
                combined_scores[IntentionType.MANIPULATE] *= 1.3

            if aggressiveness > 0.7:
                combined_scores[IntentionType.COMPETE] *= 1.4
                combined_scores[IntentionType.THREATEN] *= 1.3

        # 归一化
        total = sum(combined_scores.values())
        if total > 0:
            for intention in combined_scores:
                combined_scores[intention] /= total

        sorted_intentions = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "primary_intention": sorted_intentions[0][0] if sorted_intentions else None,
            "confidence": sorted_intentions[0][1] if sorted_intentions else 0.0,
            "all_intentions": dict(sorted_intentions),
            "speech_analysis": speech_result,
            "behavior_analysis": behavior_result,
            "consistency": self._check_consistency(speech_result, behavior_result),
        }

    def _check_consistency(self, speech_result: Dict, behavior_result: Dict) -> float:
        """检查言语和行为的一致性"""
        if not speech_result or not behavior_result:
            return 1.0  # 无法比较时假设一致

        speech_primary = speech_result.get("primary_intention")
        behavior_primary = behavior_result.get("primary_intention")

        if speech_primary == behavior_primary:
            return 1.0

        # 检查是否相关
        related_intentions = {
            IntentionType.HELP: [IntentionType.COOPERATE],
            IntentionType.COMPETE: [IntentionType.THREATEN],
            IntentionType.DECEIVE: [IntentionType.MANIPULATE],
        }

        if speech_primary in related_intentions:
            if behavior_primary in related_intentions[speech_primary]:
                return 0.8

        if behavior_primary in related_intentions:
            if speech_primary in related_intentions[behavior_primary]:
                return 0.8

        return 0.3  # 不一致


# ==================== 欺骗检测器 ====================


class DeceptionDetector:
    """
    欺骗检测器：识别谎言和欺骗行为

    基于多种线索：
    - 言语不一致性
    - 非语言线索
    - 事实核查
    - 行为模式异常
    """

    def __init__(self):
        self.deception_indicators: Dict[str, float] = {
            "contradiction": 0.8,
            "vagueness": 0.5,
            "over_detail": 0.4,
            "delayed_response": 0.3,
            "inconsistent_emotion": 0.6,
            "avoiding_eye_contact": 0.4,
            "defensive_language": 0.5,
            "story_changes": 0.7,
            "factual_error": 0.9,
            "implausible_details": 0.6,
        }

        self.baseline_truthfulness: Dict[str, float] = {}

    def set_baseline(self, agent_id: str, truthfulness: float) -> None:
        """设置智能体的基线诚实度"""
        self.baseline_truthfulness[agent_id] = truthfulness

    def detect_deception(
        self,
        statement: str,
        context: str,
        agent_id: Optional[str] = None,
        nonverbal_cues: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        检测欺骗

        返回：
        - deception_probability: 欺骗概率
        - indicators: 检测到的欺骗指标
        - confidence: 检测置信度
        """
        indicators_found = []
        deception_score = 0.0

        # 分析言语内容
        content_indicators = self._analyze_statement(statement)
        for indicator, weight in content_indicators:
            indicators_found.append(indicator)
            deception_score += weight * self.deception_indicators.get(indicator, 0.5)

        # 分析非语言线索
        if nonverbal_cues:
            nonverbal_indicators = self._analyze_nonverbal(nonverbal_cues)
            for indicator, weight in nonverbal_indicators:
                indicators_found.append(indicator)
                deception_score += weight * self.deception_indicators.get(indicator, 0.5)

        # 考虑基线诚实度
        baseline = self.baseline_truthfulness.get(agent_id, 0.5) if agent_id else 0.5
        deception_score *= 1.0 - baseline * 0.3

        # 归一化到 0-1
        deception_probability = min(deception_score, 1.0)

        # 计算置信度（基于指标数量）
        confidence = min(len(indicators_found) * 0.15, 1.0)

        return {
            "deception_probability": deception_probability,
            "is_likely_deceptive": deception_probability > 0.5,
            "indicators": indicators_found,
            "confidence": confidence,
            "baseline_truthfulness": baseline,
        }

    def fact_check(self, statement: str, known_facts: Set[str]) -> Dict[str, Any]:
        """事实核查"""
        statement_lower = statement.lower()

        contradictions = []
        unsupported_claims = []

        for fact in known_facts:
            fact_lower = fact.lower()

            # 检查直接矛盾
            if self._are_contradictory(statement_lower, fact_lower):
                contradictions.append(fact)

        # 简单实现：检查陈述中的主张是否在已知事实中
        claims = self._extract_claims(statement)
        for claim in claims:
            if not any(claim in fact for fact in known_facts):
                unsupported_claims.append(claim)

        return {
            "contradictions": contradictions,
            "unsupported_claims": unsupported_claims,
            "credibility_score": 1.0 - (len(contradictions) * 0.3 + len(unsupported_claims) * 0.1),
        }

    def analyze_consistency(self, statements: List[str]) -> Dict[str, Any]:
        """分析多个陈述之间的一致性"""
        if len(statements) < 2:
            return {"is_consistent": True, "inconsistencies": []}

        inconsistencies = []

        for i, s1 in enumerate(statements):
            for s2 in statements[i + 1 :]:
                if self._are_contradictory(s1.lower(), s2.lower()):
                    inconsistencies.append((s1, s2))

        return {
            "is_consistent": len(inconsistencies) == 0,
            "inconsistencies": inconsistencies,
            "consistency_score": 1.0 - (len(inconsistencies) * 0.2),
        }

    def _analyze_statement(self, statement: str) -> List[Tuple[str, float]]:
        """分析陈述中的欺骗指标"""
        indicators = []
        statement_lower = statement.lower()

        # 矛盾检测（简化）
        if "but" in statement_lower and "earlier" in statement_lower:
            indicators.append(("contradiction", 0.7))

        # 模糊性
        vague_words = ["maybe", "perhaps", "possibly", "might", "could"]
        vague_count = sum(1 for word in vague_words if word in statement_lower)
        if vague_count >= 3:
            indicators.append(("vagueness", 0.6))

        # 过度细节
        words = statement.split()
        if len(words) > 50 and len(set(words)) / len(words) < 0.6:
            indicators.append(("over_detail", 0.5))

        # 防御性语言
        defensive_phrases = ["to be honest", "frankly", "believe me", "i swear"]
        if any(phrase in statement_lower for phrase in defensive_phrases):
            indicators.append(("defensive_language", 0.6))

        # 不合理细节
        implausible_words = ["miracle", "impossible", "never happened before"]
        if any(word in statement_lower for word in implausible_words):
            indicators.append(("implausible_details", 0.5))

        return indicators

    def _analyze_nonverbal(self, cues: Dict[str, Any]) -> List[Tuple[str, float]]:
        """分析非语言线索"""
        indicators = []

        if cues.get("eye_contact", 1.0) < 0.3:
            indicators.append(("avoiding_eye_contact", 0.7))

        if cues.get("response_delay", 0.5) > 2.0:  # 秒
            indicators.append(("delayed_response", 0.5))

        emotion = cues.get("emotion")
        statement_emotion = cues.get("statement_emotion")
        if emotion and statement_emotion and emotion != statement_emotion:
            indicators.append(("inconsistent_emotion", 0.8))

        return indicators

    def _are_contradictory(self, s1: str, s2: str) -> bool:
        """检查两个陈述是否矛盾"""
        negations = ["not ", "no ", "never ", "cannot ", "can't ", "won't "]

        for neg in negations:
            if s1 == neg + s2 or s2 == neg + s1:
                return True

        # 数字矛盾
        import re

        numbers1 = re.findall(r"\d+", s1)
        numbers2 = re.findall(r"\d+", s2)

        if numbers1 and numbers2 and set(numbers1) != set(numbers2):
            # 如果其他部分相似但数字不同，可能是矛盾
            words1 = set(s1.split()) - set(numbers1)
            words2 = set(s2.split()) - set(numbers2)
            if len(words1.intersection(words2)) > len(words1.union(words2)) * 0.7:
                return True

        return False

    def _extract_claims(self, statement: str) -> List[str]:
        """提取陈述中的主张"""
        # 简化实现：按连接词分割
        connectors = ["because", "therefore", "so", "and", "but"]
        claims = [statement]

        for connector in connectors:
            new_claims = []
            for claim in claims:
                new_claims.extend(claim.split(connector))
            claims = new_claims

        return [c.strip() for c in claims if c.strip()]


# ==================== 社会学习引擎 ====================


class SocialLearningEngine:
    """
    社会学习引擎：通过观察他人学习

    包含：
    - 观察学习（Observational Learning）
    - 模仿学习（Imitation Learning）
    - 教学学习（Instructional Learning）
    - 规范学习（Norm Learning）
    """

    def __init__(self):
        self.observed_behaviors: List[Dict[str, Any]] = []
        self.social_norms: Dict[str, Dict[str, Any]] = {}
        self.role_models: Dict[str, float] = {}  # 榜样及其影响力

    def observe_behavior(self, agent_id: str, behavior: str, outcome: str, context: str) -> None:
        """观察并记录他人行为"""
        observation = {
            "agent_id": agent_id,
            "behavior": behavior,
            "outcome": outcome,
            "context": context,
            "timestamp": len(self.observed_behaviors),
        }
        self.observed_behaviors.append(observation)

    def learn_from_observation(
        self, learner_state: MentalState, target_behavior: str
    ) -> Optional[str]:
        """
        从观察中学习

        返回：学习到的行为策略
        """
        relevant_observations = [
            obs for obs in self.observed_behaviors if target_behavior in obs["behavior"]
        ]

        if not relevant_observations:
            return None

        # 统计成功和失败
        success_count = 0
        failure_count = 0

        for obs in relevant_observations:
            if "success" in obs["outcome"].lower() or "positive" in obs["outcome"].lower():
                success_count += 1
            elif "fail" in obs["outcome"].lower() or "negative" in obs["outcome"].lower():
                failure_count += 1

        total = success_count + failure_count
        if total == 0:
            return None

        success_rate = success_count / total

        if success_rate > 0.6:
            # 学习到积极的行为
            learned_strategy = f"Adopt {target_behavior} (success rate: {success_rate:.2f})"
            learner_state.add_belief(
                f"{target_behavior} leads to positive outcomes",
                BeliefStrength.LIKELY,
                source="social_learning",
            )
            return learned_strategy
        elif success_rate < 0.4:
            # 学习到避免该行为
            learner_state.add_belief(
                f"Avoid {target_behavior} (failure rate: {1-success_rate:.2f})",
                BeliefStrength.LIKELY,
                source="social_learning",
            )
            return f"Avoid {target_behavior}"

        return None

    def imitate(
        self, model_agent_id: str, behavior_pattern: List[str], learner_capabilities: Set[str]
    ) -> List[str]:
        """
        模仿学习

        返回：可执行的模仿行为序列
        """
        if model_agent_id not in self.role_models:
            # 默认可以模仿
            pass

        # 过滤掉学习者不具备能力的行为
        imitable_behaviors = []
        for behavior in behavior_pattern:
            # 简化：假设所有行为都可模仿
            imitable_behaviors.append(behavior)

        return imitable_behaviors

    def learn_social_norm(
        self, context: str, behaviors: List[str], sanctions: Dict[str, str]
    ) -> None:
        """
        学习社会规范

        sanctions: 行为 -> 制裁（奖励或惩罚）
        """
        norm = {
            "context": context,
            "prescribed_behaviors": [],
            "prohibited_behaviors": [],
            "sanctions": sanctions,
        }

        for behavior, sanction in sanctions.items():
            if "reward" in sanction.lower() or "praise" in sanction.lower():
                norm["prescribed_behaviors"].append(behavior)
            elif "punish" in sanction.lower() or "penalty" in sanction.lower():
                norm["prohibited_behaviors"].append(behavior)

        self.social_norms[context] = norm

    def check_norm_compliance(self, behavior: str, context: str) -> Dict[str, Any]:
        """检查行为是否符合社会规范"""
        if context not in self.social_norms:
            return {"compliant": True, "reason": "No norms defined for this context"}

        norm = self.social_norms[context]

        if behavior in norm["prohibited_behaviors"]:
            return {
                "compliant": False,
                "violation_type": "prohibited",
                "expected_sanction": norm["sanctions"].get(behavior, "unknown"),
            }

        if behavior in norm["prescribed_behaviors"]:
            return {
                "compliant": True,
                "conformity_type": "prescribed",
                "expected_reward": norm["sanctions"].get(behavior, "unknown"),
            }

        return {"compliant": True, "reason": "Behavior not regulated by norms"}

    def set_role_model(self, agent_id: str, influence: float) -> None:
        """设置榜样及其影响力"""
        self.role_models[agent_id] = min(max(influence, 0.0), 1.0)


# ==================== 社会网络模型 ====================


class SocialNetworkModel:
    """
    社会网络模型：建模智能体之间的社会关系

    支持：
    - 关系类型（朋友、敌人、中立等）
    - 关系强度
    - 信任度
    - 影响力传播
    """

    def __init__(self):
        self.agents: Set[str] = set()
        self.relationships: Dict[Tuple[str, str], Dict[str, float]] = {}
        self.trust_network: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.influence_graph: Dict[str, List[str]] = defaultdict(list)

    def add_agent(self, agent_id: str) -> None:
        """添加智能体"""
        self.agents.add(agent_id)

    def establish_relationship(
        self,
        agent1: str,
        agent2: str,
        relationship_type: str,
        strength: float = 0.5,
        trust: float = 0.5,
    ) -> None:
        """建立关系"""
        self.agents.add(agent1)
        self.agents.add(agent2)

        key = (agent1, agent2)
        self.relationships[key] = {
            "type": relationship_type,
            "strength": min(max(strength, 0.0), 1.0),
            "trust": min(max(trust, 0.0), 1.0),
        }

        # 更新信任网络
        self.trust_network[agent1][agent2] = min(max(trust, 0.0), 1.0)

    def update_trust(self, agent1: str, agent2: str, experience: str, delta: float) -> None:
        """根据经验更新信任度"""
        if (agent1, agent2) not in self.relationships:
            return

        current_trust = self.relationships[(agent1, agent2)]["trust"]

        # 积极经验增加信任，消极经验减少信任
        if "positive" in experience.lower() or "helpful" in experience.lower():
            new_trust = current_trust + delta * (1 - current_trust)
        elif "negative" in experience.lower() or "harmful" in experience.lower():
            new_trust = current_trust - delta * current_trust
        else:
            new_trust = current_trust

        new_trust = min(max(new_trust, 0.0), 1.0)
        self.relationships[(agent1, agent2)]["trust"] = new_trust
        self.trust_network[agent1][agent2] = new_trust

    def get_relationship(self, agent1: str, agent2: str) -> Optional[Dict[str, Any]]:
        """获取两个智能体之间的关系"""
        key = (agent1, agent2)
        if key in self.relationships:
            return self.relationships[key]
        return None

    def get_trust_level(self, agent1: str, agent2: str) -> float:
        """获取信任级别"""
        if agent1 in self.trust_network and agent2 in self.trust_network[agent1]:
            return self.trust_network[agent1][agent2]
        return 0.5  # 默认中等信任

    def find_influencers(self, agent_id: str, max_depth: int = 2) -> List[str]:
        """找出对某智能体有影响力的其他智能体"""
        influencers = []

        # 一度关系
        for (a1, a2), rel in self.relationships.items():
            if a2 == agent_id and rel["strength"] > 0.6:
                influencers.append(a1)

        # 二度关系（简化）
        if max_depth >= 2:
            for influencer in influencers[:]:
                for (a1, a2), rel in self.relationships.items():
                    if a2 == influencer and rel["strength"] > 0.6:
                        if a1 not in influencers:
                            influencers.append(a1)

        return influencers

    def propagate_belief(
        self, source_agent: str, belief: str, initial_strength: float
    ) -> Dict[str, float]:
        """
        信念在网络中的传播

        返回：各智能体接收到的信念强度
        """
        propagation_result = {source_agent: initial_strength}
        visited = {source_agent}
        queue = [(source_agent, initial_strength)]

        while queue:
            current_agent, current_strength = queue.pop(0)

            # 找到当前智能体的邻居
            neighbors = []
            for (a1, a2), rel in self.relationships.items():
                if a1 == current_agent and a2 not in visited:
                    neighbors.append((a2, rel["trust"]))
                elif a2 == current_agent and a1 not in visited:
                    neighbors.append((a1, rel["trust"]))

            for neighbor, trust in neighbors:
                # 信念强度随信任度衰减
                received_strength = current_strength * trust * 0.8
                if received_strength > 0.1:  # 阈值
                    propagation_result[neighbor] = received_strength
                    visited.add(neighbor)
                    queue.append((neighbor, received_strength))

        return propagation_result

    def detect_communities(self) -> List[Set[str]]:
        """检测社区（简化实现：基于强关系聚类）"""
        communities = []
        assigned = set()

        for agent in self.agents:
            if agent in assigned:
                continue

            # 从该智能体开始构建社区
            community = {agent}
            queue = [agent]

            while queue:
                current = queue.pop(0)

                for (a1, a2), rel in self.relationships.items():
                    if rel["strength"] < 0.5:
                        continue

                    if a1 == current and a2 not in assigned:
                        community.add(a2)
                        assigned.add(a2)
                        queue.append(a2)
                    elif a2 == current and a1 not in assigned:
                        community.add(a1)
                        assigned.add(a1)
                        queue.append(a1)

            if len(community) > 1:
                communities.append(community)
            else:
                assigned.add(agent)

        return communities


# ==================== 主接口类 ====================


class SocialCognitionEngine:
    """
    社会认知引擎：整合所有社会认知能力

    提供统一接口用于：
    - 心智理论推理
    - 共情
    - 意图识别
    - 欺骗检测
    - 社会学习
    - 社会网络分析
    """

    def __init__(self):
        self.tom_engine = TheoryOfMindEngine()
        self.empathy_module = EmpathyModule()
        self.intention_recognizer = IntentionRecognizer()
        self.deception_detector = DeceptionDetector()
        self.social_learning = SocialLearningEngine()
        self.social_network = SocialNetworkModel()

    def register_agent(
        self, agent_id: str, initial_beliefs: List[str] = None, initial_desires: List[str] = None
    ) -> MentalState:
        """注册智能体并返回其心智状态"""
        mental_state = MentalState(agent_id=agent_id)

        if initial_beliefs:
            for belief in initial_beliefs:
                mental_state.add_belief(belief)

        if initial_desires:
            for desire in initial_desires:
                mental_state.add_desire(desire)

        self.tom_engine.register_agent(agent_id, mental_state)
        self.social_network.add_agent(agent_id)

        return mental_state

    def establish_relationship(
        self,
        agent1: str,
        agent2: str,
        relationship_type: str,
        strength: float = 0.5,
        trust: float = 0.5,
    ) -> None:
        """建立智能体间关系"""
        self.social_network.establish_relationship(
            agent1, agent2, relationship_type, strength, trust
        )

        # 根据关系类型设置共情水平
        empathy_levels = {
            "family": 0.9,
            "friend": 0.8,
            "colleague": 0.6,
            "stranger": 0.4,
            "rival": 0.2,
            "enemy": 0.1,
        }

        level = empathy_levels.get(relationship_type, 0.4)
        self.empathy_module.set_empathy_level(agent2, level)

    def understand_other(self, observer_id: str, target_id: str, situation: str) -> Dict[str, Any]:
        """
        理解他人：综合心智理论和共情

        返回对目标智能体的全面理解
        """
        # 心智理论推断
        perspective = self.tom_engine.perspective_taking(target_id, situation)

        # 共情推断
        target_state = self.tom_engine.agent_models.get(target_id)
        if target_state:
            emotional_understanding = self.empathy_module.cognitive_empathy(target_state, situation)
            empathic_concerns = self.empathy_module.empathic_concern(target_state)
        else:
            emotional_understanding = {}
            empathic_concerns = []

        return {
            "perspective": perspective,
            "emotional_state": emotional_understanding,
            "empathic_concerns": empathic_concerns,
            "relationship": self.social_network.get_relationship(observer_id, target_id),
        }

    def interpret_action(
        self, agent_id: str, action: str, context: str, utterance: str = None
    ) -> Dict[str, Any]:
        """
        解释行动：识别意图并检测欺骗

        返回行动的全面解释
        """
        # 意图识别
        intention_result = self.intention_recognizer.recognize_combined(
            utterance=utterance, actions=[action], context=context
        )

        # 欺骗检测（如果有言语）
        deception_result = None
        if utterance:
            deception_result = self.deception_detector.detect_deception(
                statement=utterance, context=context, agent_id=agent_id
            )

        # 更新心智模型
        self.tom_engine.update_agent_model(agent_id, f"{action}: {utterance or ''}", action)

        return {
            "intention": intention_result,
            "deception_analysis": deception_result,
            "updated_beliefs": self.tom_engine.agent_models.get(agent_id),
        }

    def learn_from_interaction(
        self, learner_id: str, model_id: str, behavior: str, outcome: str, context: str
    ) -> Optional[str]:
        """
        从社会互动中学习

        返回学习到的策略
        """
        # 记录观察
        self.social_learning.observe_behavior(model_id, behavior, outcome, context)

        # 学习
        learner_state = self.tom_engine.agent_models.get(learner_id)
        if learner_state:
            return self.social_learning.learn_from_observation(learner_state, behavior)

        return None

    def predict_emotional_reaction(self, agent_id: str, event: str) -> List[Emotion]:
        """预测智能体对某事件的情绪反应"""
        agent_state = self.tom_engine.agent_models.get(agent_id)
        if not agent_state:
            return []

        return self.empathy_module.simulate_emotional_impact(event, agent_state)

    def analyze_social_dynamics(self) -> Dict[str, Any]:
        """分析整体社会动态"""
        communities = self.social_network.detect_communities()

        return {
            "total_agents": len(self.social_network.agents),
            "total_relationships": len(self.social_network.relationships),
            "communities": [list(c) for c in communities],
            "community_count": len(communities),
            "average_trust": self._calculate_average_trust(),
        }

    def _calculate_average_trust(self) -> float:
        """计算平均信任度"""
        if not self.social_network.relationships:
            return 0.5

        total_trust = sum(rel["trust"] for rel in self.social_network.relationships.values())
        return total_trust / len(self.social_network.relationships)


# ==================== 工具函数 ====================


def create_simple_scenario() -> SocialCognitionEngine:
    """创建一个简单的社会认知场景用于演示"""
    engine = SocialCognitionEngine()

    # 创建智能体
    alice = engine.register_agent(
        "Alice",
        initial_beliefs=["The cake is in the cupboard", "Bob is friendly"],
        initial_desires=["Eat the cake", "Make friends"],
    )

    bob = engine.register_agent(
        "Bob",
        initial_beliefs=["The cake is on the table", "Alice likes cake"],
        initial_desires=["Surprise Alice", "Share food"],
    )

    # 建立关系
    engine.establish_relationship("Alice", "Bob", "friend", strength=0.8, trust=0.7)
    engine.establish_relationship("Bob", "Alice", "friend", strength=0.8, trust=0.7)

    return engine


if __name__ == "__main__":
    # 简单演示
    engine = create_simple_scenario()

    print("=== 社会认知引擎演示 ===\n")

    # 理解他人
    understanding = engine.understand_other("Alice", "Bob", "Bob is looking at the cake")
    print(f"Alice 对 Bob 的理解: {understanding['emotional_state']}\n")

    # 解释行动
    interpretation = engine.interpret_action(
        "Bob", "gives cake to Alice", "friendly gathering", "Here, I got this for you!"
    )
    print(f"Bob 的行动解释: {interpretation['intention']['primary_intention']}\n")

    # 预测情绪反应
    emotions = engine.predict_emotional_reaction("Alice", "receives a gift")
    print(f"Alice 的情绪反应: {[e.emotion_type.name for e in emotions]}\n")

    # 社会动态分析
    dynamics = engine.analyze_social_dynamics()
    print(f"社会动态: {dynamics['total_agents']} 个智能体，{dynamics['community_count']} 个社群")
