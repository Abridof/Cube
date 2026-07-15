"""
Creative Imagination Engine for AGI
=====================================
Enables counterfactual reasoning, concept blending, and novel idea generation.

This module implements:
- Concept Space Walk: Random walk through semantic space to discover new connections
- Counterfactual Engine: "What if" reasoning with causal graph manipulation
- Dream Recombination: Subconscious-style random recombination of memory fragments
- Novelty Evaluator: Balances novelty vs utility using information theory
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class ImaginationMode(Enum):
    """Modes of imaginative thinking"""
    EXPLORATORY = "exploratory"  # Wide search, high novelty
    EXPLOITATIVE = "exploitative"  # Deep refinement, high utility
    DREAMING = "dreaming"  # Unconstrained, surreal combinations
    COUNTERFACTUAL = "counterfactual"  # Alternative history/logic scenarios


@dataclass
class ConceptNode:
    """Represents a concept in the imagination space"""
    name: str
    semantic_vector: np.ndarray
    attributes: Dict[str, Any] = field(default_factory=dict)
    activation_level: float = 0.5
    connections: Set[str] = field(default_factory=set)
    
    def similarity_to(self, other: 'ConceptNode') -> float:
        """Calculate cosine similarity between concepts"""
        norm1 = np.linalg.norm(self.semantic_vector)
        norm2 = np.linalg.norm(other.semantic_vector)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(self.semantic_vector, other.semantic_vector) / (norm1 * norm2))


@dataclass
class ImaginativeOutput:
    """Result of an imaginative process"""
    original_input: str
    generated_output: str
    mode: ImaginationMode
    novelty_score: float
    utility_score: float
    confidence: float
    reasoning_chain: List[str] = field(default_factory=list)
    alternative_scenarios: List[str] = field(default_factory=list)


class ConceptBlender:
    """Blends two or more concepts to create novel combinations"""
    
    def __init__(self, vocabulary_size: int = 1000, embedding_dim: int = 128):
        self.vocabulary_size = vocabulary_size
        self.embedding_dim = embedding_dim
        self.concept_space: Dict[str, ConceptNode] = {}
        
    def add_concept(self, name: str, attributes: Optional[Dict] = None) -> ConceptNode:
        """Add a concept to the space with random initial embedding"""
        if name not in self.concept_space:
            vector = np.random.randn(self.embedding_dim)
            vector /= np.linalg.norm(vector)
            self.concept_space[name] = ConceptNode(
                name=name,
                semantic_vector=vector,
                attributes=attributes or {}
            )
        return self.concept_space[name]
    
    def blend_concepts(self, concept_names: List[str], 
                      blend_ratio: Optional[List[float]] = None) -> ConceptNode:
        """Create a blended concept from multiple source concepts"""
        if len(concept_names) < 2:
            raise ValueError("Need at least 2 concepts to blend")
        
        concepts = [self.concept_space[name] for name in concept_names if name in self.concept_space]
        if len(concepts) < 2:
            raise ValueError(f"Could not find enough concepts: {concept_names}")
        
        if blend_ratio is None:
            blend_ratio = [1.0 / len(concepts)] * len(concepts)
        
        # Weighted average of semantic vectors
        blended_vector = sum(c.semantic_vector * r for c, r in zip(concepts, blend_ratio))
        blended_vector /= np.linalg.norm(blended_vector)
        
        # Merge attributes with creative modifications
        blended_attrs = {}
        for concept, ratio in zip(concepts, blend_ratio):
            for key, value in concept.attributes.items():
                if key not in blended_attrs:
                    blended_attrs[key] = value
                elif isinstance(value, (int, float)):
                    # Numeric attributes are averaged
                    blended_attrs[key] = blended_attrs[key] * (1 - ratio) + value * ratio
        
        blended_name = "_".join(concept_names[:2]) + "_fusion"
        blended_concept = ConceptNode(
            name=blended_name,
            semantic_vector=blended_vector,
            attributes=blended_attrs,
            connections=set(concept_names)
        )
        
        self.concept_space[blended_name] = blended_concept
        return blended_concept
    
    def find_distant_concepts(self, reference: str, top_k: int = 5) -> List[str]:
        """Find concepts most dissimilar to the reference"""
        if reference not in self.concept_space:
            return []
        
        ref_concept = self.concept_space[reference]
        similarities = []
        
        for name, concept in self.concept_space.items():
            if name != reference:
                sim = ref_concept.similarity_to(concept)
                similarities.append((name, sim))
        
        # Sort by distance (inverse similarity)
        similarities.sort(key=lambda x: x[1])
        return [name for name, _ in similarities[:top_k]]


class CounterfactualEngine:
    """Generates and evaluates counterfactual scenarios"""
    
    def __init__(self):
        self.causal_graph: Dict[str, List[str]] = {}
        self.factual_knowledge: Dict[str, Any] = {}
        
    def add_causal_link(self, cause: str, effect: str):
        """Add a causal relationship to the graph"""
        if cause not in self.causal_graph:
            self.causal_graph[cause] = []
        if effect not in self.causal_graph[cause]:
            self.causal_graph[cause].append(effect)
    
    def generate_counterfactual(self, event: str, 
                               modification: str) -> Dict[str, Any]:
        """Generate a counterfactual scenario by modifying an event"""
        scenario = {
            "original_event": event,
            "modification": modification,
            "direct_effects": [],
            "cascade_effects": [],
            "probability_estimate": 0.0,
            "plausibility_score": 0.0
        }
        
        # Find effects of the modified event
        if event in self.causal_graph:
            scenario["direct_effects"] = self.causal_graph[event][:]
            
            # Propagate effects through the causal chain
            visited = set()
            queue = list(scenario["direct_effects"])
            
            while queue and len(visited) < 50:  # Limit depth
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                scenario["cascade_effects"].append(current)
                
                if current in self.causal_graph:
                    queue.extend(self.causal_graph[current])
        
        # Estimate probability based on number of changes required
        num_changes = len(scenario["direct_effects"]) + len(scenario["cascade_effects"])
        scenario["probability_estimate"] = math.exp(-0.5 * num_changes)
        
        # Plausibility based on consistency with known facts
        scenario["plausibility_score"] = self._evaluate_plausibility(scenario)
        
        return scenario
    
    def _evaluate_plausibility(self, scenario: Dict) -> float:
        """Evaluate how plausible a counterfactual scenario is"""
        # Simple heuristic: fewer contradictions = higher plausibility
        contradictions = 0
        
        for effect in scenario.get("cascade_effects", []):
            if effect in self.factual_knowledge:
                # Check if effect contradicts known facts
                if self.factual_knowledge[effect] == False:
                    contradictions += 1
        
        return max(0.0, 1.0 - contradictions * 0.2)


class SubconsciousDreamer:
    """Simulates dream-like recombination of memories and concepts"""
    
    def __init__(self, temperature: float = 0.8):
        self.temperature = temperature
        self.memory_fragments: List[str] = []
        self.dream_log: List[Dict] = []
        
    def store_memory_fragment(self, fragment: str):
        """Store a memory fragment for potential dream recombination"""
        self.memory_fragments.append(fragment)
        if len(self.memory_fragments) > 1000:
            # Forget oldest memories
            self.memory_fragments = self.memory_fragments[-1000:]
    
    def generate_dream(self, num_fragments: int = 5) -> Dict[str, Any]:
        """Generate a dream-like recombination of memory fragments"""
        if len(self.memory_fragments) < num_fragments:
            return {"error": "Not enough memory fragments"}
        
        # Random selection with temperature-based weighting
        weights = np.exp(np.random.randn(len(self.memory_fragments)) * self.temperature)
        weights /= weights.sum()
        
        selected_indices = np.random.choice(
            len(self.memory_fragments), 
            size=num_fragments, 
            p=weights, 
            replace=False
        )
        
        selected_fragments = [self.memory_fragments[i] for i in selected_indices]
        
        # Create surreal narrative
        dream_narrative = self._weave_dream_narrative(selected_fragments)
        
        dream_result = {
            "fragments": selected_fragments,
            "narrative": dream_narrative,
            "coherence_score": self._evaluate_dream_coherence(selected_fragments),
            "novelty_score": self._evaluate_dream_novelty(selected_fragments),
            "emotional_tone": self._extract_emotional_tone(dream_narrative)
        }
        
        self.dream_log.append(dream_result)
        return dream_result
    
    def _weave_dream_narrative(self, fragments: List[str]) -> str:
        """Create a surreal narrative from fragments"""
        connectors = [
            "suddenly transformed into",
            "merged with",
            "was floating inside",
            "became one with",
            "dissolved into",
            "gave birth to"
        ]
        
        narrative = fragments[0]
        for i, fragment in enumerate(fragments[1:], 1):
            connector = random.choice(connectors)
            narrative += f" {connector} {fragment}"
        
        return narrative + " in an endless loop of meaning."
    
    def _evaluate_dream_coherence(self, fragments: List[str]) -> float:
        """Evaluate how coherent the dream narrative is"""
        # Simple metric: semantic overlap between fragments
        words_sets = [set(f.lower().split()) for f in fragments]
        
        overlaps = []
        for i in range(len(words_sets) - 1):
            intersection = len(words_sets[i] & words_sets[i+1])
            union = len(words_sets[i] | words_sets[i+1])
            if union > 0:
                overlaps.append(intersection / union)
        
        return np.mean(overlaps) if overlaps else 0.0
    
    def _evaluate_dream_novelty(self, fragments: List[str]) -> float:
        """Evaluate novelty of the dream combination"""
        # Novelty increases with unusual combinations
        word_freq: Dict[str, int] = {}
        for fragment in fragments:
            for word in fragment.lower().split():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Rare word combinations indicate higher novelty
        rarity_scores = [1.0 / freq for freq in word_freq.values()]
        return np.mean(rarity_scores) if rarity_scores else 0.0
    
    def _extract_emotional_tone(self, narrative: str) -> str:
        """Extract the emotional tone of a dream narrative"""
        positive_words = {'beautiful', 'wonderful', 'amazing', 'joy', 'love', 'peace'}
        negative_words = {'terrible', 'awful', 'fear', 'anger', 'sad', 'chaos'}
        
        words = set(narrative.lower().split())
        
        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)
        
        if pos_count > neg_count:
            return "positive/euphoric"
        elif neg_count > pos_count:
            return "negative/anxious"
        else:
            return "neutral/surreal"


class NoveltyEvaluator:
    """Evaluates the novelty and utility of generated ideas"""
    
    def __init__(self, novelty_weight: float = 0.6, utility_weight: float = 0.4):
        self.novelty_weight = novelty_weight
        self.utility_weight = utility_weight
        self.knowledge_base: Set[str] = set()
        
    def add_to_knowledge_base(self, concept: str):
        """Add a known concept to the knowledge base"""
        self.knowledge_base.add(concept.lower())
    
    def evaluate(self, idea: str, context: Optional[str] = None) -> Dict[str, float]:
        """Evaluate an idea's novelty and utility"""
        novelty = self._calculate_novelty(idea)
        utility = self._calculate_utility(idea, context)
        
        combined_score = (
            self.novelty_weight * novelty + 
            self.utility_weight * utility
        )
        
        return {
            "novelty_score": novelty,
            "utility_score": utility,
            "combined_score": combined_score,
            "recommendation": self._generate_recommendation(novelty, utility)
        }
    
    def _calculate_novelty(self, idea: str) -> float:
        """Calculate novelty based on rarity in knowledge base"""
        words = idea.lower().split()
        
        if not words:
            return 0.0
        
        rare_word_count = sum(1 for word in words if word not in self.knowledge_base)
        return rare_word_count / len(words)
    
    def _calculate_utility(self, idea: str, context: Optional[str]) -> float:
        """Calculate utility based on relevance and actionability"""
        # Simple heuristic: longer, more specific ideas tend to be more useful
        specificity_score = min(1.0, len(idea.split()) / 20.0)
        
        # Check for action verbs (simple heuristic)
        action_verbs = {'create', 'build', 'make', 'solve', 'fix', 'improve', 'design'}
        has_action = any(verb in idea.lower() for verb in action_verbs)
        
        context_relevance = 0.5
        if context:
            context_words = set(context.lower().split())
            idea_words = set(idea.lower().split())
            overlap = len(context_words & idea_words)
            context_relevance = min(1.0, overlap / max(1, len(context_words)))
        
        return (specificity_score * 0.4 + 
                (1.0 if has_action else 0.3) * 0.3 + 
                context_relevance * 0.3)
    
    def _generate_recommendation(self, novelty: float, utility: float) -> str:
        """Generate a recommendation based on scores"""
        if novelty > 0.7 and utility > 0.7:
            return "HIGHLY RECOMMENDED: Both novel and useful"
        elif novelty > 0.7:
            return "INTERESTING: Very novel but may need refinement for practical use"
        elif utility > 0.7:
            return "PRACTICAL: Useful but consider adding novel elements"
        else:
            return "NEEDS WORK: Consider revising for both novelty and utility"


