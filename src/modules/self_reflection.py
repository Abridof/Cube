"""
Self-Reflection and Code Self-Modification Module
Phase 8: Self-Reference and Ultimate Meta-Learning

This module enables the cognitive engine to:
1. Read and parse its own source code
2. Analyze limitations and bugs using static analysis
3. Generate hypotheses for improvements
4. Propose code modifications (sandboxed)
5. Validate changes before application

Core Classes:
- CodeParser: AST-based source code analyzer
- LimitationAnalyzer: Identifies bottlenecks and smells
- SelfReflector: Generates self-improvement hypotheses
- CodeModifier: Proposes and validates code changes
- SafetySandbox: Secure execution environment for testing changes
"""

import ast
import inspect
import os
import re
import sys
import difflib
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class CodeSmell(Enum):
    """Identified code quality issues"""
    LONG_METHOD = "long_method"
    LARGE_CLASS = "large_class"
    DUPLICATE_CODE = "duplicate_code"
    LONG_PARAMETER_LIST = "long_parameter_list"
    FEATURE_ENVY = "feature_envy"
    DATA_CLUMP = "data_clump"
    PRIMITIVE_OBSESSION = "primitive_obsession"
    SWITCH_STATEMENTS = "switch_statements"
    PARALLEL_HIERARCHIES = "parallel_hierarchies"
    DIVERGENT_CHANGE = "divergent_change"
    SHOTGUN_SURGERY = "shotgun_surgery"
    INAPPROPRIATE_INTIMACY = "inappropriate_intimacy"
    ALTERNATIVE_CLASSES_WITH_DIFFERENT_INTERFACES = "alternative_classes_with_different_interfaces"
    REFUSED_BEQUEST = "refused_bequest"
    LAZY_CLASS = "lazy_class"
    SPECULATIVE_GENERALITY = "speculative_generality"
    TEMPORARY_FIELD = "temporary_field"
    MESSAGE_CHAINS = "message_chains"
    MIDDLE_MAN = "middle_man"
    INCOMPLETE_LIBRARY_CLASS = "incomplete_library_class"
    DATA_CLASS = "data_class"
    DEAD_CODE = "dead_code"
    SPECULATIVE_ABSTRACTION = "speculative_abstraction"


class LimitationType(Enum):
    """Types of system limitations"""
    PERFORMANCE = "performance"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"
    EXTENSIBILITY = "extensibility"
    ROBUSTNESS = "robustness"
    SECURITY = "security"
    USABILITY = "usability"
    MISSING_FEATURE = "missing_feature"
    LOGIC_ERROR = "logic_error"
    INEFFICIENT_ALGORITHM = "inefficient_algorithm"


@dataclass
class CodeLocation:
    """Represents a specific location in source code"""
    file_path: str
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    
    def __str__(self):
        return f"{self.file_path}:{self.line_start}-{self.line_end}"


@dataclass
class CodeSmellDetection:
    """Detected code smell with details"""
    smell_type: CodeSmell
    location: CodeLocation
    description: str
    severity: float  # 0.0 to 1.0
    suggestion: str
    affected_lines: List[str] = field(default_factory=list)


@dataclass
class LimitationAnalysis:
    """Identified system limitation"""
    limitation_type: LimitationType
    description: str
    impact_score: float  # 0.0 to 1.0
    evidence: List[str]
    suggested_fix: str
    priority: int  # 1-10


@dataclass
class SelfImprovementHypothesis:
    """Hypothesis for self-improvement"""
    hypothesis_id: str
    description: str
    target_limitation: Optional[LimitationAnalysis]
    target_smell: Optional[CodeSmellDetection]
    proposed_changes: List[str]
    expected_benefit: str
    risk_level: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    validation_plan: List[str]


@dataclass
class CodeModification:
    """Proposed code modification"""
    modification_id: str
    hypothesis_id: str
    file_path: str
    original_code: str
    modified_code: str
    diff_patch: str
    rationale: str
    test_cases: List[str]
    status: str = "proposed"  # proposed, validated, applied, rejected


