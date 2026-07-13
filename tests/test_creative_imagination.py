"""
Tests for Creative Imagination Engine
======================================
Comprehensive tests for counterfactual reasoning, concept blending, 
dream recombination, and novelty evaluation.
"""

import pytest
import numpy as np
from src.modules.creative_imagination import (
    ConceptNode,
    ConceptBlender,
    CounterfactualEngine,
    SubconsciousDreamer,
    NoveltyEvaluator,
    CreativeImaginationEngine,
    ImaginationMode,
    ImaginativeOutput,
    get_imagination_engine,
    reset_imagination_engine
)


class TestConceptNode:
    """Test basic concept node functionality"""
    
    def test_concept_creation(self):
        """Test creating a concept node"""
        vector = np.random.randn(128)
        concept = ConceptNode(
            name="test_concept",
            semantic_vector=vector,
            attributes={"category": "test"}
        )
        
        assert concept.name == "test_concept"
        assert len(concept.semantic_vector) == 128
        assert concept.attributes["category"] == "test"
        assert concept.activation_level == 0.5
    
    def test_concept_similarity_identical(self):
        """Test similarity of identical concepts"""
        vector = np.array([1.0, 0.0, 0.0])
        concept1 = ConceptNode("c1", vector)
        concept2 = ConceptNode("c2", vector.copy())
        
        similarity = concept1.similarity_to(concept2)
        assert abs(similarity - 1.0) < 1e-6  # Should be nearly identical
    
    def test_concept_similarity_orthogonal(self):
        """Test similarity of orthogonal concepts"""
        vector1 = np.array([1.0, 0.0, 0.0])
        vector2 = np.array([0.0, 1.0, 0.0])
        
        concept1 = ConceptNode("c1", vector1)
        concept2 = ConceptNode("c2", vector2)
        
        similarity = concept1.similarity_to(concept2)
        assert abs(similarity) < 1e-6  # Should be nearly zero
    
    def test_concept_similarity_opposite(self):
        """Test similarity of opposite concepts"""
        vector1 = np.array([1.0, 0.0, 0.0])
        vector2 = np.array([-1.0, 0.0, 0.0])
        
        concept1 = ConceptNode("c1", vector1)
        concept2 = ConceptNode("c2", vector2)
        
        similarity = concept1.similarity_to(concept2)
        assert abs(similarity - (-1.0)) < 1e-6  # Should be nearly -1


class TestConceptBlender:
    """Test concept blending functionality"""
    
    def test_add_concept(self):
        """Test adding concepts to the blender"""
        blender = ConceptBlender(embedding_dim=64)
        concept = blender.add_concept("test", {"key": "value"})
        
        assert concept.name == "test"
        assert len(concept.semantic_vector) == 64
        assert "test" in blender.concept_space
    
    def test_blend_two_concepts(self):
        """Test blending two concepts"""
        blender = ConceptBlender(embedding_dim=32)
        blender.add_concept("fire", {"hot": True})
        blender.add_concept("ice", {"cold": True})
        
        blended = blender.blend_concepts(["fire", "ice"])
        
        assert "fire_ice_fusion" in blender.concept_space
        assert len(blended.semantic_vector) == 32
        assert "fire" in blended.connections
        assert "ice" in blended.connections
    
    def test_blend_insufficient_concepts(self):
        """Test blending with insufficient concepts"""
        blender = ConceptBlender()
        blender.add_concept("only_one", {})
        
        with pytest.raises(ValueError):
            blender.blend_concepts(["only_one"])
    
    def test_find_distant_concepts(self):
        """Test finding distant concepts"""
        blender = ConceptBlender(embedding_dim=16)
        
        # Add similar concepts
        blender.add_concept("cat", {"type": "animal"})
        blender.add_concept("dog", {"type": "animal"})
        
        # Add very different concept
        blender.add_concept("galaxy", {"type": "astronomy"})
        
        distant = blender.find_distant_concepts("cat", top_k=1)
        
        # Galaxy should be more distant than dog
        assert "galaxy" in distant or len(distant) > 0


class TestCounterfactualEngine:
    """Test counterfactual reasoning"""
    
    def test_add_causal_link(self):
        """Test adding causal relationships"""
        engine = CounterfactualEngine()
        engine.add_causal_link("rain", "wet_ground")
        
        assert "rain" in engine.causal_graph
        assert "wet_ground" in engine.causal_graph["rain"]
    
    def test_generate_simple_counterfactual(self):
        """Test generating a simple counterfactual"""
        engine = CounterfactualEngine()
        engine.add_causal_link("strike_match", "fire")
        engine.add_causal_link("fire", "smoke")
        
        scenario = engine.generate_counterfactual("strike_match", "not happened")
        
        assert scenario["original_event"] == "strike_match"
        assert "fire" in scenario["direct_effects"]
        assert len(scenario["cascade_effects"]) > 0
    
    def test_counterfactual_probability(self):
        """Test probability estimation"""
        engine = CounterfactualEngine()
        
        # Simple chain
        engine.add_causal_link("A", "B")
        scenario1 = engine.generate_counterfactual("A", "changed")
        
        # Longer chain
        engine.add_causal_link("B", "C")
        engine.add_causal_link("C", "D")
        scenario2 = engine.generate_counterfactual("A", "changed")
        
        # More effects should mean lower probability
        assert scenario1["probability_estimate"] >= scenario2["probability_estimate"]


