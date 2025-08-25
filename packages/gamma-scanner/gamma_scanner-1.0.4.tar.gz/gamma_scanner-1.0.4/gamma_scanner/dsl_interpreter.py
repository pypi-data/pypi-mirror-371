"""
StringForge DSL Interpreter
Executes compiled AST nodes
"""

import re
import functools
from typing import Any, Dict, List, Optional, Union, Callable
from .dsl_ast import *
from .dsl_builtins import StringForgeBuiltins

class ExecutionContext:
    """Context for DSL execution"""
    
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        self.functions: Dict[str, Callable] = {}
        self.current_text: str = ""
        self.match_results: List[Dict[str, Any]] = []
        self.builtins = StringForgeBuiltins()
        
        # Register built-in functions
        self._register_builtins()
    
    def _register_builtins(self):
        """Register built-in functions"""
        self.functions.update({
            'length': self.builtins.length,
            'count': self.builtins.count,
            'split': self.builtins.split,
            'join': self.builtins.join,
            'upper': self.builtins.upper,
            'lower': self.builtins.lower,
            'strip': self.builtins.strip,
            'replace': self.builtins.replace,
            'extract': self.builtins.extract,
            'regex_compile': self.builtins.regex_compile,
            'regex_match': self.builtins.regex_match,
            'regex_findall': self.builtins.regex_findall,
            'contains': self.builtins.contains,
            'starts_with': self.builtins.starts_with,
            'ends_with': self.builtins.ends_with,
            'substring': self.builtins.substring,
            'reverse': self.builtins.reverse,
            'trim': self.builtins.trim,
            'capitalize': self.builtins.capitalize,
            'title': self.builtins.title,
            'swapcase': self.builtins.swapcase,
            'encode': self.builtins.encode,
            'decode': self.builtins.decode,
            'hash': self.builtins.hash_string,
            'entropy': self.builtins.entropy,
            'similarity': self.builtins.similarity,
            'distance': self.builtins.distance,
        })
    
    def set_variable(self, name: str, value: Any):
        """Set variable value"""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Any:
        """Get variable value"""
        return self.variables.get(name)
    
    def set_current_text(self, text: str):
        """Set current text being processed"""
        self.current_text = text
    
    def add_match_result(self, result: Dict[str, Any]):
        """Add match result"""
        self.match_results.append(result)

class CompiledRule:
    """Compiled rule for efficient execution"""
    
    def __init__(self, name: str, conditions: List[Any], actions: List[Any], metadata: Optional[Any] = None):
        self.name = name
        self.conditions = conditions
        self.actions = actions
        self.metadata = metadata
        self.compiled_regex = {}  # Cache for compiled regex patterns

