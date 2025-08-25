# Gamma Scanner

Advanced string manipulation and pattern matching engine with a completely unique DSL syntax that doesn't resemble any existing programming language.

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
gamma scan rules.gamma target_file.txt --alert

# Show examples
gamma examples
```

## Unique DSL Syntax

Gamma Scanner features a completely original DSL syntax using unique keywords and natural flow operators. The syntax is intuitive and easy to use for comprehensive pattern matching.

### Basic Rule Structure

```gamma
HUNT RuleName:
    CONDITION:
        "literal_text"
```

### Advanced Rule Structure

```gamma
HUNT SQLInjection:
    LOOK FOR:
        sqli_pattern ~ text "' OR '1'='1" IGNORE case
        union_attack ~ text "UNION SELECT" IGNORE case
    WHEN:
        file HAS sqli_pattern EITHER content HOLDS union_attack
    THEN:
        ALERT "SQL injection detected!" with high_priority
```

## Complete DSL Reference

### Keywords

#### Primary Keywords
- **HUNT** - Defines a detection rule
- **SCAN** - Alternative to HUNT
- **FIND** - Alternative to HUNT  
- **SEEK** - Alternative to HUNT

#### Section Keywords
- **CONDITION** - Simple condition block
- **LOOK FOR** - Pattern definition section
- **WHEN** - Conditional logic section
- **THEN** - Action section
- **meta** - Metadata section

#### Logical Operators
- **ALSO** - Logical AND
- **EITHER** - Logical OR
- **UNLESS** - Logical NOT
- **HAS** - Contains check
- **HOLDS** - Alternative to HAS

#### Pattern Types
- **text** - Text pattern matching
- **regex** - Regular expression matching
- **hex** - Hexadecimal pattern matching
- **base64** - Base64 encoded patterns

#### Modifiers
- **IGNORE case** - Case-insensitive matching
- **WHOLE word** - Word boundary matching
- **ASCII** - ASCII encoding
- **WIDE** - Wide character encoding

### Operators

- **~** - Pattern assignment operator
- **->** - Flow operator
- **=** - Equality operator
- **!=** - Inequality operator
- **>** - Greater than
- **<** - Less than
- **>=** - Greater than or equal
- **<=** - Less than or equal

### Built-in Functions

#### String Functions
- `length(string)` - Get string length
- `upper(string)` - Convert to uppercase
- `lower(string)` - Convert to lowercase
- `substr(string, start, length)` - Extract substring
- `replace(string, old, new)` - Replace text

#### Encoding Functions
- `base64_encode(data)` - Base64 encode
- `base64_decode(data)` - Base64 decode
- `url_encode(data)` - URL encode
- `url_decode(data)` - URL decode
- `hex_encode(data)` - Hexadecimal encode
- `hex_decode(data)` - Hexadecimal decode

#### Hash Functions
- `md5(data)` - MD5 hash
- `sha1(data)` - SHA1 hash
- `sha256(data)` - SHA256 hash

#### Analysis Functions
- `entropy(data)` - Calculate entropy
- `regex_match(pattern, text)` - Regex matching
- `contains(text, substring)` - Substring check

## Syntax Examples

### 1. Simple Literal Matching

```gamma
HUNT PasswordDetection:
    CONDITION:
        "password"
```

### 2. Case-Insensitive Pattern

```gamma
HUNT MalwareDetection:
    LOOK FOR:
        malware_sig ~ text "malicious" IGNORE case
    WHEN:
        content HAS malware_sig
    THEN:
        ALERT "Malware detected!"
```

### 3. Multiple Patterns with Logic

```gamma
HUNT SQLInjection:
    LOOK FOR:
        sqli1 ~ text "' OR 1=1" IGNORE case
        sqli2 ~ text "UNION SELECT" IGNORE case
        sqli3 ~ text "DROP TABLE" IGNORE case
    WHEN:
        content HAS sqli1 EITHER content HAS sqli2 EITHER content HAS sqli3
    THEN:
        ALERT "SQL injection attempt detected!"
