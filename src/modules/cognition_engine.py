"""
Universal Cognition Engine (UCE) v1.0
-------------------------------------
Core module for "Identifying and Researching All Things".
This engine provides a generalized framework for:
1. Perception: Parsing diverse inputs (code, text, data structures).
2. Reasoning: Generating dynamic Chains of Thought (CoT).
3. Learning: Extracting patterns from interactions to build local knowledge.
4. Action: Executing verified plans in safe environments.

Author: AI Assistant
Goal: To evolve towards universal wisdom through continuous iteration.
"""

import json
import hashlib
import logging
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

# Import existing modules for integration
try:
    from .config import Config
    from .llm_client import LLMClient
    from .secure_sandbox import SecureSandbox
except ImportError:
    # Fallback for standalone testing or partial imports
    class Config:
        @staticmethod
        def get(key, default=None):
            return default

    class LLMClient:
        def generate(self, *args, **kwargs):
            return {"content": "", "usage": {}}

    class SecureSandbox:
        def execute(self, *args, **kwargs):
            return {"success": False, "output": ""}


logger = logging.getLogger(__name__)


class CognitiveState(Enum):
    """Represents the current state of the cognitive process."""

    IDLE = "idle"
    PERCEIVING = "perceiving"
    REASONING = "reasoning"
    PLANNING = "planning"
    ACTING = "acting"
    LEARNING = "learning"
    ERROR = "error"


@dataclass
class KnowledgeNode:
    """A single unit of learned knowledge or pattern."""

    id: str
    domain: str
    pattern_type: str  # e.g., "logic_error", "optimization_strategy", "scientific_law"
    description: str
    examples: List[str] = field(default_factory=list)
    confidence_score: float = 0.5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "KnowledgeNode":
        return cls(**data)


