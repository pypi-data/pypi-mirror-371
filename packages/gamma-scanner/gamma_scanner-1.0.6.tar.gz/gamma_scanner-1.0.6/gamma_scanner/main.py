#!/usr/bin/env python3
"""
Gamma Scanner - Advanced String Manipulation and Pattern Matching
A Python-based security pattern detection engine
"""

import sys
import os
from typing import Optional, Dict, Any, List
from .dsl_engine import StringForgeEngine
from .dsl_interpreter import StringForgeInterpreter
from .dsl_parser import StringForgeParser
from .dsl_lexer import StringForgeLexer

class GammaScanner:
    """Main Gamma Scanner class providing the primary interface"""
    
    def __init__(self):
        self.lexer = StringForgeLexer()
        self.parser = StringForgeParser()
        self.interpreter = StringForgeInterpreter()
        self.engine = StringForgeEngine()
        self.compiled_rules: Dict[str, Any] = {}
    
    def compile_rule(self, rule_text: str, rule_name: Optional[str] = None) -> bool:
        """
        Compile a DSL rule from text
        
        Args:
            rule_text: The DSL rule as a string
            rule_name: Optional name for the rule
            
        Returns:
            True if compilation successful, False otherwise
        """
        try:
            # Tokenize the rule
            tokens = self.lexer.tokenize(rule_text)
            
            # Parse into AST
            ast = self.parser.parse(tokens)
            if not ast:
                return False
            
            # Compile the AST (returns a list of rules)
            compiled_rules = self.interpreter.compile_ast(ast)
            
            # Store compiled rules
            for i, compiled_rule in enumerate(compiled_rules):
                if rule_name and len(compiled_rules) == 1:
                    self.compiled_rules[rule_name] = compiled_rule
                else:
                    rule_key = rule_name or f"rule_{len(self.compiled_rules)}"
                    if len(compiled_rules) > 1:
                        rule_key = f"{rule_key}_{i}"
                    self.compiled_rules[rule_key] = compiled_rule
            
            return True
            
        except Exception as e:
            print(f"Error compiling rule: {e}")
            return False
    
    def compile_file(self, filepath: str) -> bool:
        """
        Compile rules from a file
        
        Args:
            filepath: Path to the DSL file
            
        Returns:
            True if all rules compiled successfully
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the entire file as one unit (handles multiple rules with metadata)
            tokens = self.lexer.tokenize(content)
            ast = self.parser.parse(tokens)
            
            if not ast:
                return False
            
            # Compile all rules from the AST
            compiled_rules = self.interpreter.compile_ast(ast)
            
            # Store compiled rules
            for rule in compiled_rules:
                self.compiled_rules[rule.name] = rule
            
            return True
            
        except Exception as e:
            print(f"Error compiling file {filepath}: {e}")
            return False
    
    def load_rules_from_file(self, filepath: str) -> List[Any]:
        """
        Load and compile rules from a .gamma file
        
        Args:
            filepath: Path to the .gamma file
            
        Returns:
            List of compiled rules
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the entire file
            tokens = self.lexer.tokenize(content)
            ast = self.parser.parse(tokens)
            
            if not ast:
                raise Exception("Failed to parse file")
            
            # Compile all rules from the AST
            compiled_rules = self.interpreter.compile_ast(ast)
            
            # Store compiled rules
            for rule in compiled_rules:
                self.compiled_rules[rule.name] = rule
            
            return compiled_rules
            
        except Exception as e:
            raise Exception(f"Error loading rules from file {filepath}: {e}")
    
    def get_rule_metadata(self, rule_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific rule
        
        Args:
            rule_name: Name of the rule
            
        Returns:
            Metadata dictionary or None if not found
        """
        if rule_name in self.compiled_rules:
            rule = self.compiled_rules[rule_name]
            if hasattr(rule, 'metadata') and rule.metadata:
                return {entry.key: entry.value for entry in rule.metadata.entries}
        return None
    
    def load_rules_from_file_content(self, content: str) -> List[Any]:
        """
        Load and compile rules from rule content string
        
        Args:
            content: Rule content as string
            
        Returns:
            List of compiled rules
        """
        try:
            # Parse the content
            tokens = self.lexer.tokenize(content)
            ast = self.parser.parse(tokens)
            
            if not ast:
                raise Exception("Failed to parse content")
            
            # Compile all rules from the AST
            compiled_rules = self.interpreter.compile_ast(ast)
            
            # Store compiled rules
            for rule in compiled_rules:
                self.compiled_rules[rule.name] = rule
            
            return compiled_rules
            
        except Exception as e:
            raise Exception(f"Error loading rules from content: {e}")
    
    def match(self, text: str, rule_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Match text against compiled rules
        
        Args:
            text: Text to match against
            rule_name: Optional specific rule name to match against
            
        Returns:
            List of match results
        """
        results = []
        
        rules_to_check = {}
        if rule_name and rule_name in self.compiled_rules:
            rules_to_check[rule_name] = self.compiled_rules[rule_name]
        else:
            rules_to_check = self.compiled_rules
        
        for name, rule in rules_to_check.items():
            try:
                matches = self.engine.execute_rule(rule, text)
                if matches:
                    results.extend([{
                        'rule_name': name,
                        'match': match,
                        'position': match.get('position', -1),
                        'length': match.get('length', 0),
                        'captured_groups': match.get('groups', [])
                    } for match in matches])
            except Exception as e:
                print(f"Error executing rule {name}: {e}")
        
        return results
    
    def transform(self, text: str, transformation_rule: str) -> str:
        """
        Apply transformation rule to text
        
        Args:
            text: Input text
            transformation_rule: DSL transformation rule
            
        Returns:
            Transformed text
        """
        try:
            tokens = self.lexer.tokenize(transformation_rule)
            ast = self.parser.parse(tokens)
            if ast:
                return self.engine.execute_transformation(ast, text)
            return text
        except Exception as e:
            print(f"Error in transformation: {e}")
            return text
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive text analysis
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results dictionary
        """
        return self.engine.analyze_text(text)

def main():
    """Main entry point for direct script execution"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <dsl_file> [text_file]")
        print("   or: python main.py --interactive")
        sys.exit(1)
    
    dsl = GammaScanner()
    
    if sys.argv[1] == "--interactive":
        # Interactive mode
        print("Gamma Scanner Interactive Mode")
        print("Type 'help' for commands, 'exit' to quit")
        
        while True:
            try:
                command = input("Gamma> ").strip()
                
                if command == "exit":
                    break
                elif command == "help":
                    print("Commands:")
                    print("  compile <rule>  - Compile a DSL rule")
                    print("  match <text>    - Match text against all rules")
                    print("  load <file>     - Load rules from file")
                    print("  list            - List compiled rules")
                    print("  exit            - Exit interactive mode")
                elif command.startswith("compile "):
                    rule = command[8:]
                    if dsl.compile_rule(rule):
                        print("Rule compiled successfully")
                    else:
                        print("Failed to compile rule")
                elif command.startswith("match "):
                    text = command[6:]
                    results = dsl.match(text)
                    if results:
                        for result in results:
                            print(f"Match found: {result}")
                    else:
                        print("No matches found")
                elif command.startswith("load "):
                    filepath = command[5:]
                    if dsl.compile_file(filepath):
                        print(f"Successfully loaded rules from {filepath}")
                    else:
                        print(f"Failed to load rules from {filepath}")
                elif command == "list":
                    if dsl.compiled_rules:
                        print("Compiled rules:")
                        for rule_name in dsl.compiled_rules:
                            print(f"  - {rule_name}")
                    else:
                        print("No compiled rules")
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except EOFError:
                break
    else:
        # File mode
        dsl_file = sys.argv[1]
        
        if not dsl.compile_file(dsl_file):
            print(f"Failed to compile DSL file: {dsl_file}")
            sys.exit(1)
        
        print(f"Successfully compiled {len(dsl.compiled_rules)} rules from {dsl_file}")
        
        if len(sys.argv) > 2:
            # Match against text file
            text_file = sys.argv[2]
            try:
                with open(text_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                results = dsl.match(text)
                if results:
                    print(f"\nFound {len(results)} matches:")
                    for result in results:
                        print(f"  Rule: {result['rule_name']}")
                        print(f"  Position: {result['position']}")
                        print(f"  Match: {result['match']}")
                        print()
                else:
                    print("No matches found")
                    
            except Exception as e:
                print(f"Error reading text file: {e}")
                sys.exit(1)

if __name__ == "__main__":
    main()