```

### 4. Regex Pattern Matching

```gamma
HUNT EmailExtraction:
    LOOK FOR:
        email_pattern ~ regex "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    WHEN:
        content HAS email_pattern
    THEN:
        REPORT "Email found" -> security_team
```

### 5. Hexadecimal Pattern Detection

```gamma
HUNT ExecutableSignature:
    LOOK FOR:
        pe_header ~ hex "4D 5A 90 00"
        elf_header ~ hex "7F 45 4C 46"
    WHEN:
        file HAS pe_header EITHER file HAS elf_header
    THEN:
        ALERT "Executable file detected!"
```

### 6. Complex Conditional Logic

```gamma
HUNT AdvancedThreat:
    LOOK FOR:
        cmd_inject ~ text "cmd.exe" IGNORE case
        powershell ~ text "powershell" IGNORE case
        base64_data ~ regex "[A-Za-z0-9+/=]{20,}"
    WHEN:
        (content HAS cmd_inject EITHER content HAS powershell) 
        ALSO content HAS base64_data 
        ALSO length(content) > 1000
    THEN:
        ALERT "Advanced threat detected!" with critical_priority
        REPORT to incident_response
```

### 7. Built-in Function Usage

```gamma
HUNT EncodedContent:
    LOOK FOR:
        suspicious_b64 ~ text base64_decode($content)
    WHEN:
        entropy($content) > 6.0 
        ALSO length($content) > 100
        ALSO contains(suspicious_b64, "malware")
    THEN:
        ALERT "Encoded malicious content!"
```

### 8. Metadata Section

```gamma
HUNT WebShellDetection:
    meta:
        author = "Security Team"
        description = "Detects common web shell patterns"
        version = "1.2"
        category = "web_security"
        reference = "https://owasp.org/webshells"
        created = "2024-01-01"
        
    LOOK FOR:
        php_shell ~ text "<?php system($_GET"
        asp_shell ~ text "<%eval request"
        jsp_shell ~ text "<%Runtime.getRuntime().exec"
        
    WHEN:
        content HAS php_shell EITHER content HAS asp_shell EITHER content HAS jsp_shell
        
    THEN:
        ALERT "Web shell detected!" with high_priority
        REPORT to security_team
        QUARANTINE file
```

### 9. File Analysis Patterns

```gamma
HUNT SensitiveDataLeak:
    LOOK FOR:
        ssn_pattern ~ regex "\b\d{3}-\d{2}-\d{4}\b"
        cc_pattern ~ regex "\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"
        api_key ~ regex "[Aa][Pp][Ii]_?[Kk][Ee][Yy].*[A-Za-z0-9]{32,}"
        
    WHEN:
        content HAS ssn_pattern 
        EITHER content HAS cc_pattern 
        EITHER content HAS api_key
        
    THEN:
        ALERT "Sensitive data exposure!" with critical_priority
        CLASSIFY as "PII_LEAK"
        NOTIFY compliance_team
```

### 10. Network Security Patterns

```gamma
HUNT NetworkThreat:
    LOOK FOR:
        ip_pattern ~ regex "\b(?:\d{1,3}\.){3}\d{1,3}\b"
        port_scan ~ text "nmap"
        reverse_shell ~ text "/bin/sh"
        
    WHEN:
        content HAS ip_pattern 
        ALSO (content HAS port_scan EITHER content HAS reverse_shell)
        ALSO length(content) > 50
        
    THEN:
        ALERT "Network threat detected!"
        BLOCK source_ip
        LOG to security_events
```

## Command Line Usage

### Scanning Commands

```bash
# Basic file scanning
gamma scan rules.gamma target_file.txt

# Directory scanning with alerts
gamma scan malware_rules.gamma /suspicious/directory --alert --recursive

# Verbose output with reporting
gamma scan security_rules.gamma logs/ --verbose --report --output results.json

# Hunt for specific threats
gamma hunt apt_rules.gamma network_logs/ --alert
```

### Rule Development

```bash
# Validate rule syntax
gamma validate my_rules.gamma

# Test rules against sample data
gamma test rules.gamma --input test_data.txt

# Compile rules and check syntax
gamma compile advanced_rules.gamma --check-syntax