class StringForgeInterpreter:
    """Interpreter for StringForge DSL"""
    
    def __init__(self):
        self.context = ExecutionContext()
    
    def compile_ast(self, ast: ProgramNode) -> List[CompiledRule]:
        """
        Compile AST into executable rules
        
        Args:
            ast: Program AST node
            
        Returns:
            List of compiled rules
        """
        compiled_rules = []
        
        for statement in ast.statements:
            if isinstance(statement, RuleNode):
                compiled_rule = self._compile_rule(statement)
                compiled_rules.append(compiled_rule)
        
        return compiled_rules
    
    def _compile_rule(self, rule_node: RuleNode) -> CompiledRule:
        """Compile a single rule"""
        compiled_conditions = []
        compiled_actions = []
        
        # Compile conditions
        for condition in rule_node.conditions:
            compiled_cond = self._compile_condition(condition)
            compiled_conditions.append(compiled_cond)
        
        # Compile actions
        for action in rule_node.actions:
            compiled_action = self._compile_action(action)
            compiled_actions.append(compiled_action)
        
        return CompiledRule(rule_node.name, compiled_conditions, compiled_actions, rule_node.metadata)
    
    def _compile_condition(self, condition) -> Dict[str, Any]:
        """Compile a condition node"""
        # Handle different types of condition nodes
        if isinstance(condition, ConditionNode):
            compiled = {
                'type': condition.condition_type,
                'pattern': self._evaluate_expression(condition.pattern),
                'target': self._evaluate_expression(condition.target) if condition.target else None,
                'flags': self._evaluate_expression(condition.flags) if condition.flags else None,
            }
            
            # Pre-compile regex patterns for efficiency
            if condition.condition_type == 'regex_match':
                pattern = compiled['pattern']
                flags = compiled['flags'] or 0
                if isinstance(flags, str):
                    flag_value = 0
                    if 'i' in flags: flag_value |= re.IGNORECASE
                    if 'm' in flags: flag_value |= re.MULTILINE
                    if 's' in flags: flag_value |= re.DOTALL
                    if 'x' in flags: flag_value |= re.VERBOSE
                    flags = flag_value
                
                try:
                    compiled['compiled_regex'] = re.compile(pattern, flags)
                except re.error as e:
                    raise ValueError(f"Invalid regex pattern: {pattern}, error: {e}")
            
            return compiled
        
        elif isinstance(condition, BinaryOpNode):
            # Handle OR/AND expressions
            return {
                'type': 'binary_op',
                'operator': condition.operator,
                'left': self._compile_condition(condition.left),
                'right': self._compile_condition(condition.right)
            }
        
        elif isinstance(condition, FunctionCallNode):
            # Handle function calls like contains(), regex_match(), etc.
            func_name = self._evaluate_expression(condition.function)
            args = [self._evaluate_expression(arg) for arg in condition.arguments]
            
            return {
                'type': 'function_call',
                'function': func_name,
                'arguments': args
            }
        
        else:
            # General expression - evaluate it
            return {
                'type': 'expression',
                'expression': self._evaluate_expression(condition)
            }
    
    def _compile_action(self, action: ActionNode) -> Dict[str, Any]:
        """Compile an action node"""
        return {
            'type': action.action_type,
            'pattern': self._evaluate_expression(action.pattern),
            'replacement': self._evaluate_expression(action.replacement) if action.replacement else None,
            'target': self._evaluate_expression(action.target) if action.target else None,
        }
    
    def execute_rule(self, compiled_rule: CompiledRule, text: str) -> List[Dict[str, Any]]:
        """
        Execute a compiled rule against text
        
        Args:
            compiled_rule: Compiled rule to execute
            text: Text to match against
            
        Returns:
            List of match results
        """
        self.context.set_current_text(text)
        self.context.match_results = []
        
        # Set up string definitions if available from the rule
        self.context.string_definitions = {}
        if hasattr(compiled_rule, 'strings') and compiled_rule.strings:
            if hasattr(compiled_rule.strings, 'string_definitions'):
                for string_def in compiled_rule.strings.string_definitions:
                    if hasattr(string_def, 'identifier') and hasattr(string_def, 'value'):
                        self.context.string_definitions[string_def.identifier] = string_def.value
        
        # Also check if the compiled rule has metadata with string definitions
        if hasattr(compiled_rule, 'metadata') and compiled_rule.metadata:
            # Look for string patterns in metadata or other sources
            pass
        
        # Evaluate all conditions
        any_condition_met = False
        condition_results = []
        
        for condition in compiled_rule.conditions:
            result = self._execute_condition(condition, text)
            condition_results.append(result)
            # If ANY meaningful condition matches, trigger the rule
            if result.get('matched', False):
                any_condition_met = True
                # Add a match result immediately
                self.context.add_match_result({
                    'type': 'rule_match',
                    'rule_name': compiled_rule.name,
                    'condition': condition,
                    'details': result.get('details', {}),
                    'matched_text': text
                })
        
        # If any conditions are met, execute actions
        if any_condition_met:
            for action in compiled_rule.actions:
                self._execute_action(action, text)
        
        return self.context.match_results
    
    def _execute_condition(self, condition: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Execute a single condition"""
        condition_type = condition['type']
        
        # Handle binary operations (OR/AND)
        if condition_type == 'binary_op':
            left_result = self._execute_condition(condition['left'], text)
            right_result = self._execute_condition(condition['right'], text)
            
            if condition['operator'] == 'or':
                matched = left_result.get('matched', False) or right_result.get('matched', False)
            elif condition['operator'] == 'and':
                matched = left_result.get('matched', False) and right_result.get('matched', False)
            else:
                matched = False
            
            return {'matched': matched, 'details': {'left': left_result, 'right': right_result}}
        
        # Handle function calls
        elif condition_type == 'function_call':
            func_name = condition['function']
            args = condition['arguments']
            
            # Execute the function with text as first argument if not provided
            if func_name in self.context.functions:
                try:
                    # Add text as first argument if needed
                    full_args = [text] + args if args else [text]
                    if func_name == 'contains':
                        # For contains, pattern is first arg, text is second
                        full_args = args + [text] if args else [text]
                    
                    result_value = self.context.functions[func_name](*full_args)
                    return {'matched': bool(result_value), 'details': {'function': func_name, 'result': result_value}}
                except Exception as e:
                    return {'matched': False, 'details': {'error': str(e)}}
            else:
                return {'matched': False, 'details': {'error': f'Unknown function: {func_name}'}}
        
        # Handle expression conditions
        elif condition_type == 'expression':
            try:
                result_value = self._evaluate_expression(condition['expression'])
                return {'matched': bool(result_value), 'details': {'result': result_value}}
            except Exception as e:
                return {'matched': False, 'details': {'error': str(e)}}
        
        # Handle traditional condition types
        pattern = condition.get('pattern', '')
        target = condition.get('target', text)
        
        result = {'matched': False, 'details': {}}
        
        try:
            if condition_type == 'match':
                # Simple string matching
                if isinstance(pattern, str) and pattern in target:
                    result['matched'] = True
                    result['details'] = {
                        'position': target.find(pattern),
                        'length': len(pattern),
                        'match_text': pattern
                    }
            
            elif condition_type == 'contains':
                result['matched'] = pattern in target
                if result['matched']:
                    result['details'] = {
                        'position': target.find(pattern),
                        'length': len(pattern),
                        'match_text': pattern
                    }
            
            elif condition_type == 'starts_with':
                result['matched'] = target.startswith(pattern)
                if result['matched']:
                    result['details'] = {
                        'position': 0,
                        'length': len(pattern),
                        'match_text': pattern
                    }
            
            elif condition_type == 'ends_with':
                result['matched'] = target.endswith(pattern)
                if result['matched']:
                    result['details'] = {
                        'position': len(target) - len(pattern),
                        'length': len(pattern),
                        'match_text': pattern
                    }
            
            elif condition_type == 'regex_match':
                compiled_regex = condition.get('compiled_regex')
                if compiled_regex:
                    match = compiled_regex.search(target)
                    if match:
                        result['matched'] = True
                        result['details'] = {
                            'position': match.start(),
                            'length': match.end() - match.start(),
                            'match_text': match.group(0),
                            'groups': list(match.groups()),
                            'groupdict': match.groupdict()
                        }
            
            elif condition_type == 'expression':
                # Evaluate arbitrary expression
                expr_result = self._evaluate_expression(condition['pattern'])
                result['matched'] = bool(expr_result)
                result['details'] = {'expression_result': expr_result}
        
        except Exception as e:
            result['matched'] = False
            result['error'] = str(e)
        
        # Add match result to context if matched
        if result['matched']:
            self.context.add_match_result({
                'type': 'condition',
                'condition_type': condition_type,
                'pattern': pattern,
                'position': result['details'].get('position', -1),
                'length': result['details'].get('length', 0),
                'match_text': result['details'].get('match_text', ''),
                'groups': result['details'].get('groups', []),
                'groupdict': result['details'].get('groupdict', {})
            })
        
        return result
    
    def _execute_action(self, action: Dict[str, Any], text: str):
        """Execute a single action"""
        action_type = action['type']
        pattern = action['pattern']
        replacement = action.get('replacement')
        target = action.get('target', text)
        
        try:
            if action_type == 'replace':
                if replacement is not None:
                    if isinstance(pattern, str):
                        result_text = target.replace(pattern, replacement)
                    else:
                        # Assume regex pattern
                        result_text = re.sub(pattern, replacement, target)
                    
                    self.context.add_match_result({
                        'type': 'action',
                        'action_type': action_type,
                        'original_text': target,
                        'result_text': result_text,
                        'pattern': pattern,
                        'replacement': replacement
                    })
            
            elif action_type == 'extract':
                if isinstance(pattern, str):
                    # Simple string extraction
                    start_idx = target.find(pattern)
                    if start_idx != -1:
                        extracted = target[start_idx:start_idx + len(pattern)]
                        self.context.add_match_result({
                            'type': 'action',
                            'action_type': action_type,
                            'extracted_text': extracted,
                            'position': start_idx,
                            'length': len(pattern)
                        })
                else:
                    # Regex extraction
                    matches = re.findall(pattern, target)
                    for match in matches:
                        self.context.add_match_result({
                            'type': 'action',
                            'action_type': action_type,
                            'extracted_text': match,
                            'pattern': pattern
                        })
            
            elif action_type == 'transform':
                # Apply transformation function
                if callable(pattern):
                    result_text = pattern(target)
                else:
                    # Evaluate transformation expression
                    result_text = self._evaluate_expression(pattern)
                
                self.context.add_match_result({
                    'type': 'action',
                    'action_type': action_type,
                    'original_text': target,
                    'result_text': result_text,
                    'transformation': pattern
                })
        
        except Exception as e:
            self.context.add_match_result({
                'type': 'action_error',
                'action_type': action_type,
                'error': str(e),
                'pattern': pattern
            })
    
    def _evaluate_expression(self, expr: ExpressionNode) -> Any:
        """Evaluate an expression node"""
        if expr is None:
            return None
        
        if isinstance(expr, LiteralNode):
            return expr.value
        
        elif isinstance(expr, IdentifierNode):
            return self.context.get_variable(expr.name)
        
        elif isinstance(expr, BinaryOpNode):
            left = self._evaluate_expression(expr.left)
            right = self._evaluate_expression(expr.right)
            
            if expr.operator == '+':
                return left + right
            elif expr.operator == '-':
                return left - right
            elif expr.operator == '*':
                return left * right
            elif expr.operator == '/':
                return left / right
            elif expr.operator == '%':
                return left % right
            elif expr.operator == '==':
                return left == right
            elif expr.operator == '!=':
                return left != right
            elif expr.operator == '<':
                return left < right
            elif expr.operator == '>':
                return left > right
            elif expr.operator == '<=':
                return left <= right
            elif expr.operator == '>=':
                return left >= right
            elif expr.operator == 'and':
                return left and right
            elif expr.operator == 'or':
                return left or right
            else:
                raise ValueError(f"Unknown binary operator: {expr.operator}")
        
        elif isinstance(expr, UnaryOpNode):
            operand = self._evaluate_expression(expr.operand)
            
            if expr.operator == '-':
                return -operand
            elif expr.operator == 'not':
                return not operand
            else:
                raise ValueError(f"Unknown unary operator: {expr.operator}")
        
        elif isinstance(expr, FunctionCallNode):
            function = self._evaluate_expression(expr.function)
            args = [self._evaluate_expression(arg) for arg in expr.arguments]
            
            if isinstance(function, str) and function in self.context.functions:
                return self.context.functions[function](*args)
            elif callable(function):
                return function(*args)
            else:
                raise ValueError(f"Unknown function: {function}")
        
        elif isinstance(expr, MemberAccessNode):
            obj = self._evaluate_expression(expr.object)
            return getattr(obj, expr.member)
        
        elif isinstance(expr, IndexAccessNode):
            obj = self._evaluate_expression(expr.object)
            index = self._evaluate_expression(expr.index)
            return obj[index]
        
        elif isinstance(expr, ArrayLiteralNode):
            return [self._evaluate_expression(elem) for elem in expr.elements]
        
        # Handle basic types
        elif isinstance(expr, str):
            # String literal - check if it's a variable reference or literal text
            if expr.startswith('$'):
                # YARA-style variable reference - lookup in context  
                var_name = expr[1:]  # Remove $ prefix
                if hasattr(self.context, 'string_definitions') and var_name in self.context.string_definitions:
                    pattern = self.context.string_definitions[var_name]
                    # Perform the actual string matching
                    if isinstance(pattern, str) and pattern in self.context.current_text:
                        return True
                    return False
                return self.context.get_variable(var_name)
            else:
                # Regular string literal - check if it's in the current text
                if hasattr(self.context, 'current_text') and self.context.current_text:
                    return expr in self.context.current_text
                return expr
        
        elif isinstance(expr, (int, float, bool)):
            return expr
        
        elif expr is None:
            return None
        
        # YARA-style expressions
        elif hasattr(expr, '__class__') and 'StringIdentifierNode' in str(expr.__class__):
            # Handle StringIdentifierNode
            return getattr(expr, 'identifier', str(expr))
        
        elif hasattr(expr, '__class__') and 'StringCountNode' in str(expr.__class__):
            # Handle StringCountNode
            return {'type': 'string_count', 'identifier': getattr(expr, 'string_identifier', '')}
        
        elif hasattr(expr, '__class__') and 'FilesizeNode' in str(expr.__class__):
            # Handle FilesizeNode - return current text length
            return len(self.context.current_text) if self.context.current_text else 0
        
        elif hasattr(expr, '__class__') and 'HexStringNode' in str(expr.__class__):
            # Handle HexStringNode
            return {'type': 'hex_pattern', 'pattern': getattr(expr, 'hex_pattern', '')}
        
        else:
            raise ValueError(f"Unknown expression node type: {type(expr)}")
    
    def execute_transformation(self, ast: ProgramNode, text: str) -> str:
        """
        Execute transformation rules on text
        
        Args:
            ast: Program AST containing transformation rules
            text: Input text
            
        Returns:
            Transformed text
        """
        result_text = text
        
        for statement in ast.statements:
            if isinstance(statement, RuleNode):
                compiled_rule = self._compile_rule(statement)
                matches = self.execute_rule(compiled_rule, result_text)
                
                # Apply transformations from match results
                for match in matches:
                    if match.get('type') == 'action' and 'result_text' in match:
                        result_text = match['result_text']
        
        return result_text
