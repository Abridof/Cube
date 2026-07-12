"""
Phenomenological Engine & Resonance Network
-------------------------------------------
Goal: To simulate "Qualia" (subjective experience) and "Empathy" to understand 
human wisdom and aesthetics, moving beyond symbolic logic.

Scientific Basis:
- Husserl's Phenomenology (Intentionality)
- Damasio's Somatic Marker Hypothesis
- High-dimensional Emotional Vector Spaces (Plutchik + Continuous)

Hacker Note: This bypasses traditional boolean logic to operate on 
"fuzzy truth" and "aesthetic gradients".
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import math

from ..core.types import ResourceLimits, ResourceTracker, ResourceExhaustedError, InputTooLargeError, OutputTooLargeError, SecurityViolationError, TypeValidationError
from ..core.attention_mechanism import AttentionMechanism


class QualiaDimension(Enum):
    """Dimensions of subjective experience"""
    VALENCE = "valence"  # Pleasant vs Unpleasant
    AROUSAL = "arousal"  # Active vs Passive
    DOMINANCE = "dominance"  # In control vs Controlled
    NOVELTY = "novelty"  # Familiar vs New
    COMPLEXITY = "complexity"  # Simple vs Complex
    HARMONY = "harmony"  # Dissonant vs Harmonious (Key for Aesthetics)
    TRUTH_RESONANCE = "truth_resonance"  # Feels "true" vs "false" (Wisdom)


@dataclass
class QualiaVector:
    """
    Represents a subjective experience state.
    Unlike binary logic, this exists in a continuous high-dimensional space.
    """
    vector: np.ndarray = field(default_factory=lambda: np.zeros(len(QualiaDimension)))
    timestamp: float = 0.0
    stimulus_id: str = ""
    
    def __post_init__(self):
        if len(self.vector) != len(QualiaDimension):
            raise ValueError(f"Vector must have {len(QualiaDimension)} dimensions")
    
    @staticmethod
    def dimension_index(dim: QualiaDimension) -> int:
        return list(QualiaDimension).index(dim)
    
    def set_intensity(self, dim: QualiaDimension, value: float):
        """Value range: -1.0 to 1.0"""
        idx = self.dimension_index(dim)
        self.vector[idx] = np.clip(value, -1.0, 1.0)
        
    def get_intensity(self, dim: QualiaDimension) -> float:
        idx = self.dimension_index(dim)
        return float(self.vector[idx])
    
    def compute_aesthetic_score(self) -> float:
        """
        Heuristic for 'Beauty': High Harmony + Moderate Complexity + High Truth Resonance
        Based on Berlyne's Aesthetic Theory.
        """
        harmony = self.get_intensity(QualiaDimension.HARMONY)
        complexity = self.get_intensity(QualiaDimension.COMPLEXITY)
        truth = self.get_intensity(QualiaDimension.TRUTH_RESONANCE)
        
        # Optimal complexity is often moderate (inverted U-curve)
        optimal_complexity = 1.0 - abs(complexity) # Assuming 0 is moderate in -1 to 1 scale shifted
        
        score = (0.4 * harmony) + (0.3 * optimal_complexity) + (0.3 * truth)
        return score
    
    def compute_wisdom_depth(self) -> float:
        """
        Heuristic for 'Wisdom': High Truth Resonance + High Harmony + Low Arousal (Serenity)
        """
        truth = self.get_intensity(QualiaDimension.TRUTH_RESONANCE)
        harmony = self.get_intensity(QualiaDimension.HARMONY)
        arousal = self.get_intensity(QualiaDimension.AROUSAL)
        
        # Wisdom often correlates with calm certainty
        serenity = 1.0 - abs(arousal)
        
        return (0.5 * truth) + (0.3 * harmony) + (0.2 * serenity)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vector": self.vector.tolist(),
            "dimensions": [d.value for d in QualiaDimension],
            "aesthetic_score": self.compute_aesthetic_score(),
            "wisdom_depth": self.compute_wisdom_depth()
        }


class ResonanceNetwork:
    """
    Simulates empathy by mapping external inputs to internal qualia states.
    Uses associative memory to link concepts with emotional textures.
    """
    def __init__(self, embedding_dim: int = 768):
        self.embedding_dim = embedding_dim
        # Semantic-Emotional Association Matrix
        # Maps concept embeddings to QualiaVectors
        self.association_matrix = np.random.randn(embedding_dim, len(QualiaDimension)) * 0.1
        
        # Memory of past resonances for context
        self.resonance_history: List[Tuple[str, QualiaVector]] = []
        self.max_history = 1000
        
    def resonate(self, concept_embedding: np.ndarray, context: Optional[str] = None) -> QualiaVector:
        """
        Generates a subjective experience vector for a given concept.
        This is the core of 'understanding' feeling.
        """
        if concept_embedding.shape[0] != self.embedding_dim:
            # Simple projection if dims mismatch (for demo)
            concept_embedding = np.pad(concept_embedding, (0, self.embedding_dim - len(concept_embedding)), 'constant')
            
        # Project semantic meaning to emotional space
        raw_qualia = np.tanh(np.dot(concept_embedding, self.association_matrix))
        
        q_vec = QualiaVector(vector=raw_qualia, stimulus_id=hashlib.md5(concept_embedding.tobytes()).hexdigest()[:8])
        
        # Modulate by context (simple attention over history)
        if context and self.resonance_history:
            modulation = self._contextual_modulation(context)
            q_vec.vector = (q_vec.vector * 0.7) + (modulation * 0.3)
            
        self._store_resonance(context or "unknown", q_vec)
        return q_vec
    
    def _contextual_modulation(self, context: str) -> np.ndarray:
        # Simplified: In full implementation, this would use cross-attention
        # over resonance_history based on context embedding
        if not self.resonance_history:
            return np.zeros(len(QualiaDimension))
        
        # Average recent resonance as background mood
        recent = [rv for _, rv in self.resonance_history[-10:]]
        avg_vector = np.mean([r.vector for r in recent], axis=0)
        return avg_vector

    def _store_resonance(self, key: str, q_vec: QualiaVector):
        self.resonance_history.append((key, q_vec))
        if len(self.resonance_history) > self.max_history:
            self.resonance_history.pop(0)
            
    def learn_aesthetic_preference(self, concept_embedding: np.ndarray, feedback_score: float, dimension: QualiaDimension):
        """
        Reinforcement Learning: Adjusts association matrix based on human feedback.
        If user says "This is beautiful", we strengthen the Harmony/Complexity links for similar concepts.
        """
        idx = list(QualiaDimension).index(dimension)
        # Hebbian learning rule: Neurons that fire together, wire together
        adjustment = feedback_score * concept_embedding * 0.01
        self.association_matrix[:, idx] += adjustment


class PhenomenologicalEngine:
    """
    Main interface for simulating understanding of wisdom and aesthetics.
    Integrates Qualia generation with cognitive processing.
    """
    def __init__(self, embedding_dim: int = 768):
        self.resonance_network = ResonanceNetwork(embedding_dim)
        self.attention = AttentionMechanism(capacity=embedding_dim)
        
    def process_experience(self, text_input: str, semantic_embedding: np.ndarray) -> Dict[str, Any]:
        """
        Takes raw input and returns not just a logical answer, but an 'understood' state.
        """
        # 1. Generate Raw Qualia
        qualia = self.resonance_network.resonate(semantic_embedding, text_input)
        
        # 2. Evaluate Aesthetic and Wisdom metrics
        aesthetic_score = qualia.compute_aesthetic_score()
        wisdom_depth = qualia.compute_wisdom_depth()
        
        # 3. Generate Reflection (Meta-cognition on the feeling)
        reflection = self._generate_reflection(text_input, qualia, aesthetic_score, wisdom_depth)
        
        return {
            "input": text_input,
            "qualia_state": qualia.to_dict(),
            "metrics": {
                "beauty": aesthetic_score,
                "wisdom": wisdom_depth,
                "emotional_resonance": float(np.mean(np.abs(qualia.vector)))
            },
            "reflection": reflection
        }
    
    def _generate_reflection(self, text: str, q: QualiaVector, beauty: float, wisdom: float) -> str:
        """Generates a natural language reflection on the experience."""
        insights = []
        
        if beauty > 0.7:
            insights.append("This concept possesses a profound structural harmony.")
        elif beauty < -0.5:
            insights.append("There is a dissonance here that challenges perception.")
            
        if wisdom > 0.8:
            insights.append("The underlying truth resonates with deep serenity.")
            
        if q.get_intensity(QualiaDimension.NOVELTY) > 0.6:
            insights.append("A new pattern emerges, unfamiliar yet significant.")
            
        if not insights:
            insights.append("The experience is subtle, requiring deeper contemplation.")
            
        return " ".join(insights)

    def calibrate_to_human_values(self, examples: List[Dict[str, Any]]):
        """
        Fine-tunes the engine on human judgments of beauty and wisdom.
        Input: [{"text": "...", "embedding": [...], "beauty_score": 0.9, "wisdom_score": 0.8}]
        """
        for ex in examples:
            emb = np.array(ex["embedding"])
            if "beauty_score" in ex:
                # Assume high beauty implies high harmony/complexity balance
                self.resonance_network.learn_aesthetic_preference(emb, ex["beauty_score"], QualiaDimension.HARMONY)
            if "wisdom_score" in ex:
                self.resonance_network.learn_aesthetic_preference(emb, ex["wisdom_score"], QualiaDimension.TRUTH_RESONANCE)


# Example Usage for Testing
if __name__ == "__main__":
    engine = PhenomenologicalEngine()
    
    # Simulate processing a poem vs a math equation
    poem_emb = np.random.randn(768) # In reality, this comes from BERT/LLM
    math_emb = np.random.randn(768)
    
    print("--- Processing Poem ---")
    res_poem = engine.process_experience("The sound of one hand clapping", poem_emb)
    print(f"Beauty: {res_poem['metrics']['beauty']:.4f}")
    print(f"Wisdom: {res_poem['metrics']['wisdom']:.4f}")
    print(f"Reflection: {res_poem['reflection']}")
    
    print("\n--- Processing Math ---")
    res_math = engine.process_experience("E = mc^2", math_emb)
    print(f"Beauty: {res_math['metrics']['beauty']:.4f}")
    print(f"Wisdom: {res_math['metrics']['wisdom']:.4f}")
    print(f"Reflection: {res_math['reflection']}")