class CreativeImaginationEngine:
    """Main engine for creative imagination processes"""
    
    def __init__(self, embedding_dim: int = 128):
        self.blender = ConceptBlender(embedding_dim=embedding_dim)
        self.counterfactual = CounterfactualEngine()
        self.dreamer = SubconsciousDreamer()
        self.evaluator = NoveltyEvaluator()
        
        self.mode = ImaginationMode.EXPLORATORY
        self.creative_history: List[ImaginativeOutput] = []
        
        # Initialize with some basic concepts
        self._initialize_basic_concepts()
    
    def _initialize_basic_concepts(self):
        """Initialize with fundamental concepts"""
        basic_concepts = [
            ("time", {"abstract": True, "dimension": "temporal"}),
            ("space", {"abstract": True, "dimension": "spatial"}),
            ("cause", {"abstract": True, "type": "relation"}),
            ("effect", {"abstract": True, "type": "relation"}),
            ("life", {"abstract": False, "category": "biology"}),
            ("death", {"abstract": False, "category": "biology"}),
            ("love", {"abstract": True, "category": "emotion"}),
            ("fear", {"abstract": True, "category": "emotion"}),
            ("creation", {"abstract": True, "action": True}),
            ("destruction", {"abstract": True, "action": True}),
        ]
        
        for name, attrs in basic_concepts:
            self.blender.add_concept(name, attrs)
            self.evaluator.add_to_knowledge_base(name)
        
        # Add some causal links
        self.counterfactual.add_causal_link("rain", "wet_ground")
        self.counterfactual.add_causal_link("fire", "smoke")
        self.counterfactual.add_causal_link("study", "knowledge")
        self.counterfactual.add_causal_link("practice", "skill")
    
    def set_mode(self, mode: ImaginationMode):
        """Set the imagination mode"""
        self.mode = mode
    
    def imagine(self, prompt: str, 
               constraints: Optional[List[str]] = None) -> ImaginativeOutput:
        """Generate creative output based on prompt and mode"""
        
        if self.mode == ImaginationMode.EXPLORATORY:
            return self._exploratory_imagination(prompt, constraints)
        elif self.mode == ImaginationMode.EXPLOITATIVE:
            return self._exploitative_imagination(prompt, constraints)
        elif self.mode == ImaginationMode.DREAMING:
            return self._dreaming_imagination(prompt, constraints)
        elif self.mode == ImaginationMode.COUNTERFACTUAL:
            return self._counterfactual_imagination(prompt, constraints)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")
    
    def _exploratory_imagination(self, prompt: str, 
                                constraints: Optional[List[str]]) -> ImaginativeOutput:
        """Wide search for novel connections"""
        reasoning_chain = []
        
        # Extract key concepts from prompt
        prompt_words = prompt.lower().split()
        known_concepts = [w for w in prompt_words if w in self.blender.concept_space]
        
        if not known_concepts:
            # Add first word as new concept
            first_word = prompt_words[0] if prompt_words else "unknown"
            self.blender.add_concept(first_word)
            known_concepts = [first_word]
        
        reasoning_chain.append(f"Identified concepts: {known_concepts}")
        
        # Find distant concepts for blending
        distant = self.blender.find_distant_concepts(known_concepts[0], top_k=3)
        reasoning_chain.append(f"Found distant concepts: {distant}")
        
        # Blend with distant concepts
        if distant:
            blend_target = distant[0]
            blended = self.blender.blend_concepts([known_concepts[0], blend_target])
            reasoning_chain.append(f"Created blend: {blended.name}")
            
            output_text = f"Imagine {prompt} through the lens of {blend_target}: "
            output_text += f"The fusion reveals unexpected properties where "
            output_text += f"{known_concepts[0]} and {blend_target} intersect."
        else:
            output_text = f"Exploring variations of: {prompt}"
        
        evaluation = self.evaluator.evaluate(output_text, prompt)
        
        result = ImaginativeOutput(
            original_input=prompt,
            generated_output=output_text,
            mode=self.mode,
            novelty_score=evaluation["novelty_score"],
            utility_score=evaluation["utility_score"],
            confidence=0.7,
            reasoning_chain=reasoning_chain
        )
        
        self.creative_history.append(result)
        return result
    
    def _exploitative_imagination(self, prompt: str, 
                                 constraints: Optional[List[str]]) -> ImaginativeOutput:
        """Deep refinement of existing ideas"""
        reasoning_chain = ["Refining concept in depth"]
        
        # Focus on elaborating the prompt
        elaborations = [
            f"Consider the nuances of {prompt}",
            f"What are the underlying assumptions?",
            f"How does this connect to related domains?",
            f"What edge cases should be considered?"
        ]
        
        output_text = " | ".join(elaborations)
        evaluation = self.evaluator.evaluate(output_text, prompt)
        
        result = ImaginativeOutput(
            original_input=prompt,
            generated_output=output_text,
            mode=self.mode,
            novelty_score=evaluation["novelty_score"] * 0.7,  # Lower novelty expected
            utility_score=evaluation["utility_score"] * 1.3,  # Higher utility expected
            confidence=0.85,
            reasoning_chain=reasoning_chain
        )
        
        self.creative_history.append(result)
        return result
    
    def _dreaming_imagination(self, prompt: str, 
                             constraints: Optional[List[str]]) -> ImaginativeOutput:
        """Unconstrained, surreal combinations"""
        reasoning_chain = ["Entering dream state", "Accessing memory fragments"]
        
        # Store prompt as memory fragment
        self.dreamer.store_memory_fragment(prompt)
        
        # Generate dream
        dream = self.dreamer.generate_dream(num_fragments=4)
        
        if "error" in dream:
            output_text = f"Dreaming about: {prompt}"
        else:
            output_text = dream["narrative"]
            reasoning_chain.append(f"Dream coherence: {dream['coherence_score']:.2f}")
            reasoning_chain.append(f"Dream novelty: {dream['novelty_score']:.2f}")
        
        evaluation = self.evaluator.evaluate(output_text, prompt)
        
        result = ImaginativeOutput(
            original_input=prompt,
            generated_output=output_text,
            mode=self.mode,
            novelty_score=evaluation["novelty_score"] * 1.5,  # Amplify novelty
            utility_score=evaluation["utility_score"] * 0.5,  # Reduce utility focus
            confidence=0.5,  # Lower confidence for dreams
            reasoning_chain=reasoning_chain,
            alternative_scenarios=[output_text]
        )
        
        self.creative_history.append(result)
        return result
    
    def _counterfactual_imagination(self, prompt: str, 
                                   constraints: Optional[List[str]]) -> ImaginativeOutput:
        """Alternative history/logic scenarios"""
        reasoning_chain = ["Constructing counterfactual scenario"]
        
        # Parse prompt for event and modification
        # Simple heuristic: look for "if" or "what if"
        if "if" in prompt.lower():
            parts = prompt.lower().split("if", 1)
            event = parts[0].strip()
            modification = parts[1].strip() if len(parts) > 1 else "different outcome"
        else:
            event = prompt
            modification = "alternative version"
        
        scenario = self.counterfactual.generate_counterfactual(event, modification)
        
        output_text = f"What if {event} had {modification}?\\n"
        output_text += f"Direct effects: {', '.join(scenario['direct_effects']) or 'None identified'}\\n"
        output_text += f"Cascade effects: {', '.join(scenario['cascade_effects'][:5]) or 'None identified'}\\n"
        output_text += f"Plausibility: {scenario['plausibility_score']:.2f}"
        
        reasoning_chain.append(f"Generated {len(scenario['cascade_effects'])} cascade effects")
        
        result = ImaginativeOutput(
            original_input=prompt,
            generated_output=output_text,
            mode=self.mode,
            novelty_score=0.8,  # Counterfactuals are inherently novel
            utility_score=scenario['plausibility_score'],
            confidence=scenario['plausibility_score'],
            reasoning_chain=reasoning_chain,
            alternative_scenarios=[output_text]
        )
        
        self.creative_history.append(result)
        return result
    
    def get_creative_insights(self, topic: str) -> List[Dict[str, Any]]:
        """Generate multiple creative insights on a topic"""
        insights = []
        
        # Try different modes
        for mode in ImaginationMode:
            self.set_mode(mode)
            result = self.imagine(f"Explore creative aspects of {topic}")
            insights.append({
                "mode": mode.value,
                "insight": result.generated_output,
                "novelty": result.novelty_score,
                "utility": result.utility_score
            })
        
        # Reset to exploratory
        self.set_mode(ImaginationMode.EXPLORATORY)
        
        return insights
    
    def save_creative_history(self, filepath: str):
        """Save creative history to file"""
        import json
        
        history_data = []
        for item in self.creative_history:
            history_data.append({
                "input": item.original_input,
                "output": item.generated_output,
                "mode": item.mode.value,
                "novelty": item.novelty_score,
                "utility": item.utility_score,
                "confidence": item.confidence,
                "reasoning": item.reasoning_chain
            })
        
        with open(filepath, 'w') as f:
            json.dump(history_data, f, indent=2)
    
    def load_creative_history(self, filepath: str):
        """Load creative history from file"""
        import json
        
        try:
            with open(filepath, 'r') as f:
                history_data = json.load(f)
            
            self.creative_history = []
            for item in history_data:
                self.creative_history.append(ImaginativeOutput(
                    original_input=item["input"],
                    generated_output=item["output"],
                    mode=ImaginationMode(item["mode"]),
                    novelty_score=item["novelty"],
                    utility_score=item["utility"],
                    confidence=item["confidence"],
                    reasoning_chain=item.get("reasoning", [])
                ))
        except FileNotFoundError:
            pass  # Start fresh if file doesn't exist


# Singleton instance
_imagination_engine: Optional[CreativeImaginationEngine] = None


def get_imagination_engine() -> CreativeImaginationEngine:
    """Get or create the singleton imagination engine"""
    global _imagination_engine
    if _imagination_engine is None:
        _imagination_engine = CreativeImaginationEngine()
    return _imagination_engine


def reset_imagination_engine():
    """Reset the singleton instance (useful for testing)"""
    global _imagination_engine
    _imagination_engine = None