# Interactive rule development
gamma interactive
```

### Analysis Commands

```bash
# Comprehensive file analysis
gamma analyze document.txt --threats --pii --secrets

# Performance benchmarking
gamma benchmark rules.gamma dataset/ --iterations 100

# Show built-in examples
gamma examples
```

## Python API

### Basic Usage

```python
from gamma_scanner import GammaScanner

# Initialize scanner
scanner = GammaScanner()

# Simple rule compilation and matching
rule = '''
HUNT TestPattern:
    CONDITION:
        "malware"
'''

success = scanner.compile_rule(rule)
if success:
    results = scanner.match("This file contains malware")
    print(f"Matches found: {len(results)}")
```

### Advanced API Usage

```python
from gamma_scanner import GammaScanner
import json

scanner = GammaScanner()

# Load rules from file
compiled_rules = scanner.load_rules_from_file("security_rules.gamma")
print(f"Loaded {len(compiled_rules)} rules")

# Analyze content
content = "Suspicious content with potential threats"
matches = scanner.match(content)

# Process results
for match in matches:
    print(f"Rule: {match['rule_name']}")
    print(f"Match details: {json.dumps(match, indent=2)}")

# Access compiled rules
for rule_name, rule_obj in scanner.compiled_rules.items():
    print(f"Rule {rule_name}: {rule_obj.name}")
```

### Batch Processing

```python
from gamma_scanner import GammaScanner
import os

scanner = GammaScanner()
scanner.load_rules_from_file("comprehensive_rules.gamma")

# Process multiple files
results = []
for root, dirs, files in os.walk("/target/directory"):
    for file in files:
        file_path = os.path.join(root, file)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            matches = scanner.match(content)
            if matches:
                results.append({
                    'file': file_path,
                    'matches': len(matches),
                    'details': matches
                })
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

print(f"Found threats in {len(results)} files")
```

## Features

- **Unique DSL**: Completely original syntax that doesn't resemble any existing programming language
- **Natural Keywords**: Uses intuitive keywords like HUNT, SCAN, LOOK FOR, WHEN, ALSO, EITHER, UNLESS
- **Security Focus**: Built-in patterns for common security threats and vulnerabilities
- **High Performance**: Optimized execution engine with rule compilation and caching
- **Comprehensive CLI**: Full-featured command-line interface with multiple scanning modes
- **Pattern Library**: Extensible pattern matching with regex, hex, and text patterns
- **Built-in Functions**: Rich set of string manipulation, encoding, and analysis functions
- **Metadata Support**: Rule documentation and organization with metadata sections
- **Flexible Output**: JSON, XML, and custom report formats
- **Interactive Mode**: Real-time rule testing and development environment

## Performance

Gamma Scanner is designed for high-performance pattern matching:

- **Rule Compilation**: Rules are compiled once and cached for repeated use
- **Parallel Processing**: Multi-threaded scanning for large datasets  
- **Memory Efficient**: Streaming processing for large files
- **Optimized Matching**: Advanced pattern matching algorithms
- **Benchmark Tools**: Built-in performance measurement and optimization

## Best Practices

### Rule Organization

```gamma
# Use descriptive rule names
HUNT WebShellPHPVariant1:
    meta:
        category = "web_security"
        severity = "high"
        
    CONDITION:
        "<?php system($_GET"
```

### Pattern Efficiency

```gamma
# Combine related patterns for better performance
HUNT SQLInjectionPatterns:
    LOOK FOR:
        union_select ~ text "UNION SELECT" IGNORE case
        or_1_equals_1 ~ text "' OR '1'='1" IGNORE case
        drop_table ~ text "DROP TABLE" IGNORE case
        
    WHEN:
        content HAS union_select EITHER content HAS or_1_equals_1 EITHER content HAS drop_table
```

### Error Handling

```gamma
# Use metadata for rule documentation
HUNT DatabaseThreats:
    meta:
        description = "Detects database-related security threats"
        false_positives = "May trigger on legitimate SQL documentation"
        mitigation = "Review context before taking action"
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

## Support

For questions, issues, or feature requests, please visit our GitHub repository or contact the development team.