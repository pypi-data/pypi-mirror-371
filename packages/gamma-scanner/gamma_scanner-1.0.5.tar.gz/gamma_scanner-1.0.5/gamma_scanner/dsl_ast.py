"""
StringForge DSL Abstract Syntax Tree (AST) Node Definitions
"""

from abc import ABC, abstractmethod
from typing import List, Any, Optional, Union
from dataclasses import dataclass

class ASTNode(ABC):
    """Base class for all AST nodes"""
    pass

class StatementNode(ASTNode):
    """Base class for statement nodes"""
    pass

class ExpressionNode(ASTNode):
    """Base class for expression nodes"""
    pass

@dataclass
class MetadataNode(ASTNode):
    """Node representing metadata section"""
    entries: List['MetadataEntryNode']

@dataclass
class MetadataEntryNode(ASTNode):
    """Node representing a single metadata entry"""
    key: str
    value: str

@dataclass
class ProgramNode(ASTNode):
    """Root node representing the entire program"""
    statements: List[StatementNode]
    metadata: Optional[MetadataNode] = None

@dataclass
class StringsNode(ASTNode):
    """Node representing strings section"""
    string_definitions: List['StringDefinitionNode']

@dataclass
class StringDefinitionNode(ASTNode):
    """Node representing a single string definition"""
    identifier: str  # $string1, $pattern, etc.
    value: str       # "text" or /regex/ or {hex}
    string_type: str # "text", "regex", "hex"
    modifiers: List[str] = None  # nocase, wide, ascii, fullword

@dataclass
class RuleNode(StatementNode):
    """Node representing a rule definition"""
    name: str
    conditions: List['ConditionNode']
    actions: List['ActionNode']
    metadata: Optional[MetadataNode] = None
    strings: Optional[StringsNode] = None

@dataclass
class ConditionNode(ExpressionNode):
    """Node representing a condition in a rule"""
    condition_type: str  # match, contains, starts_with, ends_with, regex_match, etc.
    pattern: ExpressionNode
    target: Optional[ExpressionNode] = None
    flags: Optional[ExpressionNode] = None

@dataclass
class ActionNode(StatementNode):
    """Node representing an action in a rule"""
    action_type: str  # replace, extract, transform
    pattern: ExpressionNode
    replacement: Optional[ExpressionNode] = None
    target: Optional[ExpressionNode] = None

@dataclass
class AssignmentNode(StatementNode):
    """Node representing variable assignment"""
    identifier: str
    value: ExpressionNode

@dataclass
class ExpressionStatementNode(StatementNode):
    """Node representing an expression used as a statement"""
    expression: ExpressionNode

@dataclass
class IfNode(StatementNode):
    """Node representing if statement"""
    condition: ExpressionNode
    then_statements: List[StatementNode]
    else_statements: List[StatementNode]

@dataclass
class BinaryOpNode(ExpressionNode):
    """Node representing binary operation"""
    left: ExpressionNode
    operator: str
    right: ExpressionNode

@dataclass
class UnaryOpNode(ExpressionNode):
    """Node representing unary operation"""
    operator: str
    operand: ExpressionNode

@dataclass
class FunctionCallNode(ExpressionNode):
    """Node representing function call"""
    function: ExpressionNode
    arguments: List[ExpressionNode]

@dataclass
class MemberAccessNode(ExpressionNode):
    """Node representing member access (object.member)"""
    object: ExpressionNode
    member: str

@dataclass
class IndexAccessNode(ExpressionNode):
    """Node representing index access (array[index])"""
    object: ExpressionNode
    index: ExpressionNode

@dataclass
class LiteralNode(ExpressionNode):
    """Node representing literal values"""
    value: Any
    literal_type: str  # string, regex, int, float, boolean

@dataclass
class IdentifierNode(ExpressionNode):
    """Node representing identifiers/variables"""
    name: str

@dataclass
class ArrayLiteralNode(ExpressionNode):
    """Node representing array literals"""
    elements: List[ExpressionNode]

# YARA-like expression nodes
@dataclass
class StringCountNode(ExpressionNode):
    """Node representing string count (#$string)"""
    string_identifier: str

@dataclass
class StringOffsetNode(ExpressionNode):
    """Node representing string offset (@$string[index])"""
    string_identifier: str
    index: Optional[ExpressionNode] = None

@dataclass
class StringLengthNode(ExpressionNode):
    """Node representing string length (!$string[index])"""
    string_identifier: str
    index: Optional[ExpressionNode] = None

