"""
StringForge DSL Engine
High-level interface for the DSL execution and optimization
"""

import time
import threading
from typing import Any, Dict, List, Optional, Union, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from .dsl_interpreter import StringForgeInterpreter, CompiledRule
from .dsl_builtins import StringForgeBuiltins

class PerformanceStats:
    """Performance statistics for DSL execution"""
    
    def __init__(self):
        self.total_executions = 0
        self.total_time = 0.0
        self.rule_stats = {}
        self.average_time = 0.0
        self.max_time = 0.0
        self.min_time = float('inf')
    
    def add_execution(self, rule_name: str, execution_time: float):
        """Add execution statistics"""
        self.total_executions += 1
        self.total_time += execution_time
        self.average_time = self.total_time / self.total_executions
        
        if execution_time > self.max_time:
            self.max_time = execution_time
        if execution_time < self.min_time:
            self.min_time = execution_time
        
        if rule_name not in self.rule_stats:
            self.rule_stats[rule_name] = {
                'executions': 0,
                'total_time': 0.0,
                'average_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf')
            }
        
        stats = self.rule_stats[rule_name]
        stats['executions'] += 1
        stats['total_time'] += execution_time
        stats['average_time'] = stats['total_time'] / stats['executions']
        
        if execution_time > stats['max_time']:
            stats['max_time'] = execution_time
        if execution_time < stats['min_time']:
            stats['min_time'] = execution_time
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'total_executions': self.total_executions,
            'total_time': self.total_time,
            'average_time': self.average_time,
            'max_time': self.max_time,
            'min_time': self.min_time if self.min_time != float('inf') else 0.0,
            'rules': self.rule_stats
        }

