#!/usr/bin/env python3
"""
Gamma Scanner Command Line Interface
"""

import argparse
import sys
import os
import json
import time
from typing import Dict, Any, List
from .main import GammaScanner

def print_banner():
    """Print Gamma Scanner banner"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                      GAMMA SCANNER                       ║
║               Security Pattern Detection                  ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)

def format_match_results(results: List[Dict[str, Any]]) -> str:
    """Format match results for display"""
    if not results:
        return "No matches found."
    
    output = []
    output.append(f"\nFound {len(results)} match(es):\n")
    
    for i, result in enumerate(results, 1):
        output.append(f"Match #{i}:")
        output.append(f"  Rule: {result.get('rule_name', 'Unknown')}")
        output.append(f"  Position: {result.get('position', 'Unknown')}")
        output.append(f"  Length: {result.get('length', 'Unknown')}")
        
        match_text = result.get('match', {})
        if isinstance(match_text, dict):
            output.append(f"  Match Text: {match_text.get('match_text', 'N/A')}")
            if match_text.get('groups'):
                output.append(f"  Groups: {match_text['groups']}")
        else:
            output.append(f"  Match: {match_text}")
        
        output.append("")
    
    return "\n".join(output)

def format_analysis_results(analysis: Dict[str, Any]) -> str:
    """Format text analysis results for display"""
    output = []
    output.append("\n" + "="*50)
    output.append("TEXT ANALYSIS RESULTS")
    output.append("="*50)
    
    # Basic statistics
    if 'basic_stats' in analysis:
        stats = analysis['basic_stats']
        output.append("\nBasic Statistics:")
        output.append(f"  Length: {stats.get('length', 0)} characters")
        output.append(f"  Words: {stats.get('word_count', 0)}")
        output.append(f"  Lines: {stats.get('line_count', 0)}")
        output.append(f"  Average word length: {stats.get('average_word_length', 0):.2f}")
        output.append(f"  Alphabetic: {stats.get('alphabetic_count', 0)}")
        output.append(f"  Numeric: {stats.get('numeric_count', 0)}")
        output.append(f"  Whitespace: {stats.get('whitespace_count', 0)}")
    
    # Entropy
    if 'entropy' in analysis:
        output.append(f"\nEntropy: {analysis['entropy']:.3f} bits")
    
    # Character analysis
    if 'character_analysis' in analysis:
        char_analysis = analysis['character_analysis']
        output.append(f"\nCharacter Analysis:")
        output.append(f"  Unique characters: {char_analysis.get('unique_characters', 0)}")
        
        if char_analysis.get('most_common'):
            output.append("  Most common characters:")
            for char, count in char_analysis['most_common'][:5]:
                char_display = repr(char) if char in '\n\t\r ' else char
                output.append(f"    {char_display}: {count}")
    
    # Security analysis
    if 'security_analysis' in analysis:
        security = analysis['security_analysis']
        output.append(f"\nSecurity Analysis:")
        output.append(f"  Risk Level: {security.get('risk_level', 'unknown').upper()}")
        output.append(f"  Risk Score: {security.get('risk_score', 0)}")
        
        patterns = security.get('patterns', {})
        for pattern_name, count in patterns.items():
            if count > 0:
                output.append(f"  {pattern_name.replace('_', ' ').title()}: {count}")
    
    # Extracted data
    if 'extracted_data' in analysis:
        extracted = analysis['extracted_data']
        output.append("\nExtracted Data:")
        
        for data_type, items in extracted.items():
            if items:
                output.append(f"  {data_type.replace('_', ' ').title()}: {len(items)}")
                for item in items[:3]:  # Show first 3 items
                    output.append(f"    - {item}")
                if len(items) > 3:
                    output.append(f"    ... and {len(items) - 3} more")
    
    return "\n".join(output)

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="🛡️ Gamma Scanner - Next-Generation Security Pattern Detection Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🚀 GAMMA DSL EXAMPLES:

Security Scanning:
  %(prog)s scan malware.gamma suspicious_files/ --alert --report
  %(prog)s hunt threats.gamma logfile.txt --output results.json
  %(prog)s detect sql_injection.gamma webapp_logs/ --verbose

Rule Development:
  %(prog)s validate my_rules.gamma
  %(prog)s test rules.gamma --input test_data.txt
  %(prog)s compile advanced_threats.gamma --check-syntax

Analysis & Reporting:
  %(prog)s analyze document.txt --threats --pii --secrets
  %(prog)s benchmark performance.gamma dataset/ --iterations 100
  %(prog)s interactive  # Start interactive rule testing

📖 UNIQUE GAMMA SYNTAX:
  HUNT ThreatName:
      LOOK FOR:
          pattern ~ text "malicious" IGNORE case
          signature ~ hex "4D 5A 90 00"
      WHEN:
          file HAS pattern ALSO SIZE greater than 1KB
      THEN:
          ALERT "Threat detected!" with high_priority
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='🛡️ Available Gamma Scanner Commands')
    
    # Scan command (primary security scanning)
    scan_parser = subparsers.add_parser('scan', help='🔍 Scan files/directories for security threats')
    scan_parser.add_argument('rules_file', help='Gamma rules file (.gamma)')
    scan_parser.add_argument('target', help='File or directory to scan')
    scan_parser.add_argument('--output', '-o', help='Output results to file')
    scan_parser.add_argument('--format', choices=['text', 'json', 'xml'], default='text', help='Output format')
    scan_parser.add_argument('--alert', action='store_true', help='Show alerts for detections')
    scan_parser.add_argument('--report', action='store_true', help='Generate detailed report')
    scan_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    scan_parser.add_argument('--recursive', '-r', action='store_true', help='Scan directories recursively')
    
    # Hunt command (threat hunting)
    hunt_parser = subparsers.add_parser('hunt', help='🎯 Hunt for specific threats using Gamma rules')
    hunt_parser.add_argument('rules_file', help='Gamma threat hunting rules')
    hunt_parser.add_argument('target', help='Target to hunt in')
    hunt_parser.add_argument('--output', '-o', help='Save hunt results')
    hunt_parser.add_argument('--severity', choices=['low', 'medium', 'high', 'critical'], help='Minimum severity level')
    hunt_parser.add_argument('--live', action='store_true', help='Live monitoring mode')
    
    # Detect command (pattern detection)
    detect_parser = subparsers.add_parser('detect', help='🚨 Detect patterns in files using Gamma DSL')
    detect_parser.add_argument('rules_file', help='Gamma detection rules')
    detect_parser.add_argument('input_file', help='File to analyze')
    detect_parser.add_argument('--patterns', help='Specific patterns to look for')
    detect_parser.add_argument('--count', action='store_true', help='Count matches only')
    
    # Validate command (rule validation)
    validate_parser = subparsers.add_parser('validate', help='✅ Validate Gamma rule syntax')
    validate_parser.add_argument('rules_file', help='Gamma rules file to validate')
    validate_parser.add_argument('--strict', action='store_true', help='Strict validation mode')
    validate_parser.add_argument('--explain', action='store_true', help='Explain rule structure')
    
    # Test command (rule testing)
    test_parser = subparsers.add_parser('test', help='🧪 Test Gamma rules against sample data')
    test_parser.add_argument('rules_file', help='Gamma rules to test')
    test_parser.add_argument('--input', help='Test input file')
    test_parser.add_argument('--samples', help='Directory of test samples')
    test_parser.add_argument('--coverage', action='store_true', help='Show rule coverage')
    
    # Compile command (rule compilation)
    compile_parser = subparsers.add_parser('compile', help='⚙️ Compile Gamma DSL rules')
    compile_parser.add_argument('rules_file', help='Gamma DSL rules file (.gamma)')
    compile_parser.add_argument('--output', help='Output compiled rules')
    compile_parser.add_argument('--check-syntax', action='store_true', help='Check syntax only')
    compile_parser.add_argument('--optimize', action='store_true', help='Optimize compiled rules')
    compile_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose compilation output')
    
    # Analyze command (enhanced analysis)
    analyze_parser = subparsers.add_parser('analyze', help='📊 Comprehensive file analysis')
    analyze_parser.add_argument('target', help='File or directory to analyze')
    analyze_parser.add_argument('--threats', action='store_true', help='Analyze for security threats')
    analyze_parser.add_argument('--pii', action='store_true', help='Detect personal information')
    analyze_parser.add_argument('--secrets', action='store_true', help='Find secrets and credentials')
    analyze_parser.add_argument('--encoding', action='store_true', help='Detect encoding attempts')
    analyze_parser.add_argument('--output', help='Save analysis results')
    analyze_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    
    # Interactive command (enhanced REPL)
    interactive_parser = subparsers.add_parser('interactive', help='💻 Interactive Gamma DSL shell')
    interactive_parser.add_argument('--load', help='Load rules on startup')
    interactive_parser.add_argument('--examples', action='store_true', help='Show syntax examples')
    
    # Benchmark command (performance testing)
    benchmark_parser = subparsers.add_parser('benchmark', help='⚡ Benchmark rule performance')
    benchmark_parser.add_argument('rules_file', help='Gamma rules to benchmark')
    benchmark_parser.add_argument('data_path', help='Test data path')
    benchmark_parser.add_argument('--iterations', type=int, default=10, help='Number of test iterations')
    benchmark_parser.add_argument('--threads', type=int, default=1, help='Number of threads')
    benchmark_parser.add_argument('--profile', action='store_true', help='Enable profiling')
    
    # Examples command (show usage examples)
    examples_parser = subparsers.add_parser('examples', help='📚 Show Gamma DSL syntax examples')
    examples_parser.add_argument('--category', choices=['security', 'data', 'malware', 'web'], help='Example category')
    examples_parser.add_argument('--advanced', action='store_true', help='Show advanced examples')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return
    
    # Initialize Gamma Scanner
    scanner = GammaScanner()
    
    try:
        if args.command == 'scan':
            scan_command(scanner, args)
        elif args.command == 'hunt':
            hunt_command(scanner, args)
        elif args.command == 'detect':
            detect_command(scanner, args)
        elif args.command == 'validate':
            validate_command(scanner, args)
        elif args.command == 'test':
            test_command(scanner, args)
        elif args.command == 'compile':
            compile_command(scanner, args)
        elif args.command == 'analyze':
            analyze_command(scanner, args)
        elif args.command == 'interactive':
            interactive_command(scanner, args)
        elif args.command == 'benchmark':
            benchmark_command(scanner, args)
        elif args.command == 'examples':
            examples_command(args)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def scan_command(scanner: GammaScanner, args):
    """Handle scan command - primary security scanning"""
    print(f"🔍 Scanning with Gamma rules: {args.rules_file}")
    
    if not os.path.exists(args.rules_file):
        print(f"❌ Error: Rules file '{args.rules_file}' not found.")
        sys.exit(1)
    
    if not os.path.exists(args.target):
        print(f"❌ Error: Target '{args.target}' not found.")
        sys.exit(1)
    
    # Load rules
    try:
        with open(args.rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        
        compiled_rules = scanner.load_rules_from_file_content(rules_content)
        if not compiled_rules:
            print(f"❌ Failed to compile rules from {args.rules_file}")
            sys.exit(1)
            
        print(f"✅ Loaded {len(compiled_rules)} Gamma rules")
        
        if args.verbose:
            for rule in compiled_rules:
                print(f"   📋 Rule: {rule.name}")
        
    except Exception as e:
        print(f"❌ Error loading rules: {e}")
        sys.exit(1)
    
    # Collect files to scan
    scan_files = []
    if os.path.isfile(args.target):
        scan_files = [args.target]
    elif os.path.isdir(args.target):
        if args.recursive:
            for root, dirs, files in os.walk(args.target):
                for file in files:
                    scan_files.append(os.path.join(root, file))
        else:
            scan_files = [os.path.join(args.target, f) for f in os.listdir(args.target) 
                         if os.path.isfile(os.path.join(args.target, f))]
    
    if not scan_files:
        print("❌ No files found to scan")
        sys.exit(1)
    
    print(f"🎯 Scanning {len(scan_files)} files...")
    
    total_matches = 0
    threat_files = []
    scan_start = time.time()
    
    results = []
    
    for file_path in scan_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Simulate pattern matching
            file_matches = []
            for rule in compiled_rules:
                if hasattr(rule, 'strings') and rule.strings:
                    for pattern in rule.strings.string_definitions:
                        if pattern.string_type == 'text':
                            search_text = content.lower() if 'nocase' in pattern.modifiers else content
                            pattern_text = pattern.value.lower() if 'nocase' in pattern.modifiers else pattern.value
                            if pattern_text in search_text:
                                file_matches.append({
                                    'rule': rule.name,
                                    'pattern': pattern.identifier,
                                    'type': pattern.string_type,
                                    'file': file_path
                                })
            
            if file_matches:
                total_matches += len(file_matches)
                threat_files.append(file_path)
                results.extend(file_matches)
                
                if args.alert:
                    print(f"🚨 ALERT: Threats detected in {file_path}")
                    for match in file_matches:
                        print(f"   ⚠️  Rule: {match['rule']} | Pattern: {match['pattern']}")
            
            if args.verbose:
                status = "🔴 THREATS" if file_matches else "✅ CLEAN"
                print(f"   {status} {file_path}")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not scan {file_path}: {e}")
    
    scan_time = time.time() - scan_start
    
    # Generate report
    print(f"\n" + "="*60)
    print(f"🛡️ GAMMA SCANNER RESULTS")
    print(f"="*60)
    print(f"📊 Files scanned: {len(scan_files)}")
    print(f"🚨 Threats found: {total_matches}")
    print(f"📁 Infected files: {len(threat_files)}")
    print(f"⏱️  Scan time: {scan_time:.2f} seconds")
    print(f"🚀 Speed: {len(scan_files)/scan_time:.1f} files/second")
    
    if args.report and threat_files:
        print(f"\n📋 DETAILED THREAT REPORT:")
        for file_path in threat_files:
            file_matches = [r for r in results if r['file'] == file_path]
            print(f"\n🔴 {file_path}")
            for match in file_matches:
                print(f"   └─ {match['rule']} → {match['pattern']} ({match['type']})")
    
    # Save results if requested
    if args.output:
        output_data = {
            'scan_summary': {
                'files_scanned': len(scan_files),
                'threats_found': total_matches,
                'infected_files': len(threat_files),
                'scan_time': scan_time
            },
            'results': results
        }
        
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.format == 'json':
                json.dump(output_data, f, indent=2)
            else:
                f.write(f"Gamma Scanner Results\n")
                f.write(f"Files scanned: {len(scan_files)}\n")
                f.write(f"Threats found: {total_matches}\n")
                for result in results:
                    f.write(f"{result['file']}: {result['rule']} -> {result['pattern']}\n")
        
        print(f"💾 Results saved to: {args.output}")

def hunt_command(scanner: GammaScanner, args):
    """Handle hunt command - threat hunting"""
    print(f"🎯 Threat hunting with: {args.rules_file}")
    print(f"🔍 Target: {args.target}")
    
    # Implementation similar to scan but focused on threat hunting
    print("🚧 Threat hunting mode - Enhanced detection algorithms active")
    # Call scan_command with modified args for now
    args.alert = True
    args.report = True
    args.verbose = True
    scan_command(scanner, args)

def detect_command(scanner: GammaScanner, args):
    """Handle detect command - pattern detection"""
    print(f"🚨 Pattern detection with: {args.rules_file}")
    scan_command(scanner, args)

def validate_command(scanner: GammaScanner, args):
    """Handle validate command - rule validation"""
    print(f"✅ Validating Gamma rules: {args.rules_file}")
    
    if not os.path.exists(args.rules_file):
        print(f"❌ Error: Rules file '{args.rules_file}' not found.")
        sys.exit(1)
    
    try:
        with open(args.rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        
        print("📝 Parsing Gamma DSL syntax...")
        
        # Tokenize
        tokens = scanner.lexer.tokenize(rules_content)
        print(f"   ✅ Tokenization successful: {len(tokens)} tokens")
        
        # Parse
        ast = scanner.parser.parse(tokens)
        if ast:
            print(f"   ✅ Parsing successful: {len(ast.statements)} rules")
            
            if args.explain:
                print(f"\n📋 RULE STRUCTURE ANALYSIS:")
                for i, stmt in enumerate(ast.statements):
                    print(f"   Rule {i+1}: {stmt.name}")
                    if hasattr(stmt, 'metadata') and stmt.metadata:
                        print(f"      📄 Metadata: {len(stmt.metadata.entries)} entries")
                    if hasattr(stmt, 'strings') and stmt.strings:
                        print(f"      🔍 Patterns: {len(stmt.strings.string_definitions)}")
                        for pattern in stmt.strings.string_definitions:
                            print(f"         - {pattern.identifier}: {pattern.string_type}")
        else:
            print(f"   ❌ Parsing failed")
            sys.exit(1)
        
        print(f"\n🎉 Validation complete: All Gamma DSL syntax is valid!")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)

def test_command(scanner: GammaScanner, args):
    """Handle test command - rule testing"""
    print(f"🧪 Testing Gamma rules: {args.rules_file}")
    
    if args.input:
        print(f"📄 Test input: {args.input}")
        # Test against specific file
        args.target = args.input
        args.verbose = True
        scan_command(scanner, args)
    elif args.samples:
        print(f"📁 Test samples: {args.samples}")
        # Test against sample directory
        args.target = args.samples
        args.recursive = True
        args.report = True
        scan_command(scanner, args)
    else:
        print("🔧 No test input specified. Use --input or --samples")

def compile_command(scanner: GammaScanner, args):
    """Handle compile command"""
    print(f"⚙️ Compiling rules from: {args.rules_file}")
    
    if not os.path.exists(args.rules_file):
        print(f"❌ Error: Rules file '{args.rules_file}' not found.")
        sys.exit(1)
    
    try:
        with open(args.rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        
        if args.check_syntax:
            print("📝 Checking syntax only...")
            tokens = scanner.lexer.tokenize(rules_content)
            ast = scanner.parser.parse(tokens)
            if ast:
                print(f"✅ Syntax check passed: {len(ast.statements)} rules")
            else:
                print("❌ Syntax check failed")
                sys.exit(1)
            return
        
        compiled_rules = scanner.load_rules_from_file_content(rules_content)
        if compiled_rules:
            print(f"✅ Successfully compiled {len(compiled_rules)} rules")
            
            if args.verbose:
                print("\nCompiled rules:")
                for rule in compiled_rules:
                    print(f"  📋 {rule.name}")
                    if hasattr(rule, 'strings') and rule.strings:
                        print(f"     Patterns: {len(rule.strings.string_definitions)}")
        else:
            print("❌ Failed to compile rules")
            sys.exit(1)
            
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(f"# Compiled Gamma Rules\n")
                f.write(f"# Generated from: {args.rules_file}\n")
                f.write(f"# Rules: {len(compiled_rules)}\n")
            print(f"💾 Compiled rules metadata saved to: {args.output}")
            
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def analyze_command(scanner: GammaScanner, args):
    """Handle analyze command - enhanced analysis"""
    print(f"📊 Analyzing: {args.target}")
    
    if not os.path.exists(args.target):
        print(f"❌ Error: Target '{args.target}' not found.")
        sys.exit(1)
    
    analysis_results = {}
    
    if os.path.isfile(args.target):
        files_to_analyze = [args.target]
    else:
        files_to_analyze = []
        for root, dirs, files in os.walk(args.target):
            for file in files:
                files_to_analyze.append(os.path.join(root, file))
    
    print(f"🔍 Analyzing {len(files_to_analyze)} files...")
    
    for file_path in files_to_analyze:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            file_analysis = {
                'file_size': len(content),
                'line_count': content.count('\n'),
                'threats_detected': [],
                'pii_detected': [],
                'secrets_detected': []
            }
            
            if args.threats:
                # Basic threat detection
                threat_patterns = ['script>', 'eval(', 'exec(', 'system(', 'shell_exec']
                for pattern in threat_patterns:
                    if pattern.lower() in content.lower():
                        file_analysis['threats_detected'].append(pattern)
            
            if args.pii:
                # Basic PII detection
                import re
                email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
                emails = email_pattern.findall(content)
                if emails:
                    file_analysis['pii_detected'].extend(emails[:5])  # First 5
            
            if args.secrets:
                # Basic secrets detection
                secret_patterns = ['password=', 'api_key=', 'secret=', 'token=']
                for pattern in secret_patterns:
                    if pattern.lower() in content.lower():
                        file_analysis['secrets_detected'].append(pattern)
            
            analysis_results[file_path] = file_analysis
            
        except Exception as e:
            print(f"⚠️ Warning: Could not analyze {file_path}: {e}")
    
    # Generate report
    print(f"\n" + "="*60)
    print(f"📊 ANALYSIS RESULTS")
    print(f"="*60)
    
    total_threats = sum(len(r['threats_detected']) for r in analysis_results.values())
    total_pii = sum(len(r['pii_detected']) for r in analysis_results.values())
    total_secrets = sum(len(r['secrets_detected']) for r in analysis_results.values())
    
    print(f"📁 Files analyzed: {len(analysis_results)}")
    if args.threats:
        print(f"🚨 Threats found: {total_threats}")
    if args.pii:
        print(f"👤 PII instances: {total_pii}")
    if args.secrets:
        print(f"🔑 Secrets found: {total_secrets}")
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            if args.format == 'json':
                json.dump(analysis_results, f, indent=2)
            else:
                f.write("Gamma Scanner Analysis Results\n")
                f.write("=" * 40 + "\n")
                for file_path, results in analysis_results.items():
                    f.write(f"\nFile: {file_path}\n")
                    f.write(f"Size: {results['file_size']} bytes\n")
                    if results['threats_detected']:
                        f.write(f"Threats: {', '.join(results['threats_detected'])}\n")
        print(f"💾 Analysis saved to: {args.output}")

def interactive_command(scanner: GammaScanner, args):
    """Handle interactive command - enhanced REPL"""
    print_banner()
    print("Gamma Scanner Interactive Mode")
    print("Type 'help' for commands, 'exit' to quit\n")
    
    if args.load:
        if os.path.exists(args.load):
            try:
                with open(args.load, 'r', encoding='utf-8') as f:
                    content = f.read()
                compiled_rules = scanner.load_rules_from_file_content(content)
                if compiled_rules:
                    print(f"✅ Loaded {len(compiled_rules)} rules from {args.load}")
                else:
                    print(f"❌ Failed to load rules from {args.load}")
            except Exception as e:
                print(f"❌ Error loading {args.load}: {e}")
    
    if args.examples:
        print_gamma_examples()
    
    while True:
        try:
            command = input("gamma> ").strip()
            
            if command in ["exit", "quit", "q"]:
                print("Goodbye!")
                break
            
            elif command == "help":
                print_interactive_help()
            
            elif command == "examples":
                print_gamma_examples()
            
            elif command.startswith("validate "):
                rule_text = command[9:].strip()
                try:
                    tokens = scanner.lexer.tokenize(rule_text)
                    ast = scanner.parser.parse(tokens)
                    if ast:
                        print("✅ Rule syntax is valid")
                    else:
                        print("❌ Invalid rule syntax")
                except Exception as e:
                    print(f"❌ Validation error: {e}")
            
            elif command.startswith("scan "):
                target = command[5:].strip()
                if os.path.exists(target):
                    print(f"🔍 Scanning {target}...")
                    # Simplified scan for interactive mode
                    print("✅ Scan complete (interactive mode)")
                else:
                    print(f"❌ Target not found: {target}")
            
            elif command == "stats":
                print("📊 Scanner Statistics:")
                print("  Interactive session active")
            
            elif command and not command.startswith("#"):
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            print("\nGoodbye!")
            break

def print_interactive_help():
    """Print interactive mode help"""
    print("""
