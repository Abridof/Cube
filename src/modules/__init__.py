"""
认知模块包 - 核心 AI 能力模块
================================

包含:
- UCR Layer: 统一认知表示层
- Knowledge Graph: 知识图谱与元学习
- Multimodal Perception: 多模态感知
- World Model: 世界模型与自主性
- Cognition Engine: 通用认知引擎
- Cognitive Loop: 认知闭环控制器
- Self Reflection: 自反思模块
- Embodied Environment: 具身环境
- Neural Backend: 神经语义后端
"""

from .ucr_layer import (
    CognitiveUnit,
    SymbolicNode,
    VectorEmbedding,
    EntityType,
    RepresentationType,
    UnifiedRepresentationEngine,
)

from .knowledge_graph import (
    KnowledgeGraph,
    KnowledgeEdge,
    RelationType,
    LearningStrategy,
    Hypothesis,
    HybridRetriever,
    EnhancedMemoryBank,
)

from .multimodal_perception import (
    MultimodalFusionEngine,
    PerceivedObject,
    ModalFeature,
    ModalityType,
    FeatureType,
)

from .world_model import (
    WorldModel,
    State,
    StateVariable,
    StateType,
    Transition,
    Prediction,
    Counterfactual,
)

from .cognition_engine import (
    CognitionEngine,
    MemoryBank,
    KnowledgeNode,
    CognitiveState,
)

from .cognitive_loop import (
    CognitiveLoopController,
    LoopPhase,
    CognitiveEvent,
)

from .self_reflection import (
    CodeParser,
    LimitationAnalyzer,
    SelfReflector,
    CodeSmell,
    LimitationType,
)

from .embodied_environment import (
    ContinuousPhysicsEngine,
    EmbodiedAgent,
    MultiAgentSociety,
    GameObject,
    Vector2D,
)

from .neural_backend import (
    NeuralUCREncoder,
    DataManager,
    IntrinsicMotivation,
    Tensor,
)

__all__ = [
    # UCR Layer
    'CognitiveUnit',
    'SymbolicNode',
    'VectorEmbedding',
    'EntityType',
    'RepresentationType',
    'UnifiedRepresentationEngine',
    
    # Knowledge Graph
    'KnowledgeGraph',
    'KnowledgeEdge',
    'RelationType',
    'LearningStrategy',
    'Hypothesis',
    'HybridRetriever',
    'EnhancedMemoryBank',
    
    # Multimodal Perception
    'MultimodalFusionEngine',
    'PerceivedObject',
    'ModalFeature',
    'ModalityType',
    'FeatureType',
    
    # World Model
    'WorldModel',
    'State',
    'StateVariable',
    'StateType',
    'Transition',
    'Prediction',
    'Counterfactual',
    
    # Cognition Engine
    'CognitionEngine',
    'MemoryBank',
    'KnowledgeNode',
    'CognitiveState',
    
    # Cognitive Loop
    'CognitiveLoopController',
    'LoopPhase',
    'CognitiveEvent',
    
    # Self Reflection
    'CodeParser',
    'LimitationAnalyzer',
    'SelfReflector',
    'CodeSmell',
    'LimitationType',
    
    # Embodied Environment
    'ContinuousPhysicsEngine',
    'EmbodiedAgent',
    'MultiAgentSociety',
    'GameObject',
    'Vector2D',
    
    # Neural Backend
    'NeuralUCREncoder',
    'DataManager',
    'IntrinsicMotivation',
    'Tensor',
]