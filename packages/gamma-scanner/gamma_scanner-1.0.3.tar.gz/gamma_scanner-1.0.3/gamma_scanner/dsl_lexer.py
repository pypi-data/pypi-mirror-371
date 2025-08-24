"""
StringForge DSL Lexer
Tokenizes DSL syntax for parsing
"""

import re
from typing import List, NamedTuple, Iterator, Optional
from enum import Enum, auto

class TokenType(Enum):
    # Literals
    STRING = auto()
    REGEX = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    HEX_STRING = auto()
    STRING_IDENTIFIER = auto()  # $string1, $pattern, etc.
    
    # Identifiers and Keywords
    IDENTIFIER = auto()
    RULE = auto()
    META = auto()
    STRINGS = auto()
    CONDITION = auto()
    MATCH = auto()
    REPLACE = auto()
    EXTRACT = auto()
    TRANSFORM = auto()
    IF = auto()
    ELSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    IN = auto()
    CONTAINS = auto()
    STARTS_WITH = auto()
    ENDS_WITH = auto()
    REGEX_MATCH = auto()
    LENGTH = auto()
    COUNT = auto()
    SPLIT = auto()
    JOIN = auto()
    UPPER = auto()
    LOWER = auto()
    STRIP = auto()
    
    # YARA-like keywords
    FOR = auto()
    ANY = auto()
    ALL = auto()
    OF = auto()
    THEM = auto()
    AT = auto()
    FILESIZE = auto()
    ENTRYPOINT = auto()
    UINT8 = auto()
    UINT16 = auto()
    UINT32 = auto()
    INT8 = auto()
    INT16 = auto()
    INT32 = auto()
    
    # String modifiers
    NOCASE = auto()
    ASCII = auto()
    WIDE = auto()
    FULLWORD = auto()
    PRIVATE = auto()
    GLOBAL = auto()
    
    # Operators
    ASSIGN = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()
    LESS_EQUAL = auto()
    GREATER_EQUAL = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    
    # Bitwise operators
    BITWISE_AND = auto()
    BITWISE_OR = auto()
    BITWISE_XOR = auto()
    BITWISE_NOT = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()
    
    # String operators
    STRING_COUNT = auto()      # #
    STRING_OFFSET = auto()     # @
    STRING_LENGTH = auto()     # !
    
    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    SEMICOLON = auto()
    COLON = auto()
    DOT = auto()
    ARROW = auto()
    DOLLAR = auto()            # $
    
    # Special
    NEWLINE = auto()
    EOF = auto()
    WHITESPACE = auto()
    COMMENT = auto()

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int

