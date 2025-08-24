"""
StringForge DSL Parser
Converts tokens into Abstract Syntax Tree (AST)
"""

from typing import List, Optional, Union, Any, Dict
from .dsl_lexer import Token, TokenType
from .dsl_ast import *

class ParseError(Exception):
    """Custom exception for parsing errors"""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        super().__init__(message)

class StringForgeParser:
    """Parser for StringForge DSL"""
    
    def __init__(self):
        self.tokens: List[Token] = []
        self.current = 0
    
    def parse(self, tokens: List[Token]) -> Optional[ProgramNode]:
        """
        Parse tokens into an AST
        
        Args:
            tokens: List of tokens from lexer
            
        Returns:
            Root AST node or None if parsing fails
        """
        self.tokens = tokens
        self.current = 0
        
        try:
            return self._parse_program()
        except ParseError as e:
            print(f"Parse error: {e.message}")
            if e.token:
                print(f"At line {e.token.line}, column {e.token.column}")
            return None
    
    def _current_token(self) -> Token:
        """Get current token"""
        if self.current >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[self.current]
    
    def _peek_token(self, offset: int = 1) -> Token:
        """Peek at token with offset"""
        index = self.current + offset
        if index >= len(self.tokens):
            return self.tokens[-1]  # EOF token
        return self.tokens[index]
    
    def _advance(self) -> Token:
        """Advance to next token and return current"""
        token = self._current_token()
        if self.current < len(self.tokens) - 1:
            self.current += 1
        return token
    
    def _match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        return self._current_token().type in token_types
    
    def _consume(self, token_type: TokenType, message: str = "") -> Token:
        """Consume token of expected type or raise error"""
        if not self._match(token_type):
            if not message:
                message = f"Expected {token_type.name}, got {self._current_token().type.name}"
            raise ParseError(message, self._current_token())
        return self._advance()
    
    def _parse_program(self) -> ProgramNode:
        """Parse the entire program"""
        statements = []
        metadata = None
        
        while not self._match(TokenType.EOF):
            # Skip newlines and whitespace
            if self._match(TokenType.NEWLINE, TokenType.WHITESPACE):
                self._advance()
                continue
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return ProgramNode(statements, metadata)
    
    def _parse_statement(self) -> Optional[StatementNode]:
        """Parse a single statement"""
        if self._match(TokenType.RULE):
            return self._parse_rule()
        elif self._match(TokenType.IDENTIFIER):
            result = self._parse_assignment_or_expression()
            if isinstance(result, ExpressionNode):
                return ExpressionStatementNode(result)
            return result
        elif self._match(TokenType.IF):
            return self._parse_if_statement()
        else:
            expr = self._parse_expression()
            return ExpressionStatementNode(expr)
    
    def _parse_rule(self) -> RuleNode:
        """Parse a scanner definition with unique DSL syntax"""
        self._consume(TokenType.RULE)  # 'HUNT', 'SCAN', 'FIND', or 'SEEK'
        
        # Scanner name
        name_token = self._consume(TokenType.IDENTIFIER, "Expected scanner name")
        rule_name = name_token.value
        
        self._consume(TokenType.COLON, "Expected ':' after scanner name")
        
        # Rule body - metadata, strings, conditions and actions
        conditions = []
        actions = []
        metadata = None
        strings = None
        
        # Parse rule sections until we hit EOF or another top-level keyword
        while not self._match(TokenType.EOF) and not self._match(TokenType.RULE):
            if self._match(TokenType.NEWLINE, TokenType.WHITESPACE):
                self._advance()
                continue
            
            # Check for metadata section (multiple keywords supported)
            if self._match(TokenType.META):
                metadata = self._parse_metadata()
                continue
            
            # Handle "LOOK FOR" syntax FIRST (before general STRINGS check)
            if (self._current_token() and self._current_token().type == TokenType.STRINGS and 
                self._current_token().value == 'LOOK' and 
                self.current + 1 < len(self.tokens) and 
                self.tokens[self.current + 1].value == 'FOR'):
                self._advance()  # consume 'LOOK'  
                self._advance()  # consume 'FOR'
                strings = self._parse_strings_unique_syntax()
                continue
                
            # Check for other patterns/strings section keywords
            if self._match(TokenType.STRINGS):
                strings = self._parse_strings() 
                continue
            
            # Check for condition section
            if self._match(TokenType.CONDITION):
                self._advance()
                self._consume(TokenType.COLON, "Expected ':' after 'condition'")
                # Parse the entire condition as one expression
                condition_expr = self._parse_expression()
                if condition_expr:
                    conditions.append(condition_expr)
                continue
            
            # Parse as expression (includes function calls like contains(), regex_match(), etc.)
            try:
                expr = self._parse_expression()
                if expr:
                    conditions.append(expr)
            except ParseError:
                # Skip this token if we can't parse it
                self._advance()
        
        # No closing brace needed for colon-based syntax
        
        return RuleNode(rule_name, conditions, actions, metadata, strings)
    
    def _parse_condition(self) -> ConditionNode:
        """Parse a condition"""
        if self._match(TokenType.MATCH):
            return self._parse_match_condition()
        elif self._match(TokenType.CONTAINS):
            return self._parse_contains_condition()
        elif self._match(TokenType.STARTS_WITH):
            return self._parse_starts_with_condition()
        elif self._match(TokenType.ENDS_WITH):
            return self._parse_ends_with_condition()
        elif self._match(TokenType.REGEX_MATCH):
            return self._parse_regex_condition()
        else:
            # Parse as general expression condition
            expr = self._parse_expression()
            return ConditionNode("expression", expr)
    
    def _parse_match_condition(self) -> ConditionNode:
        """Parse a match condition"""
        self._consume(TokenType.MATCH)
        
        self._consume(TokenType.LPAREN)
        pattern = self._parse_expression()
        
        # Optional target
        target = None
        if self._match(TokenType.COMMA):
            self._advance()
            target = self._parse_expression()
        
        self._consume(TokenType.RPAREN)
        
        return ConditionNode("match", pattern, target)
    
    def _parse_contains_condition(self) -> ConditionNode:
        """Parse a contains condition"""
        self._consume(TokenType.CONTAINS)
        
        self._consume(TokenType.LPAREN)
        substring = self._parse_expression()
        
        # Optional target
        target = None
        if self._match(TokenType.COMMA):
            self._advance()
            target = self._parse_expression()
        
        self._consume(TokenType.RPAREN)
        
        return ConditionNode("contains", substring, target)
    
    def _parse_starts_with_condition(self) -> ConditionNode:
        """Parse a starts_with condition"""
        self._consume(TokenType.STARTS_WITH)
        
        self._consume(TokenType.LPAREN)
        prefix = self._parse_expression()
        
        # Optional target
        target = None
        if self._match(TokenType.COMMA):
            self._advance()
            target = self._parse_expression()
        
        self._consume(TokenType.RPAREN)
        
        return ConditionNode("starts_with", prefix, target)
    
    def _parse_ends_with_condition(self) -> ConditionNode:
        """Parse an ends_with condition"""
        self._consume(TokenType.ENDS_WITH)
        
        self._consume(TokenType.LPAREN)
        suffix = self._parse_expression()
        
        # Optional target
        target = None
        if self._match(TokenType.COMMA):
            self._advance()
            target = self._parse_expression()
        
        self._consume(TokenType.RPAREN)
        
        return ConditionNode("ends_with", suffix, target)
    
    def _parse_regex_condition(self) -> ConditionNode:
        """Parse a regex_match condition"""
        self._consume(TokenType.REGEX_MATCH)
        
        self._consume(TokenType.LPAREN)
        pattern = self._parse_expression()
        
        # Optional target and flags
        target = None
        flags = None
        
        if self._match(TokenType.COMMA):
            self._advance()
            target = self._parse_expression()
            
            if self._match(TokenType.COMMA):
                self._advance()
                flags = self._parse_expression()
        
        self._consume(TokenType.RPAREN)
        
        return ConditionNode("regex_match", pattern, target, flags)
    
    def _parse_action(self) -> ActionNode:
        """Parse an action"""
        if self._match(TokenType.REPLACE):
            return self._parse_replace_action()
        elif self._match(TokenType.EXTRACT):
            return self._parse_extract_action()
        elif self._match(TokenType.TRANSFORM):
            return self._parse_transform_action()
        else:
            raise ParseError("Expected action keyword", self._current_token())
    
    def _parse_replace_action(self) -> ActionNode:
        """Parse a replace action"""
        self._consume(TokenType.REPLACE)
        
        self._consume(TokenType.LPAREN)
        pattern = self._parse_expression()
        self._consume(TokenType.COMMA)
        replacement = self._parse_expression()
        
        # Optional target
        target = None
        if self._match(TokenType.COMMA):
            self._advance()
            target = self._parse_expression()
        
        self._consume(TokenType.RPAREN)
        
        return ActionNode("replace", pattern, replacement, target)
    
    def _parse_extract_action(self) -> ActionNode:
        """Parse an extract action"""
        self._consume(TokenType.EXTRACT)
        
        self._consume(TokenType.LPAREN)
        pattern = self._parse_expression()
        
        # Optional target
        target = None
        if self._match(TokenType.COMMA):
            self._advance()
            target = self._parse_expression()
        
        self._consume(TokenType.RPAREN)
        
        return ActionNode("extract", pattern, target)
    
    def _parse_transform_action(self) -> ActionNode:
        """Parse a transform action"""
        self._consume(TokenType.TRANSFORM)
        
        self._consume(TokenType.LPAREN)
        transformation = self._parse_expression()
        
        # Optional target
        target = None
        if self._match(TokenType.COMMA):
            self._advance()
            target = self._parse_expression()
        
        self._consume(TokenType.RPAREN)
        
        return ActionNode("transform", transformation, target)
    
    def _parse_assignment_or_expression(self) -> Union[AssignmentNode, ExpressionNode]:
        """Parse assignment or expression"""
        # Look ahead to see if this is an assignment
        if self._peek_token().type == TokenType.ASSIGN:
            identifier = self._advance().value
            self._consume(TokenType.ASSIGN)
            value = self._parse_expression()
            return AssignmentNode(identifier, value)
        else:
            return self._parse_expression()
    
    def _parse_if_statement(self) -> IfNode:
        """Parse if statement"""
        self._consume(TokenType.IF)
        
        self._consume(TokenType.LPAREN)
        condition = self._parse_expression()
        self._consume(TokenType.RPAREN)
        
        self._consume(TokenType.LBRACE)
        then_statements = []
        while not self._match(TokenType.RBRACE):
            if self._match(TokenType.NEWLINE, TokenType.WHITESPACE):
                self._advance()
                continue
            stmt = self._parse_statement()
            if stmt:
                then_statements.append(stmt)
        self._consume(TokenType.RBRACE)
        
        # Optional else clause
        else_statements = []
        if self._match(TokenType.ELSE):
            self._advance()
            self._consume(TokenType.LBRACE)
            while not self._match(TokenType.RBRACE):
                if self._match(TokenType.NEWLINE, TokenType.WHITESPACE):
                    self._advance()
                    continue
                stmt = self._parse_statement()
                if stmt:
                    else_statements.append(stmt)
            self._consume(TokenType.RBRACE)
        
        return IfNode(condition, then_statements, else_statements)
    
    def _parse_expression(self) -> ExpressionNode:
        """Parse expression with operator precedence"""
        return self._parse_or_expression()
    
    def _parse_or_expression(self) -> ExpressionNode:
        """Parse OR expression"""
        left = self._parse_and_expression()
        
        while self._match(TokenType.OR):
            operator = self._advance().value
            right = self._parse_and_expression()
            left = BinaryOpNode(left, operator, right)
        
        return left
    
    def _parse_and_expression(self) -> ExpressionNode:
        """Parse AND expression"""
        left = self._parse_equality_expression()
        
        while self._match(TokenType.AND):
            operator = self._advance().value
            right = self._parse_equality_expression()
            left = BinaryOpNode(left, operator, right)
        
        return left
    
    def _parse_equality_expression(self) -> ExpressionNode:
        """Parse equality expression"""
        left = self._parse_relational_expression()
        
        while self._match(TokenType.EQUALS, TokenType.NOT_EQUALS):
            operator = self._advance().value
            right = self._parse_relational_expression()
            left = BinaryOpNode(left, operator, right)
        
        return left
    
    def _parse_relational_expression(self) -> ExpressionNode:
        """Parse relational expression"""
        left = self._parse_additive_expression()
        
        while self._match(TokenType.LESS_THAN, TokenType.GREATER_THAN, 
                          TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL):
            operator = self._advance().value
            right = self._parse_additive_expression()
            left = BinaryOpNode(left, operator, right)
        
        return left
    
    def _parse_additive_expression(self) -> ExpressionNode:
        """Parse additive expression"""
        left = self._parse_multiplicative_expression()
        
        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._advance().value
            right = self._parse_multiplicative_expression()
            left = BinaryOpNode(left, operator, right)
        
        return left
    
    def _parse_multiplicative_expression(self) -> ExpressionNode:
        """Parse multiplicative expression"""
        left = self._parse_unary_expression()
        
        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            operator = self._advance().value
            right = self._parse_unary_expression()
            left = BinaryOpNode(left, operator, right)
        
        return left
    
    def _parse_unary_expression(self) -> ExpressionNode:
        """Parse unary expression"""
        if self._match(TokenType.NOT, TokenType.MINUS):
            operator = self._advance().value
            operand = self._parse_unary_expression()
            return UnaryOpNode(operator, operand)
        
        return self._parse_postfix_expression()
    
    def _parse_postfix_expression(self) -> ExpressionNode:
        """Parse postfix expression (function calls, member access)"""
        expr = self._parse_primary_expression()
        
        while True:
            if self._match(TokenType.LPAREN):
                # Function call
                self._advance()
                args = []
                
                if not self._match(TokenType.RPAREN):
                    args.append(self._parse_expression())
                    while self._match(TokenType.COMMA):
                        self._advance()
                        args.append(self._parse_expression())
                
                self._consume(TokenType.RPAREN)
                expr = FunctionCallNode(expr, args)
                
            elif self._match(TokenType.DOT):
                # Member access
                self._advance()
                member = self._consume(TokenType.IDENTIFIER).value
                expr = MemberAccessNode(expr, member)
                
            elif self._match(TokenType.LBRACKET):
                # Array/string indexing
                self._advance()
                index = self._parse_expression()
                self._consume(TokenType.RBRACKET)
                expr = IndexAccessNode(expr, index)
                
            else:
                break
        
        return expr
    
    def _parse_primary_expression(self) -> ExpressionNode:
        """Parse primary expression"""
        from dsl_ast import (StringCountNode, StringOffsetNode, StringLengthNode, 
                           StringIdentifierNode, FilesizeNode, EntrypointNode,
                           ForExpressionNode, HexStringNode, StringSetNode)
        
        if self._match(TokenType.STRING):
            value = self._advance().value
            return LiteralNode(value, "string")
        
        elif self._match(TokenType.REGEX):
            value = self._advance().value
            return LiteralNode(value, "regex")
        
        elif self._match(TokenType.HEX_STRING):
            value = self._advance().value
            return HexStringNode(value)
        
        elif self._match(TokenType.NUMBER):
            value = self._advance().value
            # Convert to appropriate numeric type
            if '.' in value:
                return LiteralNode(float(value), "float")
            else:
                return LiteralNode(int(value), "int")
        
        elif self._match(TokenType.BOOLEAN):
            value = self._advance().value
            return LiteralNode(value == "true", "boolean")
        
        # YARA-style string identifiers
        elif self._match(TokenType.STRING_IDENTIFIER):
            value = self._advance().value
            return StringIdentifierNode(value)
        
        # String operations: #$string, @$string, !$string
        elif self._match(TokenType.STRING_COUNT):
            self._advance()
            if self._match(TokenType.STRING_IDENTIFIER):
                string_id = self._advance().value
                return StringCountNode(string_id)
            else:
                raise ParseError("Expected string identifier after '#'", self._current_token())
        
        elif self._match(TokenType.STRING_OFFSET):
            self._advance()
            if self._match(TokenType.STRING_IDENTIFIER):
                string_id = self._advance().value
                index = None
                if self._match(TokenType.LBRACKET):
                    self._advance()
                    index = self._parse_expression()
                    self._consume(TokenType.RBRACKET)
                return StringOffsetNode(string_id, index)
            else:
                raise ParseError("Expected string identifier after '@'", self._current_token())
        
        elif self._match(TokenType.STRING_LENGTH):
            self._advance()
            if self._match(TokenType.STRING_IDENTIFIER):
                string_id = self._advance().value
                index = None
                if self._match(TokenType.LBRACKET):
                    self._advance()
                    index = self._parse_expression()
                    self._consume(TokenType.RBRACKET)
                return StringLengthNode(string_id, index)
            else:
                raise ParseError("Expected string identifier after '!'", self._current_token())
        
        # YARA keywords
        elif self._match(TokenType.FILESIZE):
            self._advance()
            return FilesizeNode()
        
        elif self._match(TokenType.ENTRYPOINT):
            self._advance()
            return EntrypointNode()
        
        elif self._match(TokenType.THEM):
            self._advance()
            return StringSetNode(['them'])
        
        # For expressions
        elif self._match(TokenType.FOR):
            return self._parse_for_expression()
        
        elif self._match(TokenType.IDENTIFIER):
            name = self._advance().value
            return IdentifierNode(name)
        
        elif self._match(TokenType.CONTAINS, TokenType.REGEX_MATCH, TokenType.STARTS_WITH, TokenType.ENDS_WITH, TokenType.MATCH):
            # Parse built-in function calls
            func_name = self._advance().value
            return IdentifierNode(func_name)
        
        # Integer size functions
        elif self._match(TokenType.UINT8, TokenType.UINT16, TokenType.UINT32, 
                         TokenType.INT8, TokenType.INT16, TokenType.INT32):
            func_name = self._advance().value
            return IdentifierNode(func_name)
        
        elif self._match(TokenType.LPAREN):
            self._advance()
            # Check for string set: ($s1, $s2, $s3)
            if self._match(TokenType.STRING_IDENTIFIER):
                string_ids = []
                string_ids.append(self._advance().value)
                while self._match(TokenType.COMMA):
                    self._advance()
                    if self._match(TokenType.STRING_IDENTIFIER):
                        string_ids.append(self._advance().value)
                self._consume(TokenType.RPAREN)
                return StringSetNode(string_ids)
            else:
                # Regular parenthesized expression
                expr = self._parse_expression()
                self._consume(TokenType.RPAREN)
                return expr
        
        elif self._match(TokenType.LBRACKET):
            # Array literal
            self._advance()
            elements = []
            
            if not self._match(TokenType.RBRACKET):
                elements.append(self._parse_expression())
                while self._match(TokenType.COMMA):
                    self._advance()
                    elements.append(self._parse_expression())
            
            self._consume(TokenType.RBRACKET)
            return ArrayLiteralNode(elements)
        
        else:
            raise ParseError(f"Unexpected token in expression: {self._current_token().type.name}", 
                           self._current_token())
    
    def _parse_metadata(self) -> 'MetadataNode':
        """Parse a metadata section"""
        from dsl_ast import MetadataNode, MetadataEntryNode
        
        self._consume(TokenType.META)
        self._consume(TokenType.COLON, "Expected ':' after 'meta'")
        
        entries = []
        
        # Parse metadata entries until we hit something that's not a metadata entry
        while not self._match(TokenType.RBRACE, TokenType.EOF):
            if self._match(TokenType.NEWLINE, TokenType.WHITESPACE):
                self._advance()
                continue
            
            # Check if we're hitting a different section - check if identifier is followed by something other than =
            if self._match(TokenType.IDENTIFIER):
                # Peek ahead to see if this is key = value or something else
                if self._peek_token().type != TokenType.ASSIGN:
                    # This is likely the start of a condition/action, break out
                    break
                    
                key_token = self._advance()
                self._consume(TokenType.ASSIGN, "Expected '=' after metadata key")
                
                if self._match(TokenType.STRING):
                    value_token = self._advance()
                    # Remove quotes from string literal
                    value = value_token.value[1:-1] if value_token.value.startswith('"') or value_token.value.startswith("'") else value_token.value
                    entries.append(MetadataEntryNode(key_token.value, value))
                else:
                    raise ParseError("Expected string value for metadata entry", self._current_token())
            elif self._match(TokenType.MATCH, TokenType.REPLACE, TokenType.EXTRACT, TokenType.TRANSFORM, TokenType.CONTAINS, TokenType.STARTS_WITH, TokenType.ENDS_WITH, TokenType.REGEX_MATCH):
                # Hit a condition/action keyword, break out
                break
            else:
                # Unknown token, skip or break
                break
        
        return MetadataNode(entries)
    
    def _parse_strings(self) -> 'StringsNode':
        """Parse a patterns/strings section with intuitive syntax"""
        from dsl_ast import StringsNode, StringDefinitionNode
        
        self._consume(TokenType.STRINGS)
        self._consume(TokenType.COLON, "Expected ':' after patterns section")
        
        string_definitions = []
        
        while not self._match(TokenType.RBRACE, TokenType.EOF):
            if self._match(TokenType.NEWLINE, TokenType.WHITESPACE):
                self._advance()
                continue
            
            # Check if we're hitting a different section
            if self._match(TokenType.CONDITION, TokenType.META, TokenType.MATCH, TokenType.REPLACE, TokenType.EXTRACT, TokenType.TRANSFORM):
                break
            
            # Parse intuitive pattern definition: pattern_name = type "value" modifiers
            if self._match(TokenType.IDENTIFIER):
                pattern_name = self._advance().value
                self._consume(TokenType.ASSIGN, "Expected '=' after pattern name")
                
                # Parse pattern type and value
                string_type = "text"  # default
                string_value = ""
                
                # Check for explicit type declaration
                if self._match(TokenType.IDENTIFIER):
                    type_token = self._advance()
                    if type_token.value in ['text', 'regex', 'hex', 'binary']:
                        string_type = type_token.value
                
                # Parse the actual pattern value
                if self._match(TokenType.STRING):
                    string_value = self._advance().value
                    # Remove quotes
                    if string_value.startswith('"') and string_value.endswith('"'):
                        string_value = string_value[1:-1]
                    elif string_value.startswith("'") and string_value.endswith("'"):
                        string_value = string_value[1:-1]
                    
                elif self._match(TokenType.REGEX):
                    string_value = self._advance().value
                    string_type = "regex"
                    
                elif self._match(TokenType.HEX_STRING):
                    string_value = self._advance().value
                    string_type = "hex"
                
                # Parse intuitive modifiers
                modifiers = []
                while self._match(TokenType.NOCASE, TokenType.WIDE, TokenType.ASCII, TokenType.FULLWORD):
                    modifier_token = self._advance()
                    # Map intuitive modifier names to internal names
                    modifier_map = {
                        'ignore_case': 'nocase',
                        'case_insensitive': 'nocase', 
                        'ascii_only': 'ascii',
                        'wide_chars': 'wide',
                        'whole_word': 'fullword',
                        'exact_match': 'fullword'
                    }
                    modifiers.append(modifier_map.get(modifier_token.value, modifier_token.value))
                
                # Use $ prefix for internal compatibility but allow natural names
                internal_id = f"${pattern_name}" if not pattern_name.startswith('$') else pattern_name
                string_definitions.append(StringDefinitionNode(internal_id, string_value, string_type, modifiers))
            else:
                break
        
        return StringsNode(string_definitions)
        
    def _parse_strings_unique_syntax(self) -> 'StringsNode':
        """Parse unique DSL pattern syntax: pattern_name ~ type "value" modifiers"""
        from dsl_ast import StringsNode, StringDefinitionNode
        
        self._consume(TokenType.COLON, "Expected ':' after pattern section")
        
        string_definitions = []
        
        while not self._match(TokenType.RBRACE, TokenType.EOF):
            if self._match(TokenType.NEWLINE, TokenType.WHITESPACE):
                self._advance()
                continue
                
            # Check if hitting different section
            if self._match(TokenType.CONDITION, TokenType.META, TokenType.MATCH, TokenType.REPLACE, TokenType.EXTRACT, TokenType.TRANSFORM):
                break
                
            # Parse unique syntax: pattern_name ~ type "value" modifiers
            if self._match(TokenType.IDENTIFIER):
                pattern_name = self._advance().value
                
                # Expect ~ operator for pattern binding
                if self._match(TokenType.IDENTIFIER) and self._current_token().value == '~':
                    self._advance()  # consume '~'
                else:
                    # Try regular assignment for compatibility
                    if self._match(TokenType.ASSIGN):
                        self._advance()
                
                # Parse pattern type
                string_type = "text"  # default
                if self._match(TokenType.IDENTIFIER):
                    type_token = self._advance()
                    if type_token.value in ['text', 'hex', 'pattern']:
                        string_type = type_token.value
                        if string_type == 'pattern':
                            string_type = 'regex'  # Convert to internal type
                
                # Parse pattern value
                string_value = ""
                if self._match(TokenType.STRING):
                    string_value = self._advance().value
                    # Remove quotes
                    if string_value.startswith('"') and string_value.endswith('"'):
                        string_value = string_value[1:-1]
                    elif string_value.startswith("'") and string_value.endswith("'"):
                        string_value = string_value[1:-1]
                elif self._match(TokenType.REGEX):
                    string_value = self._advance().value
                    string_type = "regex"
                elif self._match(TokenType.HEX_STRING):
                    string_value = self._advance().value
                    string_type = "hex"
                
                # Parse unique modifiers
                modifiers = []
                while self._match(TokenType.NOCASE, TokenType.WIDE, TokenType.ASCII, TokenType.FULLWORD):
                    modifier_token = self._advance()
                    # Map unique modifier names to internal names
                    modifier_map = {
                        'IGNORE': 'nocase',
                        'EXACT': 'fullword',
                        'WIDE': 'wide', 
                        'NARROW': 'ascii'
                    }
                    modifiers.append(modifier_map.get(modifier_token.value, modifier_token.value.lower()))
                
                # Use $ prefix for internal compatibility
                internal_id = f"${pattern_name}" if not pattern_name.startswith('$') else pattern_name
                string_definitions.append(StringDefinitionNode(internal_id, string_value, string_type, modifiers))
            else:
                break
                
        return StringsNode(string_definitions)
    
    def _parse_for_expression(self) -> 'ForExpressionNode':
        """Parse for expressions: for any/all of them"""
        from dsl_ast import ForExpressionNode
        
        self._consume(TokenType.FOR)
        
        # Parse quantifier (any, all, or number)
        quantifier = ""
        if self._match(TokenType.ANY):
            quantifier = self._advance().value
        elif self._match(TokenType.ALL):
            quantifier = self._advance().value
        elif self._match(TokenType.NUMBER):
            quantifier = self._advance().value
        else:
            raise ParseError("Expected 'any', 'all', or number after 'for'", self._current_token())
        
        self._consume(TokenType.OF, "Expected 'of' in for expression")
        
        # Parse string set (them, ($s1, $s2), etc.)
        string_set = self._parse_expression()
        
        # Optional condition with ':'
        condition = None
        if self._match(TokenType.COLON):
            self._advance()
            # Parse condition after colon
            if self._match(TokenType.LPAREN):
                self._advance()
                condition = self._parse_expression()
                self._consume(TokenType.RPAREN, "Expected ')' after for condition")
        
        return ForExpressionNode(quantifier, "of", string_set, condition)