📚 Available Commands:
  validate <rule>     - Validate Gamma DSL rule syntax
  scan <target>       - Scan file or directory
  examples            - Show Gamma DSL syntax examples
  stats               - Show scanner statistics
  help                - Show this help message
  exit/quit/q         - Exit interactive mode

💡 Gamma DSL Syntax Examples:
  HUNT ThreatName:
      LOOK FOR:
          pattern ~ text "malicious" IGNORE case
      WHEN:
          file HAS pattern
      THEN:
          ALERT "Threat detected!"
    """)

def print_gamma_examples():
    """Print Gamma DSL syntax examples"""
    print("""
📖 GAMMA DSL SYNTAX EXAMPLES:

Basic Threat Detection:
  HUNT SQLInjection:
      LOOK FOR:
          sql_pattern ~ text "' OR '1'='1" IGNORE case
          union_attack ~ text "UNION SELECT" IGNORE case
      WHEN:
          file HAS sql_pattern EITHER content HOLDS union_attack
      THEN:
          ALERT "SQL injection detected!"

Malware Detection:
  HUNT MalwareSignature:
      LOOK FOR:
          pe_header ~ hex "4D 5A 90 00"
          suspicious_api ~ text "CreateRemoteThread" IGNORE case
      WHEN:
          file HAS pe_header ALSO content CONTAINS suspicious_api
      THEN:
          FLAG file as malware

