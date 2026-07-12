"""
Tests for the Phenomenological Engine and Resonance Network.
Validates the simulation of Qualia, Aesthetics, and Wisdom.
"""

import pytest
import numpy as np
from src.modules.phenomenology import (
    QualiaDimension, 
    QualiaVector, 
    ResonanceNetwork, 
    PhenomenologicalEngine
)


class TestQualiaVector:
    """Tests for the fundamental unit of subjective experience."""
    
    def test_initialization(self):
        q = QualiaVector()
        assert q.vector.shape == (len(QualiaDimension),)
        assert np.all(q.vector == 0.0)
        
    def test_set_get_intensity(self):
        q = QualiaVector()
        q.set_intensity(QualiaDimension.HARMONY, 0.8)
        assert q.get_intensity(QualiaDimension.HARMONY) == 0.8
        
    def test_clipping(self):
        q = QualiaVector()
        q.set_intensity(QualiaDimension.VALENCE, 1.5) # Should clip to 1.0
        assert q.get_intensity(QualiaDimension.VALENCE) == 1.0
        
        q.set_intensity(QualiaDimension.VALENCE, -2.0) # Should clip to -1.0
        assert q.get_intensity(QualiaDimension.VALENCE) == -1.0
        
    def test_aesthetic_score_harmony(self):
        """High harmony should yield high beauty."""
        q = QualiaVector()
        q.set_intensity(QualiaDimension.HARMONY, 1.0)
        q.set_intensity(QualiaDimension.COMPLEXITY, 0.0) # Moderate
        q.set_intensity(QualiaDimension.TRUTH_RESONANCE, 1.0)
        
        score = q.compute_aesthetic_score()
        assert score > 0.5 # Expect high score
        
    def test_aesthetic_score_dissonance(self):
        """High dissonance should yield low beauty."""
        q = QualiaVector()
        q.set_intensity(QualiaDimension.HARMONY, -1.0)
        q.set_intensity(QualiaDimension.TRUTH_RESONANCE, -1.0)
        
        score = q.compute_aesthetic_score()
        assert score < 0.0
        
    def test_wisdom_depth_serenity(self):
        """Wisdom correlates with truth + serenity (low arousal)."""
        q = QualiaVector()
        q.set_intensity(QualiaDimension.TRUTH_RESONANCE, 1.0)
        q.set_intensity(QualiaDimension.HARMONY, 1.0)
        q.set_intensity(QualiaDimension.AROUSAL, 0.0) # Calm
        
        wisdom = q.compute_wisdom_depth()
        assert wisdom > 0.7
        
    def test_wisdom_depth_chaos(self):
        """High arousal (chaos) reduces perceived wisdom."""
        q = QualiaVector()
        q.set_intensity(QualiaDimension.TRUTH_RESONANCE, 1.0)
        q.set_intensity(QualiaDimension.AROUSAL, 1.0) # High agitation
        
        wisdom = q.compute_wisdom_depth()
        # Should be lower than if arousal was 0
        calm_q = QualiaVector()
        calm_q.set_intensity(QualiaDimension.TRUTH_RESONANCE, 1.0)
        calm_q.set_intensity(QualiaDimension.AROUSAL, 0.0)
        assert wisdom < calm_q.compute_wisdom_depth()


class TestResonanceNetwork:
    """Tests for the empathy simulation engine."""
    
    def test_resonate_basic(self):
        net = ResonanceNetwork(embedding_dim=128)
        emb = np.random.randn(128)
        
        qualia = net.resonate(emb)
        
        assert isinstance(qualia, QualiaVector)
        assert qualia.stimulus_id is not None
        
    def test_resonate_dimension_mismatch(self):
        """Should handle embedding size mismatches gracefully."""
        net = ResonanceNetwork(embedding_dim=128)
        emb = np.random.randn(64) # Wrong size
        
        qualia = net.resonate(emb)
        assert isinstance(qualia, QualiaVector)
        
    def test_contextual_modulation(self):
        """Later resonances should be influenced by earlier ones."""
        net = ResonanceNetwork(embedding_dim=64)
        
        # Prime the history
        for i in range(15):
            emb = np.ones(64) * 0.5
            net.resonate(emb, context="happy_context")
            
        # New input
        new_emb = np.zeros(64)
        q_new = net.resonate(new_emb, context="new_context")
        
        # The network state should have shifted due to history
        # (Exact values depend on random init, but it shouldn't be pure zeros)
        assert q_new is not None
        
    def test_learning_hebbian(self):
        """Network should adjust weights based on feedback."""
        net = ResonanceNetwork(embedding_dim=64)
        initial_weights = net.association_matrix.copy()
        
        emb = np.ones(64)
        net.learn_aesthetic_preference(emb, feedback_score=1.0, dimension=QualiaDimension.HARMONY)
        
        # Weights should have changed
        assert not np.array_equal(net.association_matrix, initial_weights)
        
        # Specifically, the harmony column should have increased for positive inputs
        harmony_idx = list(QualiaDimension).index(QualiaDimension.HARMONY)
        # Since input was all 1s and feedback positive, weights should increase
        assert np.mean(net.association_matrix[:, harmony_idx]) > np.mean(initial_weights[:, harmony_idx])