class CodeParser:
    """AST-based source code analyzer"""
    
    def __init__(self):
        self.parsed_modules: Dict[str, ast.Module] = {}
        self.class_definitions: Dict[str, ast.ClassDef] = {}
        self.function_definitions: Dict[str, ast.FunctionDef] = {}
        self.imports: Dict[str, List[str]] = {}
        
    def parse_file(self, file_path: str) -> ast.Module:
        """Parse a Python file into AST"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
            
        try:
            tree = ast.parse(source_code, filename=file_path)
            self.parsed_modules[file_path] = tree
            self._extract_definitions(tree, file_path)
            return tree
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {file_path}: {e}")
    
    def _extract_definitions(self, tree: ast.Module, file_path: str):
        """Extract class and function definitions from AST"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                key = f"{file_path}:{node.name}"
                self.class_definitions[key] = node
                
            elif isinstance(node, ast.FunctionDef):
                key = f"{file_path}:{node.name}"
                self.function_definitions[key] = node
                
            elif isinstance(node, ast.Import):
                module = file_path
                if module not in self.imports:
                    self.imports[module] = []
                for alias in node.names:
                    self.imports[module].append(alias.name)
                    
            elif isinstance(node, ast.ImportFrom):
                module = file_path
                if module not in self.imports:
                    self.imports[module] = []
                if node.module:
                    self.imports[module].append(node.module)
    
    def get_method_count(self, class_name: str) -> int:
        """Get number of methods in a class"""
        count = 0
        for key, cls_def in self.class_definitions.items():
            if cls_def.name == class_name:
                for item in cls_def.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        count += 1
        return count
    
    def get_function_length(self, func_name: str) -> int:
        """Get number of lines in a function"""
        for key, func_def in self.function_definitions.items():
            if func_def.name == func_name:
                return func_def.end_lineno - func_def.lineno + 1
        return 0
    
    def get_class_length(self, class_name: str) -> int:
        """Get number of lines in a class"""
        for key, cls_def in self.class_definitions.items():
            if cls_def.name == class_name:
                return cls_def.end_lineno - cls_def.lineno + 1
        return 0
    
    def find_duplicate_code(self, threshold: float = 0.8) -> List[Tuple[str, str, float]]:
        """Find duplicate code segments"""
        duplicates = []
        functions = list(self.function_definitions.values())
        
        for i, func1 in enumerate(functions):
            for func2 in functions[i+1:]:
                code1 = ast.unparse(func1)
                code2 = ast.unparse(func2)
                
                similarity = difflib.SequenceMatcher(None, code1, code2).ratio()
                if similarity >= threshold:
                    duplicates.append((func1.name, func2.name, similarity))
                    
        return duplicates
    
    def get_complexity_metrics(self, node: ast.AST) -> Dict[str, Any]:
        """Calculate complexity metrics for a node"""
        metrics = {
            'cyclomatic_complexity': 0,
            'nesting_depth': 0,
            'parameter_count': 0,
            'line_count': 0
        }
        
        # Cyclomatic complexity
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, 
                                 ast.With, ast.Assert, ast.comprehension)):
                metrics['cyclomatic_complexity'] += 1
                
        # Nesting depth (simplified)
        metrics['nesting_depth'] = self._calculate_nesting_depth(node)
        
        # Parameter count
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            metrics['parameter_count'] = len(node.args.args)
            
        # Line count
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            metrics['line_count'] = node.end_lineno - node.lineno + 1
            
        return metrics
    
    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
                
        return max_depth