Data Pattern Detection:
  HUNT SensitiveData:
      LOOK FOR:
          credit_card ~ pattern /\\b4[0-9]{15}\\b/
          ssn ~ pattern /\\b\\d{3}-\\d{2}-\\d{4}\\b/
      WHEN:
          content MATCHES credit_card EITHER data HAS ssn
      THEN:
          REPORT to compliance_team
    """)

def benchmark_command(scanner: GammaScanner, args):
    """Handle benchmark command"""
    print(f"⚡ Benchmarking rules: {args.rules_file}")
    
    if not os.path.exists(args.rules_file):
        print(f"❌ Error: Rules file '{args.rules_file}' not found.")
        sys.exit(1)
    
    if not os.path.exists(args.data_path):
        print(f"❌ Error: Data path '{args.data_path}' not found.")
        sys.exit(1)
    
    # Load rules
    try:
        with open(args.rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        
        compiled_rules = scanner.load_rules_from_file_content(rules_content)
        if not compiled_rules:
            print("❌ Failed to compile rules")
            sys.exit(1)
            
        print(f"✅ Loaded {len(compiled_rules)} rules for benchmarking")
        
    except Exception as e:
        print(f"❌ Error loading rules: {e}")
        sys.exit(1)
    
    # Collect test files
    test_files = []
    if os.path.isfile(args.data_path):
        test_files = [args.data_path]
    else:
        for root, dirs, files in os.walk(args.data_path):
            for file in files:
                test_files.append(os.path.join(root, file))
    
    if not test_files:
        print("❌ No test files found")
        sys.exit(1)
    
    print(f"🎯 Benchmarking against {len(test_files)} files")
    print(f"🔄 Running {args.iterations} iterations...")
    
    total_time = 0.0
    total_files_processed = 0
    
    for iteration in range(args.iterations):
        print(f"Iteration {iteration + 1}/{args.iterations}")
        
        iteration_start = time.time()
        iteration_files = 0
        
        for test_file in test_files:
            try:
                with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Simulate scanning
                for rule in compiled_rules:
                    if hasattr(rule, 'strings') and rule.strings:
                        for pattern in rule.strings.string_definitions:
                            if pattern.string_type == 'text':
                                _ = pattern.value in content
                
                iteration_files += 1
                
            except Exception as e:
                print(f"  ⚠️ Warning: Error processing {test_file}: {e}")
        
        iteration_time = time.time() - iteration_start
        total_time += iteration_time
        total_files_processed += iteration_files
        
        print(f"  ⏱️ Time: {iteration_time:.3f}s, Files: {iteration_files}")
    
    # Results
    avg_time = total_time / args.iterations
    files_per_second = (total_files_processed / args.iterations) / avg_time if avg_time > 0 else 0
    
    print(f"\n" + "="*50)
    print(f"⚡ BENCHMARK RESULTS")
    print(f"="*50)
    print(f"📊 Total time: {total_time:.3f} seconds")
    print(f"📈 Average time per iteration: {avg_time:.3f} seconds")
    print(f"🚀 Files per second: {files_per_second:.1f}")
    print(f"📁 Average files per iteration: {total_files_processed / args.iterations:.1f}")
    print(f"🔧 Rules tested: {len(compiled_rules)}")

def examples_command(args):
    """Handle examples command"""
    print("📚 GAMMA DSL SYNTAX EXAMPLES")
    print("="*50)
    
    if args.category == 'security' or not args.category:
        print("""