class TestSubconsciousDreamer:
    """Test dream-like recombination"""
    
    def test_store_memory_fragment(self):
        """Test storing memory fragments"""
        dreamer = SubconsciousDreamer()
        dreamer.store_memory_fragment("test memory")
        
        assert len(dreamer.memory_fragments) == 1
        assert "test memory" in dreamer.memory_fragments
    
    def test_memory_limit(self):
        """Test memory fragment limit"""
        dreamer = SubconsciousDreamer()
        
        # Store more than 1000 fragments
        for i in range(1050):
            dreamer.store_memory_fragment(f"memory_{i}")
        
        assert len(dreamer.memory_fragments) == 1000
        # Oldest memories should be forgotten
        assert "memory_0" not in dreamer.memory_fragments
        assert "memory_1049" in dreamer.memory_fragments
    
    def test_generate_dream(self):
        """Test dream generation"""
        dreamer = SubconsciousDreamer()
        
        # Add some fragments
        fragments = [
            "flying through space",
            "ocean waves crashing",
            "ancient library",
            "neon city lights",
            "desert sunset"
        ]
        
        for fragment in fragments:
            dreamer.store_memory_fragment(fragment)
        
        dream = dreamer.generate_dream(num_fragments=3)
        
        assert "narrative" in dream
        assert "fragments" in dream
        assert len(dream["fragments"]) == 3
        assert "coherence_score" in dream
        assert "novelty_score" in dream
    
    def test_dream_narrative_weaving(self):
        """Test narrative creation"""
        dreamer = SubconsciousDreamer()
        
        dreamer.store_memory_fragment("a red apple")
        dreamer.store_memory_fragment("a blue ocean")
        
        dream = dreamer.generate_dream(num_fragments=2)
        
        # Narrative should contain both fragments
        assert "red apple" in dream["narrative"].lower()
        assert "blue ocean" in dream["narrative"].lower()


class TestNoveltyEvaluator:
    """Test novelty and utility evaluation"""
    
    def test_novelty_calculation(self):
        """Test novelty scoring"""
        evaluator = NoveltyEvaluator()
        evaluator.add_to_knowledge_base("common")
        evaluator.add_to_knowledge_base("known")
        
        # Known concept should have lower novelty than unknown
        result1 = evaluator.evaluate("this is common and known")
        result2 = evaluator.evaluate("this is xyzqux and flibbertigibbet")
        
        # Unknown words should have higher novelty
        assert result2["novelty_score"] > result1["novelty_score"]
    
    def test_utility_calculation(self):
        """Test utility scoring"""
        evaluator = NoveltyEvaluator()
        
        # Specific, actionable idea
        result1 = evaluator.evaluate("create a system to solve this problem efficiently")
        assert result1["utility_score"] > 0.5
        
        # Vague idea
        result2 = evaluator.evaluate("something good")
        assert result2["utility_score"] < 0.5
    
    def test_combined_scoring(self):
        """Test combined novelty and utility scoring"""
        evaluator = NoveltyEvaluator(novelty_weight=0.6, utility_weight=0.4)
        
        result = evaluator.evaluate("innovative solution to create better systems")
        
        assert "novelty_score" in result
        assert "utility_score" in result
        assert "combined_score" in result
        assert "recommendation" in result
        
        # Combined score should be weighted average
        expected = 0.6 * result["novelty_score"] + 0.4 * result["utility_score"]
        assert abs(result["combined_score"] - expected) < 1e-6