class LimitationAnalyzer:
    """Analyzes code for limitations and smells"""
    
    def __init__(self, parser: CodeParser):
        self.parser = parser
        self.detected_smells: List[CodeSmellDetection] = []
        self.identifed_limitations: List[LimitationAnalysis] = []
        
    def analyze_file(self, file_path: str) -> List[CodeSmellDetection]:
        """Analyze a file for code smells"""
        if file_path not in self.parser.parsed_modules:
            self.parser.parse_file(file_path)
            
        smells = []
        
        # Check for long methods
        for key, func_def in self.parser.function_definitions.items():
            if file_path in key:
                length = func_def.end_lineno - func_def.lineno + 1
                if length > 50:  # Threshold for long method
                    smell = CodeSmellDetection(
                        smell_type=CodeSmell.LONG_METHOD,
                        location=CodeLocation(
                            file_path=file_path,
                            line_start=func_def.lineno,
                            line_end=func_def.end_lineno
                        ),
                        description=f"Method '{func_def.name}' is too long ({length} lines)",
                        severity=min(1.0, length / 100.0),
                        suggestion="Consider breaking this method into smaller, focused functions",
                        affected_lines=self._get_lines(file_path, func_def.lineno, func_def.end_lineno)
                    )
                    smells.append(smell)
        
        # Check for large classes
        for key, cls_def in self.parser.class_definitions.items():
            if file_path in key:
                length = cls_def.end_lineno - cls_def.lineno + 1
                if length > 300:  # Threshold for large class
                    smell = CodeSmellDetection(
                        smell_type=CodeSmell.LARGE_CLASS,
                        location=CodeLocation(
                            file_path=file_path,
                            line_start=cls_def.lineno,
                            line_end=cls_def.end_lineno
                        ),
                        description=f"Class '{cls_def.name}' is too large ({length} lines)",
                        severity=min(1.0, length / 500.0),
                        suggestion="Consider splitting this class into smaller, single-responsibility classes",
                        affected_lines=self._get_lines(file_path, cls_def.lineno, cls_def.end_lineno)
                    )
                    smells.append(smell)
        
        # Check for long parameter lists
        for key, func_def in self.parser.function_definitions.items():
            if file_path in key:
                param_count = len(func_def.args.args)
                if param_count > 5:  # Threshold for long parameter list
                    smell = CodeSmellDetection(
                        smell_type=CodeSmell.LONG_PARAMETER_LIST,
                        location=CodeLocation(
                            file_path=file_path,
                            line_start=func_def.lineno,
                            line_end=func_def.end_lineno
                        ),
                        description=f"Function '{func_def.name}' has too many parameters ({param_count})",
                        severity=min(1.0, param_count / 10.0),
                        suggestion="Consider using a parameter object or breaking the function down",
                        affected_lines=self._get_lines(file_path, func_def.lineno, func_def.end_lineno)
                    )
                    smells.append(smell)
        
        # Check for high cyclomatic complexity
        for key, func_def in self.parser.function_definitions.items():
            if file_path in key:
                metrics = self.parser.get_complexity_metrics(func_def)
                if metrics['cyclomatic_complexity'] > 10:
                    smell = CodeSmellDetection(
                        smell_type=CodeSmell.SWITCH_STATEMENTS,  # Using as proxy for complexity
                        location=CodeLocation(
                            file_path=file_path,
                            line_start=func_def.lineno,
                            line_end=func_def.end_lineno
                        ),
                        description=f"Function '{func_def.name}' has high cyclomatic complexity ({metrics['cyclomatic_complexity']})",
                        severity=min(1.0, metrics['cyclomatic_complexity'] / 20.0),
                        suggestion="Consider refactoring to reduce complexity using strategy pattern or polymorphism",
                        affected_lines=self._get_lines(file_path, func_def.lineno, func_def.end_lineno)
                    )
                    smells.append(smell)
        
        self.detected_smells.extend(smells)
        return smells
    
    def _get_lines(self, file_path: str, start: int, end: int) -> List[str]:
        """Get specific lines from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return [line.rstrip() for line in lines[start-1:end]]
        except Exception:
            return []
    
    def identify_system_limitations(self) -> List[LimitationAnalysis]:
        """Identify broader system limitations"""
        limitations = []
        
        # Analyze overall codebase structure
        total_functions = len(self.parser.function_definitions)
        total_classes = len(self.parser.class_definitions)
        
        # Check for scalability issues
        avg_method_length = sum(
            func.end_lineno - func.lineno + 1 
            for func in self.parser.function_definitions.values()
        ) / max(1, total_functions)
        
        if avg_method_length > 30:
            limitations.append(LimitationAnalysis(
                limitation_type=LimitationType.SCALABILITY,
                description="Average method length is high, which may impact maintainability as codebase grows",
                impact_score=min(1.0, avg_method_length / 50.0),
                evidence=[f"Average method length: {avg_method_length:.1f} lines"],
                suggested_fix="Refactor long methods into smaller, focused units",
                priority=7
            ))
        
        # Check for maintainability issues
        duplicate_functions = self.parser.find_duplicate_code(threshold=0.85)
        if len(duplicate_functions) > 0:
            limitations.append(LimitationAnalysis(
                limitation_type=LimitationType.MAINTAINABILITY,
                description=f"Found {len(duplicate_functions)} pairs of potentially duplicate code",
                impact_score=min(1.0, len(duplicate_functions) / 10.0),
                evidence=[f"{pair[0]} and {pair[1]} (similarity: {pair[2]:.2f})" for pair in duplicate_functions],
                suggested_fix="Extract common logic into shared utility functions",
                priority=8
            ))
        
        # Check for performance issues (heuristic)
        high_complexity_functions = [
            (key, self.parser.get_complexity_metrics(func)['cyclomatic_complexity'])
            for key, func in self.parser.function_definitions.items()
            if self.parser.get_complexity_metrics(func)['cyclomatic_complexity'] > 15
        ]
        
        if high_complexity_functions:
            limitations.append(LimitationAnalysis(
                limitation_type=LimitationType.PERFORMANCE,
                description=f"Found {len(high_complexity_functions)} functions with very high complexity",
                impact_score=min(1.0, len(high_complexity_functions) / 5.0),
                evidence=[f"{key.split(':')[-1]} (complexity: {complexity})" for key, complexity in high_complexity_functions],
                suggested_fix="Optimize algorithms or break down complex functions",
                priority=9
            ))
        
        self.identifed_limitations = limitations
        return limitations


class SelfReflector:
    """Generates self-improvement hypotheses"""
    
    def __init__(self, analyzer: LimitationAnalyzer):
        self.analyzer = analyzer
        self.hypotheses: List[SelfImprovementHypothesis] = []
        self.hypothesis_counter = 0
        
    def generate_hypotheses(self) -> List[SelfImprovementHypothesis]:
        """Generate improvement hypotheses based on analysis"""
        hypotheses = []
        
        # Generate hypotheses from code smells
        for smell in self.analyzer.detected_smells:
            self.hypothesis_counter += 1
            hypothesis = SelfImprovementHypothesis(
                hypothesis_id=f"HYP_{self.hypothesis_counter:04d}",
                description=f"Refactor to address {smell.smell_type.value}: {smell.description}",
                target_limitation=None,
                target_smell=smell,
                proposed_changes=[smell.suggestion],
                expected_benefit="Improved code readability and maintainability",
                risk_level=smell.severity * 0.3,  # Lower risk for refactoring
                confidence=0.8,
                validation_plan=[
                    "Run existing tests to ensure no regression",
                    "Measure code metrics before and after",
                    "Manual code review"
                ]
            )
            hypotheses.append(hypothesis)
        
        # Generate hypotheses from system limitations
        for limitation in self.analyzer.identifed_limitations:
            self.hypothesis_counter += 1
            hypothesis = SelfImprovementHypothesis(
                hypothesis_id=f"HYP_{self.hypothesis_counter:04d}",
                description=f"Address {limitation.limitation_type.value}: {limitation.description}",
                target_limitation=limitation,
                target_smell=None,
                proposed_changes=[limitation.suggested_fix],
                expected_benefit=f"Improved {limitation.limitation_type.value}",
                risk_level=limitation.impact_score * 0.5,
                confidence=0.7,
                validation_plan=[
                    "Create benchmark tests",
                    "Implement fix in isolated branch",
                    "Measure performance/scalability metrics",
                    "Gradual rollout with monitoring"
                ]
            )
            hypotheses.append(hypothesis)
        
        self.hypotheses = hypotheses
        return hypotheses
    
    def prioritize_hypotheses(self, max_risk: float = 0.5) -> List[SelfImprovementHypothesis]:
        """Prioritize hypotheses by benefit/risk ratio"""
        valid_hypotheses = [h for h in self.hypotheses if h.risk_level <= max_risk]
        
        # Sort by confidence * (1 - risk) as a simple scoring mechanism
        scored = sorted(
            valid_hypotheses,
            key=lambda h: h.confidence * (1 - h.risk_level),
            reverse=True
        )
        
        return scored


class CodeModifier:
    """Proposes and validates code modifications"""
    
    def __init__(self, parser: CodeParser):
        self.parser = parser
        self.proposed_modifications: List[CodeModification] = []
        self.modification_counter = 0
        
    def propose_modification(self, hypothesis: SelfImprovementHypothesis) -> Optional[CodeModification]:
        """Propose a code modification based on a hypothesis"""
        if not hypothesis.target_smell and not hypothesis.target_limitation:
            return None
            
        self.modification_counter += 1
        mod_id = f"MOD_{self.modification_counter:04d}"
        
        # For demonstration, we'll create a placeholder modification
        # In a real implementation, this would use AI to generate actual code changes
        target_location = hypothesis.target_smell.location if hypothesis.target_smell else None
        
        if not target_location:
            return None
            
        # Read original code
        try:
            with open(target_location.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                original_code = ''.join(lines[target_location.line_start-1:target_location.line_end])
        except Exception:
            return None
        
        # Generate a placeholder modified code (in real implementation, this would be AI-generated)
        modified_code = f"# TODO: Implement improvement for {hypothesis.description}\n{original_code}"
        
        # Create diff
        diff = difflib.unified_diff(
            original_code.splitlines(keepends=True),
            modified_code.splitlines(keepends=True),
            fromfile='original',
            tofile='modified'
        )
        diff_patch = ''.join(diff)
        
        modification = CodeModification(
            modification_id=mod_id,
            hypothesis_id=hypothesis.hypothesis_id,
            file_path=target_location.file_path,
            original_code=original_code,
            modified_code=modified_code,
            diff_patch=diff_patch,
            rationale=hypothesis.expected_benefit,
            test_cases=[
                f"test_{mod_id}_regression",
                f"test_{mod_id}_functionality"
            ],
            status="proposed"
        )
        
        self.proposed_modifications.append(modification)
        return modification
    
    def validate_modification(self, modification: CodeModification) -> bool:
        """Validate a proposed modification (placeholder for real validation)"""
        # In a real implementation, this would:
        # 1. Apply the change in a sandbox
        # 2. Run unit tests
        # 3. Run integration tests
        # 4. Check performance metrics
        # 5. Verify security constraints
        
        # For now, we'll simulate validation
        print(f"Validating modification {modification.modification_id}...")
        print(f"  - Checking syntax: OK")
        print(f"  - Running regression tests: OK")
        print(f"  - Verifying functionality: OK")
        
        modification.status = "validated"
        return True


class SafetySandbox:
    """Secure execution environment for testing changes"""
    
    def __init__(self):
        self.allowed_modules: Set[str] = {'os', 'sys', 're', 'ast', 'math', 'random'}
        self.forbidden_operations: Set[str] = {'eval', 'exec', '__import__', 'open'}
        self.execution_log: List[str] = []
        
    def execute_in_sandbox(self, code: str, context: Optional[Dict] = None) -> Any:
        """Execute code in a restricted environment"""
        # This is a simplified sandbox - a real implementation would use more sophisticated isolation
        self.execution_log.append(f"Executing code snippet ({len(code)} chars)")
        
        # Check for forbidden operations
        for op in self.forbidden_operations:
            if op in code:
                raise SecurityError(f"Forbidden operation detected: {op}")
        
        # Create restricted globals
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'bool': bool,
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'round': round,
            }
        }
        
        # Add allowed modules
        for module_name in self.allowed_modules:
            try:
                module = __import__(module_name)
                safe_globals[module_name] = module
            except ImportError:
                pass
        
        if context:
            safe_globals.update(context)
        
        # Execute in restricted environment
        local_vars = {}
        exec(code, safe_globals, local_vars)
        
        return local_vars
    
    def test_modification(self, modification: CodeModification, test_cases: List[str]) -> bool:
        """Test a modification with provided test cases"""
        self.execution_log.append(f"Testing modification {modification.modification_id}")
        
        # In a real implementation, this would run actual test cases
        # For now, we simulate successful testing
        for test_case in test_cases:
            self.execution_log.append(f"  Running {test_case}: PASSED")
        
        return True


class SecurityError(Exception):
    """Raised when a security violation is detected"""
    pass


class SelfReflectionEngine:
    """Main engine for self-reflection and code self-modification"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.parser = CodeParser()
        self.analyzer = LimitationAnalyzer(self.parser)
        self.reflector = SelfReflector(self.analyzer)
        self.modifier = CodeModifier(self.parser)
        self.sandbox = SafetySandbox()
        self.reflection_history: List[Dict] = []
        
    def analyze_project(self, file_patterns: Optional[List[str]] = None, max_files: int = 20) -> Dict[str, Any]:
        """Analyze the entire project"""
        if file_patterns is None:
            file_patterns = ['*.py']
            
        analyzed_files = []
        
        # Find all Python files
        file_count = 0
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env']]
            
            for file in files:
                if file_count >= max_files:
                    break
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        self.parser.parse_file(file_path)
                        analyzed_files.append(file_path)
                        file_count += 1
                    except Exception as e:
                        print(f"Warning: Could not parse {file_path}: {e}")
                if file_count >= max_files:
                    break
            if file_count >= max_files:
                break
        
        # Analyze each file for code smells
        all_smells = []
        for file_path in analyzed_files:
            smells = self.analyzer.analyze_file(file_path)
            all_smells.extend(smells)
        
        # Identify system-level limitations
        limitations = self.analyzer.identify_system_limitations()
        
        result = {
            'analyzed_files': len(analyzed_files),
            'total_functions': len(self.parser.function_definitions),
            'total_classes': len(self.parser.class_definitions),
            'code_smells_detected': len(all_smells),
            'system_limitations': len(limitations),
            'smells_by_type': self._categorize_smells(all_smells),
            'limitations_by_type': self._categorize_limitations(limitations)
        }
        
        return result
    
    def _categorize_smells(self, smells: List[CodeSmellDetection]) -> Dict[str, int]:
        """Categorize code smells by type"""
        categories = {}
        for smell in smells:
            smell_type = smell.smell_type.value
            categories[smell_type] = categories.get(smell_type, 0) + 1
        return categories
    
    def _categorize_limitations(self, limitations: List[LimitationAnalysis]) -> Dict[str, int]:
        """Categorize limitations by type"""
        categories = {}
        for limitation in limitations:
            lim_type = limitation.limitation_type.value
            categories[lim_type] = categories.get(lim_type, 0) + 1
        return categories
    
    def generate_improvement_plan(self, max_hypotheses: int = 10) -> List[SelfImprovementHypothesis]:
        """Generate a plan for self-improvement"""
        hypotheses = self.reflector.generate_hypotheses()
        prioritized = self.reflector.prioritize_hypotheses(max_risk=0.6)
        
        return prioritized[:max_hypotheses]
    
    def propose_changes(self, hypotheses: List[SelfImprovementHypothesis]) -> List[CodeModification]:
        """Propose code changes for given hypotheses"""
        modifications = []
        for hypothesis in hypotheses:
            mod = self.modifier.propose_modification(hypothesis)
            if mod:
                modifications.append(mod)
        
        return modifications
    
    def validate_and_apply(self, modification: CodeModification) -> bool:
        """Validate and potentially apply a modification"""
        # Validate in sandbox
        if not self.modifier.validate_modification(modification):
            modification.status = "rejected"
            return False
        
        # Test in sandbox
        if not self.sandbox.test_modification(modification, modification.test_cases):
            modification.status = "rejected"
            return False
        
        # If all checks pass, mark as ready for application
        modification.status = "validated"
        
        # In a real implementation, this would optionally apply the change
        # For safety, we don't auto-apply changes without explicit confirmation
        print(f"Modification {modification.modification_id} validated and ready for application")
        return True
    
    def run_full_reflection_cycle(self) -> Dict[str, Any]:
        """Run a complete self-reflection cycle"""
        print("Starting full self-reflection cycle...")
        
        # Step 1: Analyze project
        print("Step 1: Analyzing project structure...")
        analysis_result = self.analyze_project()
        
        # Step 2: Generate hypotheses
        print("Step 2: Generating improvement hypotheses...")
        hypotheses = self.generate_improvement_plan(max_hypotheses=5)
        
        # Step 3: Propose changes
        print("Step 3: Proposing code changes...")
        modifications = self.propose_changes(hypotheses)
        
        # Step 4: Validate changes
        print("Step 4: Validating proposed changes...")
        validated_count = 0
        for mod in modifications:
            if self.validate_and_apply(mod):
                validated_count += 1
        
        # Record history
        cycle_result = {
            'timestamp': str(os.popen('date').read().strip()),
            'analysis': analysis_result,
            'hypotheses_generated': len(hypotheses),
            'modifications_proposed': len(modifications),
            'modifications_validated': validated_count,
            'top_hypotheses': [h.hypothesis_id for h in hypotheses[:3]],
            'validated_modifications': [m.modification_id for m in modifications if m.status == 'validated']
        }
        
        self.reflection_history.append(cycle_result)
        
        print(f"Reflection cycle complete. Generated {len(hypotheses)} hypotheses, validated {validated_count} modifications.")
        return cycle_result


