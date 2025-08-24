"""
Gamma Scanner - Advanced String Manipulation and Pattern Matching Engine

This package provides a comprehensive solution for text analysis, pattern matching,
and string transformation with a unique, intuitive DSL syntax.
"""

from .main import GammaScanner
from .dsl_lexer import StringForgeLexer
from .dsl_parser import StringForgeParser
from .dsl_interpreter import StringForgeInterpreter
from .dsl_ast import *
from .dsl_engine import StringForgeEngine

__version__ = "1.0.2"
__author__ = "Harish Santhanalakshmi Ganesan"
__email__ = "harishsg99@gmail.com"

__all__ = [
    "GammaScanner",
    "StringForgeLexer", 
    "StringForgeParser",
    "StringForgeInterpreter",
    "StringForgeEngine",
]