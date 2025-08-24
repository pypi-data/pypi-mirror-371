# Gamma Scanner

Advanced string manipulation and pattern matching engine with unique DSL syntax.

## Installation

```bash
pip install gamma-scanner
```

## Quick Start

```bash
# Run the CLI
gamma-scanner --help

# Or use the short command
gamma --help

# Interactive mode
gamma interactive

# Scan files for threats
gamma scan rules.gamma target_file.txt

# Show examples
gamma examples
```

## Unique DSL Syntax

Gamma Scanner features a completely original DSL syntax that uses natural language keywords:

```gamma
HUNT SQLInjection:
    LOOK FOR:
        sqli_pattern ~ text "' OR '1'='1" IGNORE case
        union_attack ~ text "UNION SELECT" IGNORE case
    WHEN:
        file HAS sqli_pattern EITHER content HOLDS union_attack
    THEN:
        ALERT "SQL injection detected!"
```

## Features

- **Unique DSL**: Natural language-like syntax for pattern matching
- **Security Focus**: Built-in patterns for common security threats
- **High Performance**: Optimized execution engine with caching
- **CLI Tools**: Comprehensive command-line interface
- **Pattern Library**: Extensible pattern matching capabilities

## Commands

- `scan` - Scan files/directories for security threats
- `hunt` - Hunt for specific threats using rules
- `detect` - Detect patterns in files
- `validate` - Validate DSL rule syntax
- `test` - Test rules against sample data
- `compile` - Compile DSL rules
- `analyze` - Comprehensive file analysis
- `interactive` - Interactive DSL shell
- `benchmark` - Benchmark rule performance
- `examples` - Show DSL syntax examples

## Python API

```python
from gamma_scanner import GammaScanner

scanner = GammaScanner()

# Compile a rule
rule = '''
HUNT TestRule:
    LOOK FOR:
        pattern ~ text "test" IGNORE case
    WHEN:
        content HAS pattern
    THEN:
        ALERT "Found test!"
'''

success = scanner.compile_rule(rule)
if success:
    results = scanner.match("This is a test string")
    print(results)
```

## License

MIT License - see LICENSE file for details.