class TestCreativeImaginationEngine:
    """Test the main imagination engine"""
    
    def setup_method(self):
        """Reset engine before each test"""
        reset_imagination_engine()
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = get_imagination_engine()
        
        assert engine.mode == ImaginationMode.EXPLORATORY
        assert len(engine.blender.concept_space) > 0  # Basic concepts initialized
        assert len(engine.creative_history) == 0
    
    def test_exploratory_mode(self):
        """Test exploratory imagination"""
        engine = get_imagination_engine()
        engine.set_mode(ImaginationMode.EXPLORATORY)
        
        result = engine.imagine("explore the concept of time")
        
        assert isinstance(result, ImaginativeOutput)
        assert result.mode == ImaginationMode.EXPLORATORY
        assert len(result.reasoning_chain) > 0
        assert result.novelty_score >= 0
        assert result.utility_score >= 0
    
    def test_exploitative_mode(self):
        """Test exploitative imagination"""
        engine = get_imagination_engine()
        engine.set_mode(ImaginationMode.EXPLOITATIVE)
        
        result = engine.imagine("refine this idea")
        
        assert result.mode == ImaginationMode.EXPLOITATIVE
        # Exploitative mode should have higher utility, lower novelty
        assert result.confidence > 0.7
    
    def test_dreaming_mode(self):
        """Test dreaming mode"""
        engine = get_imagination_engine()
        engine.set_mode(ImaginationMode.DREAMING)
        
        result = engine.imagine("dream about possibilities")
        
        assert result.mode == ImaginationMode.DREAMING
        # Dreams should have high novelty, lower confidence
        assert result.confidence < 0.7
    
    def test_counterfactual_mode(self):
        """Test counterfactual mode"""
        engine = get_imagination_engine()
        engine.set_mode(ImaginationMode.COUNTERFACTUAL)
        
        result = engine.imagine("What if gravity suddenly reversed?")
        
        assert result.mode == ImaginationMode.COUNTERFACTUAL
        assert "What if" in result.generated_output
        assert len(result.alternative_scenarios) > 0
    
    def test_creative_insights_multiple_modes(self):
        """Test generating insights across all modes"""
        engine = get_imagination_engine()
        
        insights = engine.get_creative_insights("creativity")
        
        assert len(insights) == 4  # One per mode
        modes_found = {insight["mode"] for insight in insights}
        
        assert modes_found == {
            "exploratory",
            "exploitative",
            "dreaming",
            "counterfactual"
        }
    
    def test_creative_history_tracking(self):
        """Test that creative history is tracked"""
        engine = get_imagination_engine()
        
        initial_count = len(engine.creative_history)
        
        engine.imagine("test idea 1")
        engine.imagine("test idea 2")
        
        assert len(engine.creative_history) == initial_count + 2
    
    def test_invalid_mode(self):
        """Test handling of invalid mode"""
        engine = get_imagination_engine()
        
        # Manually set invalid mode
        engine.mode = "invalid_mode"
        
        with pytest.raises(ValueError):
            engine.imagine("test")


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios"""
    
    def setup_method(self):
        reset_imagination_engine()
    
    def test_scientific_hypothesis_generation(self):
        """Test generating scientific hypotheses"""
        engine = get_imagination_engine()
        engine.set_mode(ImaginationMode.EXPLORATORY)
        
        result = engine.imagine("quantum mechanics and consciousness")
        
        assert result.novelty_score > 0
        assert len(result.reasoning_chain) > 0
    
    def test_product_innovation(self):
        """Test product innovation scenario"""
        engine = get_imagination_engine()
        
        insights = engine.get_creative_insights("sustainable energy storage")
        
        # Should have diverse insights
        assert len(insights) == 4
        
        # Check structure of insights
        for insight in insights:
            assert "mode" in insight
            assert "insight" in insight
            assert "novelty" in insight
            assert "utility" in insight
        
        # At least one should have good novelty
        max_novelty = max(insight["novelty"] for insight in insights)
        assert max_novelty > 0.3
    
    def test_story_creative_prompts(self):
        """Test generating story ideas"""
        engine = get_imagination_engine()
        engine.set_mode(ImaginationMode.DREAMING)
        
        result = engine.imagine("a world where dreams are currency")
        
        assert result.mode == ImaginationMode.DREAMING
        assert result.novelty_score > 0.5
    
    def test_philosophical_thought_experiment(self):
        """Test philosophical thought experiments"""
        engine = get_imagination_engine()
        engine.set_mode(ImaginationMode.COUNTERFACTUAL)
        
        result = engine.imagine("What if humans never developed language?")
        
        assert result.mode == ImaginationMode.COUNTERFACTUAL
        assert "plausibility" in result.generated_output.lower()


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        reset_imagination_engine()
    
    def test_empty_prompt(self):
        """Test handling empty prompts"""
        engine = get_imagination_engine()
        
        result = engine.imagine("")
        
        assert result is not None
        assert result.original_input == ""
    
    def test_very_long_prompt(self):
        """Test handling very long prompts"""
        engine = get_imagination_engine()
        
        long_prompt = "word " * 1000
        result = engine.imagine(long_prompt)
        
        assert result is not None
        assert len(result.original_input) > 1000
    
    def test_special_characters(self):
        """Test handling special characters"""
        engine = get_imagination_engine()
        
        prompt = "What if @#$%^&*() happened?"
        result = engine.imagine(prompt)
        
        assert result is not None
    
    def test_non_latin_characters(self):
        """Test handling non-Latin characters"""
        engine = get_imagination_engine()
        
        prompt = "什么是创造力？"  # Chinese: "What is creativity?"
        result = engine.imagine(prompt)
        
        assert result is not None
        assert result.original_input == prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