class StringForgeLexer:
    """Lexer for StringForge DSL"""
    
    def __init__(self):
        self.keywords = {
            # Completely unique DSL keywords (unlike any programming language!)
            
            # Scanner definitions using unique syntax
            'HUNT': TokenType.RULE,          # HUNT MalwareThreat
            'SCAN': TokenType.RULE,          # SCAN ForBackdoors  
            'FIND': TokenType.RULE,          # FIND SuspiciousCode
            'SEEK': TokenType.RULE,          # SEEK HiddenPatterns
            
            # Pattern definitions with unique approach
            'LOOK': TokenType.STRINGS,       # LOOK FOR these signatures
            'SEARCH': TokenType.STRINGS,     # SEARCH these patterns
            'SIGNATURES': TokenType.STRINGS, # SIGNATURES are
            
            # Conditions with flow language
            'WHEN': TokenType.CONDITION,     # WHEN any pattern matches
            'TRIGGER': TokenType.CONDITION,  # TRIGGER if conditions met
            'ACTIVATE': TokenType.CONDITION, # ACTIVATE when found
            
            # Metadata with descriptive syntax  
            'ABOUT': TokenType.META,         # ABOUT this scanner
            'INFO': TokenType.META,          # INFO regarding detection
            
            # Unique logical flow
            'ALSO': TokenType.AND,           # pattern1 ALSO pattern2
            'EITHER': TokenType.OR,          # EITHER this ELSE that
            'ELSE': TokenType.OR,            # EITHER pattern1 ELSE pattern2
            'EXCLUDE': TokenType.NOT,        # EXCLUDE pattern1
            'AVOID': TokenType.NOT,          # AVOID false positives
            'UNLESS': TokenType.NOT,         # UNLESS condition
            
            # Pattern matching with unique operators
            'HAS': TokenType.CONTAINS,       # file HAS malware_signature
            'HOLDS': TokenType.CONTAINS,     # content HOLDS backdoor_text
            'BEGINS': TokenType.STARTS_WITH, # filename BEGINS evil_prefix
            'ENDS': TokenType.ENDS_WITH,     # extension ENDS .exe
            'MATCHES': TokenType.REGEX_MATCH,# content MATCHES /regex/
            'FITS': TokenType.REGEX_MATCH,   # data FITS pattern
            
            # Quantifiers with natural flow
            'SEVERAL': TokenType.FOR,        # SEVERAL of these patterns
            'MANY': TokenType.FOR,           # MANY instances found
            'FEW': TokenType.FOR,            # FEW matches required
            'SOME': TokenType.ANY,           # SOME patterns match
            'ALL': TokenType.ALL,            # ALL signatures present
            'NONE': TokenType.NOT,           # NONE of these patterns
            'EVERY': TokenType.ALL,          # EVERY pattern matches
            
            # File properties with unique names
            'SIZE': TokenType.FILESIZE,      # SIZE greater than 1MB
            'BYTES': TokenType.FILESIZE,     # BYTES between 100 and 1000
            'ENTRY': TokenType.ENTRYPOINT,   # ENTRY point analysis
            'START': TokenType.ENTRYPOINT,   # START offset check
            
            # Data types with unique syntax
            'BYTE': TokenType.UINT8,         # BYTE value
            'WORD': TokenType.UINT16,        # WORD data
            'DWORD': TokenType.UINT32,       # DWORD content
            
            # Pattern modifiers with flow language
            'IGNORE': TokenType.NOCASE,      # IGNORE case differences
            'EXACT': TokenType.FULLWORD,     # EXACT word boundaries
            'WIDE': TokenType.WIDE,          # WIDE character encoding
            'NARROW': TokenType.ASCII,       # NARROW ascii only
            
            # Boolean values with natural language
            'YES': TokenType.BOOLEAN,        # condition is YES
            'NO': TokenType.BOOLEAN,         # result is NO
            'MAYBE': TokenType.BOOLEAN,      # heuristic MAYBE
            
            # Actions with unique syntax
            'ALERT': TokenType.MATCH,        # ALERT when found
            'REPORT': TokenType.MATCH,       # REPORT detection
            'FLAG': TokenType.MATCH,         # FLAG suspicious content
            'MARK': TokenType.MATCH,         # MARK as threat
            'CHANGE': TokenType.REPLACE,     # CHANGE malicious code
            'REMOVE': TokenType.REPLACE,     # REMOVE threat
            'EXTRACT': TokenType.EXTRACT,    # EXTRACT indicators
            'CAPTURE': TokenType.EXTRACT,    # CAPTURE evidence
        }
        
        self.operators = {
            '~': TokenType.ASSIGN,           # Use ~ for pattern binding 
            '=': TokenType.ASSIGN,
            '==': TokenType.EQUALS,
            '!=': TokenType.NOT_EQUALS,
            '<': TokenType.LESS_THAN,
            '>': TokenType.GREATER_THAN,
            '<=': TokenType.LESS_EQUAL,
            '>=': TokenType.GREATER_EQUAL,
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '->': TokenType.ARROW,
            
            # Bitwise operators
            '&': TokenType.BITWISE_AND,
            '|': TokenType.BITWISE_OR,
            '^': TokenType.BITWISE_XOR,
            '~': TokenType.BITWISE_NOT,
            '<<': TokenType.LEFT_SHIFT,
            '>>': TokenType.RIGHT_SHIFT,
            
            # String operators
            '#': TokenType.STRING_COUNT,
            '@': TokenType.STRING_OFFSET,
            '!': TokenType.STRING_LENGTH,
        }
        
        self.delimiters = {
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            '.': TokenType.DOT,
            '$': TokenType.DOLLAR,
        }
    
    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize input text into a list of tokens
        
        Args:
            text: Input DSL text
            
        Returns:
            List of tokens
        """
        tokens = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            tokens.extend(self._tokenize_line(line, line_num))
        
        tokens.append(Token(TokenType.EOF, '', len(lines), 0))
        return tokens
    
    def _tokenize_line(self, line: str, line_num: int) -> List[Token]:
        """Tokenize a single line"""
        tokens = []
        i = 0
        
        while i < len(line):
            # Skip whitespace
            if line[i].isspace():
                i += 1
                continue
            
            # Comments
            if line[i:i+2] == '//':
                # Rest of line is comment
                break
            elif line[i:i+2] == '/*':
                # Block comment - find closing */
                end_pos = line.find('*/', i + 2)
                if end_pos != -1:
                    i = end_pos + 2
                    continue
                else:
                    # Block comment continues to next line
                    break
            
            # String identifiers ($string1, $pattern, etc.) - Handle before # operator
            if line[i] == '$':
                if i + 1 < len(line) and (line[i+1].isalpha() or line[i+1] == '_'):
                    start = i + 1
                    end = start
                    while end < len(line) and (line[end].isalnum() or line[end] == '_'):
                        end += 1
                    tokens.append(Token(TokenType.STRING_IDENTIFIER, '$' + line[start:end], line_num, i))
                    i = end
                    continue
                else:
                    tokens.append(Token(TokenType.DOLLAR, '$', line_num, i))
                    i += 1
                    continue
            
            # Hex strings { 01 02 ?? 04 } - Handle before { delimiter
            if line[i] == '{':
                hex_start = i
                hex_end = line.find('}', i + 1)
                if hex_end != -1:
                    hex_content = line[i+1:hex_end].strip()
                    # Check if it looks like hex string content
                    if re.match(r'^[0-9a-fA-F\s\?]+$', hex_content):
                        tokens.append(Token(TokenType.HEX_STRING, line[i:hex_end+1], line_num, i))
                        i = hex_end + 1
                        continue
                # Fall through to regular delimiter handling
            
            # Handle # as comment vs string count operator
            if line[i] == '#':
                # Check if it's followed by $ for string count
                if i + 1 < len(line) and line[i + 1] == '$':
                    tokens.append(Token(TokenType.STRING_COUNT, '#', line_num, i))
                    i += 1
                    continue
                else:
                    # Rest of line is comment
                    break
            
            # String literals
            if line[i] in ['"', "'"]:
                quote_char = line[i]
                i += 1
                start = i
                while i < len(line) and line[i] != quote_char:
                    if line[i] == '\\' and i + 1 < len(line):
                        i += 2  # Skip escaped character
                    else:
                        i += 1
                
                if i >= len(line):
                    raise SyntaxError(f"Unterminated string literal at line {line_num}")
                
                string_value = line[start:i]
                tokens.append(Token(TokenType.STRING, string_value, line_num, start))
                i += 1  # Skip closing quote
                continue
            
            # Regex literals
            if line[i] == '/' and i + 1 < len(line) and line[i + 1] != '/':
                i += 1
                start = i
                while i < len(line) and line[i] != '/':
                    if line[i] == '\\' and i + 1 < len(line):
                        i += 2  # Skip escaped character
                    else:
                        i += 1
                
                if i >= len(line):
                    raise SyntaxError(f"Unterminated regex literal at line {line_num}")
                
                regex_value = line[start:i]
                tokens.append(Token(TokenType.REGEX, regex_value, line_num, start))
                i += 1  # Skip closing /
                continue
            
            # Numbers
            if line[i].isdigit():
                start = i
                while i < len(line) and (line[i].isdigit() or line[i] == '.'):
                    i += 1
                
                number_value = line[start:i]
                tokens.append(Token(TokenType.NUMBER, number_value, line_num, start))
                continue
            
            # Multi-character operators
            if i + 1 < len(line):
                two_char = line[i:i+2]
                if two_char in self.operators:
                    tokens.append(Token(self.operators[two_char], two_char, line_num, i))
                    i += 2
                    continue
            
            # Single-character operators and delimiters
            if line[i] in self.operators:
                tokens.append(Token(self.operators[line[i]], line[i], line_num, i))
                i += 1
                continue
            
            if line[i] in self.delimiters:
                tokens.append(Token(self.delimiters[line[i]], line[i], line_num, i))
                i += 1
                continue
            
            # Identifiers and keywords
            if line[i].isalpha() or line[i] == '_':
                start = i
                while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                
                identifier = line[start:i]
                token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
                tokens.append(Token(token_type, identifier, line_num, start))
                continue
            
            # Unknown character
            raise SyntaxError(f"Unexpected character '{line[i]}' at line {line_num}, column {i}")
        
        return tokens
    
    def tokenize_stream(self, text: str) -> Iterator[Token]:
        """
        Tokenize input text as a stream (generator)
        
        Args:
            text: Input DSL text
            
        Yields:
            Individual tokens
        """
        tokens = self.tokenize(text)
        for token in tokens:
            yield token