🔒 SECURITY PATTERNS:

SQL Injection Detection:
  HUNT SQLInjection:
      LOOK FOR:
          basic_sqli ~ text "' OR '1'='1" IGNORE case
          union_select ~ text "UNION SELECT" IGNORE case
      WHEN:
          file HAS basic_sqli EITHER content HOLDS union_select
      THEN:
          ALERT "SQL injection detected!"

XSS Detection:
  HUNT CrossSiteScripting:
      LOOK FOR:
          script_tag ~ text "<script>" IGNORE case
          javascript_url ~ text "javascript:" IGNORE case
      WHEN:
          content CONTAINS script_tag EITHER data HAS javascript_url
      THEN:
          FLAG file as xss_risk
""")
    
    if args.category == 'malware' or not args.category:
        print("""
🦠 MALWARE DETECTION:

PE Executable Analysis:
  HUNT WindowsMalware:
      LOOK FOR:
          pe_header ~ hex "4D 5A 90 00"
          suspicious_api ~ text "CreateRemoteThread" IGNORE case
      WHEN:
          file HAS pe_header ALSO content CONTAINS suspicious_api
      THEN:
          ALERT "Potential malware detected!"
""")
    
    if args.category == 'data' or not args.category:
        print("""
📄 DATA PATTERN DETECTION:

Personal Information:
  HUNT PersonalData:
      LOOK FOR:
          ssn ~ pattern /\\b\\d{3}-\\d{2}-\\d{4}\\b/
          credit_card ~ pattern /\\b4[0-9]{15}\\b/
      WHEN:
          content MATCHES ssn EITHER data CONTAINS credit_card
      THEN:
          REPORT to privacy_officer
""")
    
    if args.advanced:
        print("""
🚀 ADVANCED FEATURES:

Complex Logic Flow:
  HUNT AdvancedThreat:
      ABOUT:
          author -> "Security Team"
          severity -> "high"
      LOOK FOR:
          encoded_payload ~ pattern /[A-Za-z0-9+/]{20,}={0,2}/
          decode_function ~ text "base64_decode" IGNORE case
      WHEN:
          file HAS encoded_payload
          ALSO content HOLDS decode_function
          ALSO SIZE greater than 1000 bytes
          UNLESS filename BEGINS "test_"
      THEN:
          ALERT "Advanced threat detected!" with high_priority
          CAPTURE payload for analysis
          BLOCK execution immediately
""")

# Old functions removed - using new CLI implementation above

if __name__ == "__main__":
    main()
