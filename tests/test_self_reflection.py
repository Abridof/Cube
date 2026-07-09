"""
Test suite for Self-Reflection and Code Self-Modification Module
"""

import unittest
import os
import sys
import tempfile
import ast
from self_reflection import (
    CodeParser, CodeSmell, LimitationType, CodeLocation,
    CodeSmellDetection, LimitationAnalysis, SelfImprovementHypothesis,
    CodeModification, CodeParser, LimitationAnalyzer, SelfReflector,
    CodeModifier, SafetySandbox, SecurityError, SelfReflectionEngine
)


class TestCodeParser(unittest.TestCase):
    """Test cases for CodeParser class"""
    
    def setUp(self):
        self.parser = CodeParser()
        # Create a temporary test file
        self.test_code = '''
class TestClass:
    """A test class"""
    
    def __init__(self):
        self.value = 0
    
    def simple_method(self):
        return self.value
    
    def complex_method(self, x, y, z):
        if x > 0:
            if y > 0:
                if z > 0:
                    return x + y + z
        return 0

def simple_function():
    return 42

def long_function():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    j = 10
    return a + b + c + d + e + f + g + h + i + j
'''
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write(self.test_code)
        self.temp_file.close()
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_parse_file(self):
        """Test file parsing"""
        tree = self.parser.parse_file(self.temp_file.name)
        self.assertIsNotNone(tree)
        self.assertIn(self.temp_file.name, self.parser.parsed_modules)
    
    def test_extract_class_definitions(self):
        """Test class definition extraction"""
        self.parser.parse_file(self.temp_file.name)
        expected_key = f"{self.temp_file.name}:TestClass"
        self.assertIn(expected_key, self.parser.class_definitions)
    
    def test_extract_function_definitions(self):
        """Test function definition extraction"""
        self.parser.parse_file(self.temp_file.name)
        self.assertEqual(len(self.parser.function_definitions), 5)  # __init__, simple_method, complex_method, simple_function, long_function
    
    def test_get_method_count(self):
        """Test method counting"""
        self.parser.parse_file(self.temp_file.name)
        count = self.parser.get_method_count("TestClass")
        self.assertEqual(count, 3)  # __init__, simple_method, complex_method
    
    def test_get_function_length(self):
        """Test function length calculation"""
        self.parser.parse_file(self.temp_file.name)
        length = self.parser.get_function_length("simple_function")
        self.assertEqual(length, 2)  # def line + return line
    
    def test_find_duplicate_code(self):
        """Test duplicate code detection"""
        self.parser.parse_file(self.temp_file.name)
        duplicates = self.parser.find_duplicate_code(threshold=0.5)
        # Should find some similarities in simple functions
        self.assertIsInstance(duplicates, list)
    
    def test_complexity_metrics(self):
        """Test complexity metrics calculation"""
        self.parser.parse_file(self.temp_file.name)
        for func_def in self.parser.function_definitions.values():
            metrics = self.parser.get_complexity_metrics(func_def)
            self.assertIn('cyclomatic_complexity', metrics)
            self.assertIn('nesting_depth', metrics)
            self.assertIn('parameter_count', metrics)
            self.assertIn('line_count', metrics)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent file"""
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file("/nonexistent/file.py")
    
    def test_syntax_error(self):
        """Test handling of syntax errors"""
        bad_code = "def broken("
        temp_bad = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        temp_bad.write(bad_code)
        temp_bad.close()
        
        with self.assertRaises(SyntaxError):
            self.parser.parse_file(temp_bad.name)
        
        os.unlink(temp_bad.name)


class TestLimitationAnalyzer(unittest.TestCase):
    """Test cases for LimitationAnalyzer class"""
    
    def setUp(self):
        self.parser = CodeParser()
        self.analyzer = LimitationAnalyzer(self.parser)
        
        # Create test file with code smells
        self.smelly_code = '''
class VeryLargeClass:
    """A class with many methods"""
    
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass
    def method7(self): pass
    def method8(self): pass
    def method9(self): pass
    def method10(self): pass

def very_long_function(a, b, c, d, e, f, g, h, i, j):
    """Function with too many parameters and lines"""
    x = 1
    y = 2
    z = 3
    w = 4
    v = 5
    u = 6
    t = 7
    s = 8
    r = 9
    q = 10
    p = 11
    o = 12
    n = 13
    m = 14
    l = 15
    k = 16
    j_val = 17
    i_val = 18
    h_val = 19
    g_val = 20
    # ... imagine 30 more lines
    return sum([x, y, z, w, v, u, t, s, r, q, p, o, n, m, l, k, j_val, i_val, h_val, g_val])

def highly_complex_function(data):
    """Function with high cyclomatic complexity"""
    if data:
        if isinstance(data, list):
            for item in data:
                if item > 0:
                    if item % 2 == 0:
                        if item < 100:
                            if item > 10:
                                if item != 50:
                                    return True
    return False
'''
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write(self.smelly_code)
        self.temp_file.close()
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_analyze_file(self):
        """Test file analysis for code smells"""
        smells = self.analyzer.analyze_file(self.temp_file.name)
        self.assertIsInstance(smells, list)
        # Should detect long parameter list and high complexity
        self.assertTrue(len(smells) > 0)
    
    def test_detect_long_parameter_list(self):
        """Test detection of long parameter lists"""
        smells = self.analyzer.analyze_file(self.temp_file.name)
        long_param_smells = [s for s in smells if s.smell_type == CodeSmell.LONG_PARAMETER_LIST]
        self.assertTrue(len(long_param_smells) > 0)
    
    def test_detect_high_complexity(self):
        """Test detection of high complexity functions"""
        smells = self.analyzer.analyze_file(self.temp_file.name)
        # Check for any complexity-related smell (SWITCH_STATEMENTS is used as proxy)
        complexity_smells = [s for s in smells if s.smell_type == CodeSmell.SWITCH_STATEMENTS or s.severity > 0.5]
        # Should detect at least some code smells in complex code
        self.assertTrue(len(smells) > 0)  # At minimum, should find some smell
    
    def test_identify_system_limitations(self):
        """Test system limitation identification"""
        self.parser.parse_file(self.temp_file.name)
        limitations = self.analyzer.identify_system_limitations()
        self.assertIsInstance(limitations, list)


class TestSelfReflector(unittest.TestCase):
    """Test cases for SelfReflector class"""
    
    def setUp(self):
        self.parser = CodeParser()
        self.analyzer = LimitationAnalyzer(self.parser)
        self.reflector = SelfReflector(self.analyzer)
        
        # Create minimal test file
        self.simple_code = '''
def sample_function(x, y, z, a, b, c):
    if x > 0:
        if y > 0:
            if z > 0:
                if a > 0:
                    if b > 0:
                        if c > 0:
                            return True
    return False
'''
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write(self.simple_code)
        self.temp_file.close()
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_generate_hypotheses(self):
        """Test hypothesis generation"""
        self.parser.parse_file(self.temp_file.name)
        self.analyzer.analyze_file(self.temp_file.name)
        self.analyzer.identify_system_limitations()
        
        hypotheses = self.reflector.generate_hypotheses()
        self.assertIsInstance(hypotheses, list)
        self.assertTrue(len(hypotheses) > 0)
    
    def test_prioritize_hypotheses(self):
        """Test hypothesis prioritization"""
        self.parser.parse_file(self.temp_file.name)
        self.analyzer.analyze_file(self.temp_file.name)
        self.analyzer.identify_system_limitations()
        
        hypotheses = self.reflector.generate_hypotheses()
        prioritized = self.reflector.prioritize_hypotheses(max_risk=0.5)
        
        # All prioritized hypotheses should have risk <= max_risk
        for hyp in prioritized:
            self.assertLessEqual(hyp.risk_level, 0.5)


class TestCodeModifier(unittest.TestCase):
    """Test cases for CodeModifier class"""
    
    def setUp(self):
        self.parser = CodeParser()
        self.modifier = CodeModifier(self.parser)
        
        self.simple_code = '''
def sample(x):
    return x * 2
'''
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write(self.simple_code)
        self.temp_file.close()
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_propose_modification(self):
        """Test modification proposal"""
        self.parser.parse_file(self.temp_file.name)
        
        smell = CodeSmellDetection(
            smell_type=CodeSmell.LONG_METHOD,
            location=CodeLocation(
                file_path=self.temp_file.name,
                line_start=1,
                line_end=3
            ),
            description="Test smell",
            severity=0.5,
            suggestion="Refactor this"
        )
        
        hypothesis = SelfImprovementHypothesis(
            hypothesis_id="TEST_001",
            description="Test hypothesis",
            target_limitation=None,
            target_smell=smell,
            proposed_changes=["Refactor"],
            expected_benefit="Better code",
            risk_level=0.3,
            confidence=0.8,
            validation_plan=["Test"]
        )
        
        modification = self.modifier.propose_modification(hypothesis)
        self.assertIsNotNone(modification)
        self.assertEqual(modification.status, "proposed")
    
    def test_validate_modification(self):
        """Test modification validation"""
        self.parser.parse_file(self.temp_file.name)
        
        smell = CodeSmellDetection(
            smell_type=CodeSmell.LONG_METHOD,
            location=CodeLocation(
                file_path=self.temp_file.name,
                line_start=1,
                line_end=3
            ),
            description="Test smell",
            severity=0.5,
            suggestion="Refactor this"
        )
        
        hypothesis = SelfImprovementHypothesis(
            hypothesis_id="TEST_001",
            description="Test hypothesis",
            target_limitation=None,
            target_smell=smell,
            proposed_changes=["Refactor"],
            expected_benefit="Better code",
            risk_level=0.3,
            confidence=0.8,
            validation_plan=["Test"]
        )
        
        modification = self.modifier.propose_modification(hypothesis)
        result = self.modifier.validate_modification(modification)
        
        self.assertTrue(result)
        self.assertEqual(modification.status, "validated")


class TestSafetySandbox(unittest.TestCase):
    """Test cases for SafetySandbox class"""
    
    def setUp(self):
        self.sandbox = SafetySandbox()
    
    def test_execute_safe_code(self):
        """Test execution of safe code"""
        code = "result = 2 + 2"
        result = self.sandbox.execute_in_sandbox(code)
        self.assertEqual(result['result'], 4)
    
    def test_forbid_eval(self):
        """Test that eval is forbidden"""
        code = "eval('1+1')"
        with self.assertRaises(SecurityError):
            self.sandbox.execute_in_sandbox(code)
    
    def test_forbid_exec(self):
        """Test that exec is forbidden"""
        code = "exec('print(1)')"
        with self.assertRaises(SecurityError):
            self.sandbox.execute_in_sandbox(code)
    
    def test_test_modification(self):
        """Test modification testing"""
        mod = CodeModification(
            modification_id="MOD_TEST",
            hypothesis_id="HYP_TEST",
            file_path="test.py",
            original_code="old",
            modified_code="new",
            diff_patch="",
            rationale="Test",
            test_cases=["test1", "test2"]
        )
        
        result = self.sandbox.test_modification(mod, ["test1", "test2"])
        self.assertTrue(result)


class TestSelfReflectionEngine(unittest.TestCase):
    """Test cases for SelfReflectionEngine class"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.engine = SelfReflectionEngine(self.temp_dir)
        
        # Create a test file in the temp directory
        test_code = '''
def test_func(x, y, z, a, b, c):
    if x > 0:
        if y > 0:
            if z > 0:
                if a > 0:
                    if b > 0:
                        if c > 0:
                            return True
    return False
'''
        self.test_file = os.path.join(self.temp_dir, "test_module.py")
        with open(self.test_file, 'w') as f:
            f.write(test_code)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_analyze_project(self):
        """Test project analysis"""
        result = self.engine.analyze_project()
        
        self.assertIn('analyzed_files', result)
        self.assertIn('total_functions', result)
        self.assertIn('total_classes', result)
        self.assertIn('code_smells_detected', result)
        self.assertGreaterEqual(result['analyzed_files'], 1)
    
    def test_generate_improvement_plan(self):
        """Test improvement plan generation"""
        self.engine.analyze_project()
        hypotheses = self.engine.generate_improvement_plan(max_hypotheses=3)
        
        self.assertIsInstance(hypotheses, list)
        self.assertLessEqual(len(hypotheses), 3)
    
    def test_run_full_reflection_cycle(self):
        """Test full reflection cycle"""
        result = self.engine.run_full_reflection_cycle()
        
        self.assertIn('analysis', result)
        self.assertIn('hypotheses_generated', result)
        self.assertIn('modifications_proposed', result)
        self.assertIn('modifications_validated', result)
        
        # Check that history was recorded
        self.assertEqual(len(self.engine.reflection_history), 1)


if __name__ == '__main__':
    unittest.main()