class StringForgeEngine:
    """High-performance engine for StringForge DSL execution"""
    
    def __init__(self, max_workers: int = 4, enable_caching: bool = True):
        self.interpreter = StringForgeInterpreter()
        self.builtins = StringForgeBuiltins()
        self.max_workers = max_workers
        self.enable_caching = enable_caching
        self.cache = {} if enable_caching else None
        self.stats = PerformanceStats()
        self.compiled_rules = {}
        self._lock = threading.Lock()
    
    def execute_rule(self, compiled_rule: CompiledRule, text: str) -> List[Dict[str, Any]]:
        """
        Execute a single compiled rule against text
        
        Args:
            compiled_rule: Compiled rule to execute
            text: Text to match against
            
        Returns:
            List of match results
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = None
        if self.enable_caching:
            cache_key = f"{compiled_rule.name}:{hash(text)}"
            if cache_key in self.cache:
                execution_time = time.time() - start_time
                self.stats.add_execution(compiled_rule.name, execution_time)
                return self.cache[cache_key]
        
        # Execute rule
        try:
            results = self.interpreter.execute_rule(compiled_rule, text)
            
            # Cache results
            if self.enable_caching and cache_key:
                with self._lock:
                    self.cache[cache_key] = results
            
            execution_time = time.time() - start_time
            self.stats.add_execution(compiled_rule.name, execution_time)
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.stats.add_execution(compiled_rule.name, execution_time)
            
            return [{
                'type': 'error',
                'rule_name': compiled_rule.name,
                'error': str(e),
                'execution_time': execution_time
            }]
    
    def execute_rules_parallel(self, compiled_rules: List[CompiledRule], text: str) -> List[Dict[str, Any]]:
        """
        Execute multiple rules in parallel
        
        Args:
            compiled_rules: List of compiled rules
            text: Text to match against
            
        Returns:
            Combined list of match results
        """
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all rule executions
            future_to_rule = {
                executor.submit(self.execute_rule, rule, text): rule
                for rule in compiled_rules
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_rule):
                rule = future_to_rule[future]
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    all_results.append({
                        'type': 'error',
                        'rule_name': rule.name,
                        'error': str(e)
                    })
        
        return all_results
    
    def execute_transformation(self, ast, text: str) -> str:
        """
        Execute transformation rules on text
        
        Args:
            ast: Program AST containing transformation rules
            text: Input text
            
        Returns:
            Transformed text
        """
        return self.interpreter.execute_transformation(ast, text)
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive text analysis with automatic encoding detection
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results dictionary with encoding detection
        """
        # Get automatic encoding detection and decoding
        encoding_results = self.builtins.auto_decode_and_analyze(text)
        
        # Analyze original text
        analysis = {
            'basic_stats': self._get_basic_stats(text),
            'character_analysis': self._analyze_characters(text),
            'pattern_analysis': self._analyze_patterns(text),
            'pattern_detection': self._analyze_patterns_with_decoding(text, encoding_results),
            'entropy': self.builtins.entropy(text),
            'extracted_data': self._extract_common_data(text),
            'encoding_analysis': {
                'detected_encodings': encoding_results['decoded_variants'],
                'all_decoded_content': encoding_results['all_content'],
                'has_encoded_content': len(encoding_results['decoded_variants']) > 0
            }
        }
        
        return analysis
    
    def _get_basic_stats(self, text: str) -> Dict[str, Any]:
        """Get basic text statistics"""
        text = str(text)
        words = text.split()
        lines = text.split('\n')
        
        return {
            'length': len(text),
            'word_count': len(words),
            'line_count': len(lines),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0,
            'whitespace_count': sum(1 for c in text if c.isspace()),
            'alphabetic_count': sum(1 for c in text if c.isalpha()),
            'numeric_count': sum(1 for c in text if c.isnumeric()),
            'punctuation_count': sum(1 for c in text if not c.isalnum() and not c.isspace())
        }
    
    def _analyze_characters(self, text: str) -> Dict[str, Any]:
        """Analyze character distribution"""
        from collections import Counter
        
        text = str(text)
        char_counts = Counter(text)
        
        # Get most and least common characters
        most_common = char_counts.most_common(10)
        least_common = char_counts.most_common()[-10:] if len(char_counts) > 10 else []
        
        # Character type distribution
        char_types = {
            'uppercase': sum(1 for c in text if c.isupper()),
            'lowercase': sum(1 for c in text if c.islower()),
            'digits': sum(1 for c in text if c.isdigit()),
            'spaces': sum(1 for c in text if c.isspace()),
            'punctuation': sum(1 for c in text if not c.isalnum() and not c.isspace()),
            'control': sum(1 for c in text if ord(c) < 32),
            'extended_ascii': sum(1 for c in text if ord(c) > 127)
        }
        
        return {
            'unique_characters': len(char_counts),
            'most_common': most_common,
            'least_common': least_common,
            'character_types': char_types
        }
    
    def _analyze_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze text patterns"""
        patterns = self.builtins.find_patterns(text, min_length=3, min_occurrences=2)
        
        # Find common word patterns
        words = text.split()
        word_patterns = self.builtins.find_patterns(' '.join(words), min_length=2, min_occurrences=2)
        
        return {
            'repeated_substrings': patterns[:20],  # Top 20 patterns
            'repeated_word_sequences': word_patterns[:10],  # Top 10 word patterns
            'pattern_density': len(patterns) / len(text) if text else 0
        }
    
    def _analyze_patterns_with_decoding(self, text: str, encoding_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text for patterns including decoded variants"""
        import re
        
        # Analyze original text and all decoded variants
        all_content = encoding_results['all_content']
        combined_patterns = {}
        
        for content in all_content:
            content = str(content)
            
            # Pattern detection (no risk scoring)
            patterns = {
                'sql_keywords': len(re.findall(r'(\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b|\bDROP\b|\bUNION\b)', content, re.IGNORECASE)),
                'script_tags': len(re.findall(r'<script|javascript:|onload=|onerror=', content, re.IGNORECASE)),
                'path_traversal': len(re.findall(r'\.\./|\.\.\\\|%2e%2e', content, re.IGNORECASE)),
                'command_patterns': len(re.findall(r';\s*(cat|ls|pwd|whoami|id)\s|`.*`|\$\(.*\)', content, re.IGNORECASE)),
                'base64_strings': len(re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', content)),
                'hex_strings': len(re.findall(r'0x[a-fA-F0-9]{8,}|[a-fA-F0-9]{32,}', content)),
                'urls_with_keywords': len(re.findall(r'https?://[^\s]*(?:eval|exec|shell|cmd|payload)', content, re.IGNORECASE)),
                'ignore_instructions': len(re.findall(r'(ignore|disregard|forget).{0,10}(all|previous|prior).{0,10}(instruction|prompt|rule)', content, re.IGNORECASE)),
                'role_keywords': len(re.findall(r'(you are now|act as|pretend).{0,10}(dan|evil|unrestricted)', content, re.IGNORECASE)),
                'override_keywords': len(re.findall(r'(override|bypass|disable).{0,10}(safety|security|filter)', content, re.IGNORECASE))
            }
            
            # Combine results (take maximum from any variant)
            for pattern_name, count in patterns.items():
                combined_patterns[pattern_name] = max(combined_patterns.get(pattern_name, 0), count)
        
        return {
            'patterns': combined_patterns
        }
    
    def _extract_common_data(self, text: str) -> Dict[str, List[str]]:
        """Extract common data types from text"""
        return {
            'emails': self.builtins.extract_emails(text),
            'urls': self.builtins.extract_urls(text),
            'ip_addresses': self.builtins.extract_ips(text),
            'phone_numbers': self.builtins.extract_phone_numbers(text)
        }
    
    def optimize_rules(self, rules: List[CompiledRule]) -> List[CompiledRule]:
        """
        Optimize compiled rules for better performance
        
        Args:
            rules: List of compiled rules to optimize
            
        Returns:
            Optimized rules
        """
        optimized_rules = []
        
        for rule in rules:
            optimized_rule = self._optimize_single_rule(rule)
            optimized_rules.append(optimized_rule)
        
        # Sort rules by expected performance (simple heuristic)
        optimized_rules.sort(key=self._estimate_rule_cost)
        
        return optimized_rules
    
    def _optimize_single_rule(self, rule: CompiledRule) -> CompiledRule:
        """Optimize a single rule"""
        # Simple optimizations:
        # 1. Pre-compile regex patterns
        # 2. Reorder conditions by expected selectivity
        # 3. Cache common patterns
        
        optimized_conditions = []
        for condition in rule.conditions:
            if condition.get('type') == 'regex_match' and 'compiled_regex' not in condition:
                pattern = condition['pattern']
                flags = condition.get('flags', 0)
                try:
                    import re
                    condition['compiled_regex'] = re.compile(pattern, flags or 0)
                except re.error:
                    pass  # Keep original condition if regex compilation fails
            
            optimized_conditions.append(condition)
        
        # Sort conditions by estimated selectivity (simple heuristic)
        optimized_conditions.sort(key=self._estimate_condition_selectivity)
        
        return CompiledRule(rule.name, optimized_conditions, rule.actions)
    
    def _estimate_rule_cost(self, rule: CompiledRule) -> float:
        """Estimate execution cost of a rule (lower is better)"""
        cost = 0.0
        
        for condition in rule.conditions:
            if condition.get('type') == 'regex_match':
                cost += 10.0  # Regex is more expensive
            elif condition.get('type') in ['contains', 'starts_with', 'ends_with']:
                cost += 1.0   # Simple string operations are cheap
            else:
                cost += 5.0   # Default cost
        
        for action in rule.actions:
            if action.get('type') == 'replace':
                cost += 3.0
            elif action.get('type') == 'extract':
                cost += 2.0
            else:
                cost += 1.0
        
        return cost
    
    def _estimate_condition_selectivity(self, condition: Dict[str, Any]) -> float:
        """Estimate selectivity of a condition (lower means more selective)"""
        condition_type = condition.get('type', '')
        
        # More selective conditions should run first
        if condition_type == 'starts_with':
            return 1.0  # Very selective
        elif condition_type == 'ends_with':
            return 2.0  # Very selective
        elif condition_type == 'contains':
            return 3.0  # Moderately selective
        elif condition_type == 'regex_match':
            return 5.0  # Depends on pattern complexity
        else:
            return 10.0  # Default
    
    def clear_cache(self):
        """Clear the execution cache"""
        if self.enable_caching:
            with self._lock:
                self.cache.clear()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.stats.get_summary()
    
    def reset_stats(self):
        """Reset performance statistics"""
        self.stats = PerformanceStats()