@dataclass
class ForExpressionNode(ExpressionNode):
    """Node representing 'for' expressions (for any/all of them)"""
    quantifier: str  # "any", "all", or number
    iterator: str    # "of"
    string_set: ExpressionNode  # "them" or ($s1, $s2, ...)
    condition: Optional[ExpressionNode] = None  # optional condition

@dataclass
class AtExpressionNode(ExpressionNode):
    """Node representing 'at' expressions ($string at offset)"""
    string_expr: ExpressionNode
    offset: ExpressionNode

@dataclass
class InExpressionNode(ExpressionNode):
    """Node representing 'in' expressions ($string in range)"""
    string_expr: ExpressionNode
    range_start: ExpressionNode
    range_end: ExpressionNode

@dataclass
class FilesizeNode(ExpressionNode):
    """Node representing filesize"""
    pass

@dataclass
class EntrypointNode(ExpressionNode):
    """Node representing entrypoint"""
    pass

@dataclass
class HexStringNode(ExpressionNode):
    """Node representing hex string with wildcards"""
    hex_pattern: str  # "01 02 ?? 04"

@dataclass
class StringIdentifierNode(ExpressionNode):
    """Node representing string identifier ($string1, $pattern)"""
    identifier: str

@dataclass
class StringSetNode(ExpressionNode):
    """Node representing string set ($s1, $s2, $s3) or 'them'"""
    strings: List[str]  # list of string identifiers or ['them']

# Built-in function nodes for string operations
@dataclass
class LengthNode(ExpressionNode):
    """Node representing length function"""
    target: ExpressionNode

@dataclass
class CountNode(ExpressionNode):
    """Node representing count function"""
    pattern: ExpressionNode
    target: ExpressionNode

@dataclass
class SplitNode(ExpressionNode):
    """Node representing split function"""
    delimiter: ExpressionNode
    target: ExpressionNode
    max_splits: Optional[ExpressionNode] = None

@dataclass
class JoinNode(ExpressionNode):
    """Node representing join function"""
    delimiter: ExpressionNode
    array: ExpressionNode

@dataclass
class UpperNode(ExpressionNode):
    """Node representing upper function"""
    target: ExpressionNode

@dataclass
class LowerNode(ExpressionNode):
    """Node representing lower function"""
    target: ExpressionNode

@dataclass
class StripNode(ExpressionNode):
    """Node representing strip function"""
    target: ExpressionNode
    chars: Optional[ExpressionNode] = None

# Advanced pattern matching nodes
@dataclass
class RegexNode(ExpressionNode):
    """Node representing compiled regex pattern"""
    pattern: str
    flags: Optional[str] = None

@dataclass
class MatchResultNode(ExpressionNode):
    """Node representing match result with capture groups"""
    match_text: str
    groups: List[str]
    start_position: int
    end_position: int