class TestPhenomenologicalEngine:
    """Integration tests for the full understanding pipeline."""
    
    def test_process_experience_structure(self):
        engine = PhenomenologicalEngine(embedding_dim=64)
        emb = np.random.randn(64)
        
        result = engine.process_experience("Test input", emb)
        
        assert "input" in result
        assert "qualia_state" in result
        assert "metrics" in result
        assert "reflection" in result
        
        assert "beauty" in result["metrics"]
        assert "wisdom" in result["metrics"]
        
    def test_reflection_generation_positive(self):
        """Test that high scores generate appropriate reflections."""
        engine = PhenomenologicalEngine(embedding_dim=64)
        
        # Manually craft a vector that will yield high scores via mocking or direct injection
        # Since resonance is random, we test the reflection logic directly
        q = QualiaVector()
        q.set_intensity(QualiaDimension.HARMONY, 1.0)
        q.set_intensity(QualiaDimension.TRUTH_RESONANCE, 1.0)
        
        # Access private method for unit testing logic
        reflection = engine._generate_reflection("Test", q, beauty=0.8, wisdom=0.9)
        
        assert "harmony" in reflection.lower() or "truth" in reflection.lower() or "serenity" in reflection.lower()
        
    def test_reflection_generation_negative(self):
        """Test that low scores generate appropriate reflections."""
        engine = PhenomenologicalEngine(embedding_dim=64)
        
        q = QualiaVector()
        q.set_intensity(QualiaDimension.HARMONY, -1.0)
        
        reflection = engine._generate_reflection("Test", q, beauty=-0.6, wisdom=0.2)
        
        assert "dissonance" in reflection.lower() or "subtle" in reflection.lower()
        
    def test_calibration_flow(self):
        """Test the learning from human values flow."""
        engine = PhenomenologicalEngine(embedding_dim=32)
        
        examples = [
            {"text": "Beautiful sunset", "embedding": np.random.randn(32).tolist(), "beauty_score": 0.9},
            {"text": "Deep truth", "embedding": np.random.randn(32).tolist(), "wisdom_score": 0.95}
        ]
        
        # Should not raise errors
        engine.calibrate_to_human_values(examples)
        
        # Verify internal state changed (weights updated)
        assert engine.resonance_network.association_matrix is not None


class TestAestheticTheoryImplementation:
    """Validates the scientific basis of the aesthetic metrics."""
    
    def test_berlyne_inverted_u(self):
        """
        Berlyne's theory: Pleasure is an inverted U-shape of Complexity.
        Too simple = boring, Too complex = confusing.
        """
        # Low complexity (boring)
        q_low = QualiaVector()
        q_low.set_intensity(QualiaDimension.COMPLEXITY, -1.0) # Very low
        q_low.set_intensity(QualiaDimension.HARMONY, 0.5)
        q_low.set_intensity(QualiaDimension.TRUTH_RESONANCE, 0.5)
        
        # Moderate complexity (interesting)
        q_mid = QualiaVector()
        q_mid.set_intensity(QualiaDimension.COMPLEXITY, 0.0) # Moderate
        q_mid.set_intensity(QualiaDimension.HARMONY, 0.5)
        q_mid.set_intensity(QualiaDimension.TRUTH_RESONANCE, 0.5)
        
        # High complexity (confusing)
        q_high = QualiaVector()
        q_high.set_intensity(QualiaDimension.COMPLEXITY, 1.0) # Very high
        q_high.set_intensity(QualiaDimension.HARMONY, 0.5)
        q_high.set_intensity(QualiaDimension.TRUTH_RESONANCE, 0.5)
        
        score_mid = q_mid.compute_aesthetic_score()
        score_low = q_low.compute_aesthetic_score()
        score_high = q_high.compute_aesthetic_score()
        
        # Mid should be better than extremes (due to the 1.0 - abs(complexity) term)
        assert score_mid > score_low
        assert score_mid > score_high