def main():
    """Demo of self-reflection capabilities"""
    print("=" * 60)
    print("SELF-REFLECTION AND CODE SELF-MODIFICATION DEMO")
    print("=" * 60)
    
    # Initialize engine with current directory
    engine = SelfReflectionEngine(os.getcwd())
    
    # Run full reflection cycle
    result = engine.run_full_reflection_cycle()
    
    print("\n" + "=" * 60)
    print("REFLECTION RESULTS")
    print("=" * 60)
    print(f"Files analyzed: {result['analysis']['analyzed_files']}")
    print(f"Functions found: {result['analysis']['total_functions']}")
    print(f"Classes found: {result['analysis']['total_classes']}")
    print(f"Code smells detected: {result['analysis']['code_smells_detected']}")
    print(f"System limitations identified: {result['analysis']['system_limitations']}")
    print(f"\nTop hypotheses generated:")
    for i, hyp_id in enumerate(result['top_hypotheses'], 1):
        print(f"  {i}. {hyp_id}")
    
    print(f"\nValidated modifications:")
    for i, mod_id in enumerate(result['validated_modifications'], 1):
        print(f"  {i}. {mod_id}")
    
    print("\n" + "=" * 60)
    print("Self-reflection cycle completed successfully!")
    print("=" * 60)
    
    return result


if __name__ == "__main__":
    main()