# AST Visitor pattern for traversal
class ASTVisitor(ABC):
    """Base class for AST visitors"""
    
    @abstractmethod
    def visit(self, node: ASTNode) -> Any:
        """Visit an AST node"""
        pass
    
    def visit_program(self, node: ProgramNode) -> Any:
        """Visit program node"""
        results = []
        for statement in node.statements:
            results.append(self.visit(statement))
        
        # Include metadata if present
        metadata = None
        if node.metadata:
            metadata = self.visit_metadata(node.metadata)
            
        return {'statements': results, 'metadata': metadata}
    
    def visit_rule(self, node: RuleNode) -> Any:
        """Visit rule node"""
        conditions = [self.visit(cond) for cond in node.conditions]
        actions = [self.visit(action) for action in node.actions]
        
        # Include metadata if present
        metadata = None
        if node.metadata:
            metadata = self.visit_metadata(node.metadata)
            
        return {'name': node.name, 'conditions': conditions, 'actions': actions, 'metadata': metadata}
    
    def visit_condition(self, node: ConditionNode) -> Any:
        """Visit condition node"""
        pattern = self.visit(node.pattern)
        target = self.visit(node.target) if node.target else None
        flags = self.visit(node.flags) if node.flags else None
        return {
            'type': node.condition_type,
            'pattern': pattern,
            'target': target,
            'flags': flags
        }
    
    def visit_action(self, node: ActionNode) -> Any:
        """Visit action node"""
        pattern = self.visit(node.pattern)
        replacement = self.visit(node.replacement) if node.replacement else None
        target = self.visit(node.target) if node.target else None
        return {
            'type': node.action_type,
            'pattern': pattern,
            'replacement': replacement,
            'target': target
        }
    
    def visit_assignment(self, node: AssignmentNode) -> Any:
        """Visit assignment node"""
        value = self.visit(node.value)
        return {'identifier': node.identifier, 'value': value}
    
    def visit_if(self, node: IfNode) -> Any:
        """Visit if node"""
        condition = self.visit(node.condition)
        then_statements = [self.visit(stmt) for stmt in node.then_statements]
        else_statements = [self.visit(stmt) for stmt in node.else_statements]
        return {
            'condition': condition,
            'then': then_statements,
            'else': else_statements
        }
    
    def visit_binary_op(self, node: BinaryOpNode) -> Any:
        """Visit binary operation node"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        return {'operator': node.operator, 'left': left, 'right': right}
    
    def visit_unary_op(self, node: UnaryOpNode) -> Any:
        """Visit unary operation node"""
        operand = self.visit(node.operand)
        return {'operator': node.operator, 'operand': operand}
    
    def visit_function_call(self, node: FunctionCallNode) -> Any:
        """Visit function call node"""
        function = self.visit(node.function)
        arguments = [self.visit(arg) for arg in node.arguments]
        return {'function': function, 'arguments': arguments}
    
    def visit_member_access(self, node: MemberAccessNode) -> Any:
        """Visit member access node"""
        object_val = self.visit(node.object)
        return {'object': object_val, 'member': node.member}
    
    def visit_index_access(self, node: IndexAccessNode) -> Any:
        """Visit index access node"""
        object_val = self.visit(node.object)
        index = self.visit(node.index)
        return {'object': object_val, 'index': index}
    
    def visit_literal(self, node: LiteralNode) -> Any:
        """Visit literal node"""
        return {'value': node.value, 'type': node.literal_type}
    
    def visit_identifier(self, node: IdentifierNode) -> Any:
        """Visit identifier node"""
        return {'name': node.name}
    
    def visit_array_literal(self, node: ArrayLiteralNode) -> Any:
        """Visit array literal node"""
        elements = [self.visit(elem) for elem in node.elements]
        return {'elements': elements}
    
    def visit_metadata(self, node: MetadataNode) -> Any:
        """Visit metadata node"""
        entries = []
        for entry in node.entries:
            entries.append(self.visit_metadata_entry(entry))
        return {'entries': entries}
    
    def visit_metadata_entry(self, node: MetadataEntryNode) -> Any:
        """Visit metadata entry node"""
        return {'key': node.key, 'value': node.value}

def print_ast(node: ASTNode, indent: int = 0) -> str:
    """Pretty print AST for debugging"""
    prefix = "  " * indent
    
    if isinstance(node, ProgramNode):
        result = f"{prefix}Program:\n"
        for stmt in node.statements:
            result += print_ast(stmt, indent + 1)
        return result
    
    elif isinstance(node, RuleNode):
        result = f"{prefix}Rule '{node.name}':\n"
        
        # Print metadata if present
        if node.metadata:
            result += f"{prefix}  Metadata:\n"
            result += print_ast(node.metadata, indent + 2)
        
        result += f"{prefix}  Conditions:\n"
        for cond in node.conditions:
            result += print_ast(cond, indent + 2)
        result += f"{prefix}  Actions:\n"
        for action in node.actions:
            result += print_ast(action, indent + 2)
        return result
    
    elif isinstance(node, ConditionNode):
        result = f"{prefix}Condition ({node.condition_type}):\n"
        result += f"{prefix}  Pattern: {print_ast(node.pattern, 0).strip()}\n"
        if node.target:
            result += f"{prefix}  Target: {print_ast(node.target, 0).strip()}\n"
        return result
    
    elif isinstance(node, LiteralNode):
        return f"{prefix}Literal: {node.value} ({node.literal_type})\n"
    
    elif isinstance(node, IdentifierNode):
        return f"{prefix}Identifier: {node.name}\n"
    
    elif isinstance(node, MetadataNode):
        result = f"{prefix}Metadata:\n"
        for entry in node.entries:
            result += print_ast(entry, indent + 1)
        return result
    
    elif isinstance(node, MetadataEntryNode):
        return f"{prefix}{node.key} = {node.value}\n"
    
    else:
        return f"{prefix}{type(node).__name__}\n"