class MemoryBank:
    """
    Local persistent memory for storing extracted patterns and knowledge.
    Simulates long-term memory for the cognition engine.
    """

    def __init__(self, storage_path: str = "memory_bank.json"):
        self.storage_path = storage_path
        self.nodes: Dict[str, KnowledgeNode] = {}
        self._load()

    def _load(self):
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.nodes = {k: KnowledgeNode.from_dict(v) for k, v in data.items()}
            logger.info(f"Loaded {len(self.nodes)} knowledge nodes from memory.")
        except FileNotFoundError:
            logger.info("No existing memory bank found. Starting fresh.")
        except json.JSONDecodeError:
            logger.error("Memory bank corrupted. Starting fresh.")
            self.nodes = {}

    def save(self):
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump({k: v.to_dict() for k, v in self.nodes.items()}, f, indent=2)
        logger.debug("Memory bank saved.")

    def add_node(self, node: KnowledgeNode):
        self.nodes[node.id] = node
        self.save()
        logger.info(f"New knowledge acquired: {node.id} in domain {node.domain}")

    def search(self, query_domain: str, pattern_type: Optional[str] = None) -> List[KnowledgeNode]:
        """Retrieve relevant knowledge based on domain and type."""
        results = []
        for node in self.nodes.values():
            if node.domain == query_domain:
                if pattern_type is None or node.pattern_type == pattern_type:
                    node.last_accessed = datetime.now().isoformat()
                    results.append(node)
        # Sort by confidence score
        return sorted(results, key=lambda x: x.confidence_score, reverse=True)

    def reinforce(self, node_id: str, success: bool):
        """Update confidence score based on feedback."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            delta = 0.1 if success else -0.1
            node.confidence_score = max(0.0, min(1.0, node.confidence_score + delta))
            self.save()


class CognitionEngine:
    """
    The main brain orchestrating perception, reasoning, action, and learning.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.llm = LLMClient()  # Uses default config or env vars
        self.sandbox = SecureSandbox()
        self.memory = MemoryBank()
        self.state = CognitiveState.IDLE
        self.context_window: List[Dict] = []

    def _update_state(self, new_state: CognitiveState):
        self.state = new_state
        logger.debug(f"Cognitive state changed to: {new_state.value}")

    def perceive(self, input_data: Any, domain: str) -> Dict:
        """
        Phase 1: Perception.
        Analyze input data to understand structure, intent, and constraints.
        """
        self._update_state(CognitiveState.PERCEIVING)
        prompt = f"""
        You are a universal perceiver. Analyze the following input within the domain of '{domain}'.
        Identify:
        1. Core components and structure.
        2. Potential anomalies or key features.
        3. The underlying intent or problem statement.
        
        Input:
        {json.dumps(input_data, indent=2) if isinstance(input_data, (dict, list)) else str(input_data)}
        
        Output a structured JSON analysis.
        """

        # Retrieve relevant past knowledge to aid perception
        prior_knowledge = self.memory.search(domain)
        if prior_knowledge:
            context = "\nRelevant known patterns:\n" + "\n".join(
                [f"- {k.description}" for k in prior_knowledge[:3]]
            )
            prompt += context

        response = self.llm.generate(
            prompt, system_prompt="You are an analytical engine for universal perception."
        )
        try:
            # Assuming LLM returns valid JSON in 'content'
            analysis = json.loads(response["content"])
            logger.info("Perception complete.")
            return analysis
        except json.JSONDecodeError:
            logger.error("Failed to parse perception output.")
            return {"raw_analysis": response["content"], "error": "Parse failed"}

    def reason(self, analysis: Dict, domain: str) -> List[Dict]:
        """
        Phase 2: Reasoning.
        Generate a Chain of Thought (CoT) to solve the identified problem.
        """
        self._update_state(CognitiveState.REASONING)
        prompt = f"""
        Based on this analysis: {json.dumps(analysis)}
        Formulate a step-by-step reasoning plan to address the core problem in the domain of '{domain}'.
        Each step should be a verifiable hypothesis or action.
        Format: List of steps with 'step_id', 'description', 'expected_outcome'.
        """

        response = self.llm.generate(
            prompt, system_prompt="You are a logical reasoner. Think step-by-step."
        )
        try:
            plan = json.loads(response["content"])
            if isinstance(plan, list):
                logger.info(f"Reasoning complete. Generated {len(plan)} steps.")
                return plan
            else:
                return [
                    {"step_id": "1", "description": str(plan), "expected_outcome": "Resolution"}
                ]
        except json.JSONDecodeError:
            return [
                {
                    "step_id": "1",
                    "description": response["content"],
                    "expected_outcome": "Resolution",
                }
            ]

    def act(self, plan: List[Dict], domain: str) -> List[Dict]:
        """
        Phase 3: Action.
        Execute the plan steps in a safe environment (if applicable) or simulate.
        """
        self._update_state(CognitiveState.ACTING)
        results = []

        for step in plan:
            step_id = step.get("step_id", "unknown")
            description = step.get("description", "")

            logger.info(f"Executing step {step_id}: {description}")

            # Determine if this step requires code execution
            # Heuristic: If domain is 'coding' or description contains code-like keywords
            needs_execution = domain == "coding" or any(
                k in description.lower() for k in ["run", "execute", "calculate", "def ", "import "]
            )

            if needs_execution:
                # Use sandbox for safety
                exec_result = self.sandbox.execute(description, timeout=5)
                results.append(
                    {
                        "step_id": step_id,
                        "status": "executed",
                        "output": exec_result.get("output", ""),
                        "success": exec_result.get("success", False),
                    }
                )
            else:
                # Simulated action or theoretical deduction
                results.append(
                    {
                        "step_id": step_id,
                        "status": "simulated",
                        "output": f"Simulated outcome for: {description}",
                        "success": True,
                    }
                )

        logger.info("Action phase complete.")
        return results

    def learn(self, original_input: Any, plan: List[Dict], results: List[Dict], domain: str):
        """
        Phase 4: Learning.
        Extract patterns from the outcome and store in Memory Bank.
        """
        self._update_state(CognitiveState.LEARNING)

        success = all(r.get("success", False) for r in results)
        pattern_type = "success_pattern" if success else "failure_pattern"

        summary_prompt = f"""
        Input: {str(original_input)[:500]}
        Plan: {json.dumps(plan)}
        Results: {json.dumps(results)}
        
        Extract a generalizable lesson or pattern from this interaction.
        Describe the pattern clearly so it can be applied to future similar problems in '{domain}'.
        """

        response = self.llm.generate(
            summary_prompt, system_prompt="You are a meta-learner. Extract wisdom."
        )

        node_id = hashlib.sha256(f"{domain}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        new_node = KnowledgeNode(
            id=node_id,
            domain=domain,
            pattern_type=pattern_type,
            description=response["content"],
            examples=[str(original_input)[:200]],
            confidence_score=0.6,
        )

        self.memory.add_node(new_node)

        # Reinforce any prior knowledge used
        # (Simplified logic for demo)

        logger.info(f"Learning complete. New knowledge node created: {node_id}")

    def process(self, input_data: Any, domain: str = "general") -> Dict:
        """
        Main entry point: Orchestrates the full cognitive loop.
        """
        logger.info(f"Starting cognitive process for domain: {domain}")
        try:
            analysis = self.perceive(input_data, domain)
            plan = self.reason(analysis, domain)
            results = self.act(plan, domain)
            self.learn(input_data, plan, results, domain)

            return {
                "status": "success",
                "analysis": analysis,
                "plan": plan,
                "results": results,
                "state": self.state.value,
            }
        except Exception as e:
            logger.error(f"Cognitive process failed: {e}", exc_info=True)
            self._update_state(CognitiveState.ERROR)
            return {"status": "error", "error_message": str(e), "state": self.state.value}


# Example usage for self-validation
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = CognitionEngine()

    # Test Case 1: Coding Domain
    print("\n--- Testing Coding Domain ---")
    code_problem = {"task": "Fix the infinite loop", "code": "while True: print('help')"}
    result = engine.process(code_problem, domain="coding")
    print(f"Final State: {result['status']}")

    # Test Case 2: General Logic Domain
    print("\n--- Testing General Logic Domain ---")
    logic_problem = "If all A are B, and some B are C, can we conclude some A are C?"
    result = engine.process(logic_problem, domain="logic")
    print(f"Final State: {result['status']}")
