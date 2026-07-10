"""
Unit tests for the Universal Cognition Engine (UCE).
Validates Perception, Reasoning, Action, and Learning loops.
"""

import unittest
import json
import os
from unittest.mock import patch, MagicMock
from src.modules.cognition_engine import CognitionEngine, MemoryBank, KnowledgeNode, CognitiveState


class TestKnowledgeNode(unittest.TestCase):
    def test_creation(self):
        node = KnowledgeNode(
            id="test_1", domain="coding", pattern_type="bug_fix", description="Fixed infinite loop"
        )
        self.assertEqual(node.id, "test_1")
        self.assertEqual(node.confidence_score, 0.5)
        self.assertIn("created_at", node.to_dict())

    def test_serialization(self):
        node = KnowledgeNode(
            id="test_2", domain="math", pattern_type="formula", description="E=mc^2"
        )
        data = node.to_dict()
        restored = KnowledgeNode.from_dict(data)
        self.assertEqual(restored.id, node.id)
        self.assertEqual(restored.description, node.description)


class TestMemoryBank(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_memory.json"
        self.memory = MemoryBank(storage_path=self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_add_and_search(self):
        node = KnowledgeNode(
            id="mem_1", domain="physics", pattern_type="law", description="Newton's First Law"
        )
        self.memory.add_node(node)

        # Reload to test persistence
        new_memory = MemoryBank(storage_path=self.test_file)
        results = new_memory.search("physics")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].description, "Newton's First Law")

    def test_reinforce(self):
        node = KnowledgeNode(
            id="mem_2", domain="logic", pattern_type="fallacy", description="Ad Hominem"
        )
        self.memory.add_node(node)
        self.memory.reinforce("mem_2", success=True)

        # Check confidence increased
        self.assertGreater(self.memory.nodes["mem_2"].confidence_score, 0.5)


class TestCognitionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CognitionEngine()
        # Mock external dependencies to avoid API calls during tests
        self.engine.llm = MagicMock()
        self.engine.sandbox = MagicMock()

    def test_state_transitions(self):
        self.assertEqual(self.engine.state, CognitiveState.IDLE)

        # Mock LLM response for perception
        self.engine.llm.generate.return_value = {"content": '{"structure": "valid"}'}
        self.engine.perceive({"data": "test"}, "general")
        self.assertEqual(self.engine.state, CognitiveState.PERCEIVING)

    def test_perceive_with_prior_knowledge(self):
        # Add a knowledge node
        node = KnowledgeNode(
            id="prior_1", domain="test_domain", pattern_type="pattern", description="Known pattern"
        )
        self.engine.memory.add_node(node)

        # Mock LLM
        self.engine.llm.generate.return_value = {"content": '{"analysis": "complete"}'}

        result = self.engine.perceive({"input": "data"}, "test_domain")

        # Verify LLM was called with context including prior knowledge
        call_args = self.engine.llm.generate.call_args
        prompt_content = call_args[0][0]
        self.assertIn("Known pattern", prompt_content)

    def test_reason_parsing_list(self):
        self.engine.llm.generate.return_value = {
            "content": '[{"step_id": "1", "description": "Step 1", "expected_outcome": "OK"}]'
        }
        analysis = {"problem": "test"}
        plan = self.engine.reason(analysis, "general")

        self.assertIsInstance(plan, list)
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["step_id"], "1")

    def test_reason_parsing_fallback(self):
        # Simulate non-JSON response
        self.engine.llm.generate.return_value = {"content": "Just do step 1"}
        analysis = {"problem": "test"}
        plan = self.engine.reason(analysis, "general")

        self.assertIsInstance(plan, list)
        self.assertEqual(plan[0]["description"], "Just do step 1")

    def test_act_execution_vs_simulation(self):
        self.engine.sandbox.execute.return_value = {"success": True, "output": "42"}

        plan = [
            {
                "step_id": "1",
                "description": "analyze the data",
            },  # Should simulate (no code keywords)
            {"step_id": "2", "description": "think about logic"},  # Should simulate
        ]

        results = self.engine.act(plan, "general")  # Use 'general' domain

        self.assertEqual(results[0]["status"], "simulated")
        self.assertEqual(results[1]["status"], "simulated")

    def test_learn_creates_node(self):
        initial_count = len(self.engine.memory.nodes)

        self.engine.llm.generate.return_value = {
            "content": "Always check for off-by-one errors in loops."
        }

        self.engine.learn(
            original_input={"code": "for i in range(n): ..."},
            plan=[{"step_id": "1", "description": "fix loop"}],
            results=[{"success": True}],
            domain="coding",
        )

        new_count = len(self.engine.memory.nodes)
        self.assertEqual(new_count, initial_count + 1)

    def test_full_process_loop(self):
        # Mock all stages
        self.engine.llm.generate.side_effect = [
            {"content": '{"issue": "syntax error"}'},  # Perceive
            {"content": '[{"step_id": "1", "description": "fix syntax"}]'},  # Reason
            {"content": "Check for missing colons."},  # Learn
        ]
        self.engine.sandbox.execute.return_value = {"success": True, "output": ""}

        result = self.engine.process({"code": "print('hello'"}, "coding")

        self.assertEqual(result["status"], "success")
        self.assertIn("analysis", result)
        self.assertIn("plan", result)
        self.assertIn("results", result)


if __name__ == "__main__":
    unittest.main()
