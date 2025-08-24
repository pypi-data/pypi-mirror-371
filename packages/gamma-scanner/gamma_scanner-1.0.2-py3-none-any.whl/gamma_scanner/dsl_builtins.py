"""
StringForge DSL Built-in Functions
Comprehensive string manipulation and analysis functions
"""

import re
import hashlib
import base64
import math
import difflib
import binascii
import urllib.parse
import html
import codecs
from typing import Any, List, Dict, Optional, Union
from collections import Counter

class StringForgeBuiltins:
    """Built-in functions for StringForge DSL"""
    
    def __init__(self):
        self.compiled_regex_cache = {}
    
    # Basic string operations
    def length(self, text: str) -> int:
        """Get length of string"""
        return len(str(text))
    
    def count(self, pattern: str, text: str, overlapping: bool = False) -> int:
        """Count occurrences of pattern in text"""
        text = str(text)
        pattern = str(pattern)
        
        if not overlapping:
            return text.count(pattern)
        else:
            # Count overlapping occurrences
            count = 0
            start = 0
            while True:
                pos = text.find(pattern, start)
                if pos == -1:
                    break
                count += 1
                start = pos + 1
            return count
    
    def split(self, delimiter: str, text: str, max_splits: int = -1) -> List[str]:
        """Split string by delimiter"""
        return str(text).split(str(delimiter), max_splits)
    
    def join(self, delimiter: str, array: List[str]) -> str:
        """Join array elements with delimiter"""
        return str(delimiter).join(str(item) for item in array)
    
    def upper(self, text: str) -> str:
        """Convert to uppercase"""
        return str(text).upper()
    
    def lower(self, text: str) -> str:
        """Convert to lowercase"""
        return str(text).lower()
    
    def strip(self, text: str, chars: Optional[str] = None) -> str:
        """Strip whitespace or specified characters"""
        return str(text).strip(chars)
    
    def trim(self, text: str) -> str:
        """Alias for strip"""
        return self.strip(text)
    
    def capitalize(self, text: str) -> str:
        """Capitalize first letter"""
        return str(text).capitalize()
    
    def title(self, text: str) -> str:
        """Convert to title case"""
        return str(text).title()
    
    def swapcase(self, text: str) -> str:
        """Swap case of all characters"""
        return str(text).swapcase()
    
    # Advanced string operations
    def replace(self, pattern: str, replacement: str, text: str, count: int = -1) -> str:
        """Replace pattern with replacement in text"""
        return str(text).replace(str(pattern), str(replacement), count)
    
    def extract(self, pattern: str, text: str, group: int = 0) -> str:
        """Extract text using regex pattern"""
        text = str(text)
        pattern = str(pattern)
        
        compiled_regex = self._get_compiled_regex(pattern)
        match = compiled_regex.search(text)
        
        if match:
            return match.group(group)
        return ""
    
    def substring(self, text: str, start: int, end: Optional[int] = None) -> str:
        """Extract substring"""
        text = str(text)
        if end is None:
            return text[start:]
        return text[start:end]
    
    def reverse(self, text: str) -> str:
        """Reverse string"""
        return str(text)[::-1]
    
    # Regular expression functions
    def regex_compile(self, pattern: str, flags: str = "") -> Any:
        """Compile regex pattern with flags"""
        flag_value = 0
        if 'i' in flags: flag_value |= re.IGNORECASE
        if 'm' in flags: flag_value |= re.MULTILINE
        if 's' in flags: flag_value |= re.DOTALL
        if 'x' in flags: flag_value |= re.VERBOSE
        
        return re.compile(pattern, flag_value)
    
    def regex_match(self, pattern: str, text: str, flags: str = "") -> bool:
        """Check if regex pattern matches text"""
        compiled_regex = self._get_compiled_regex(pattern, flags)
        return bool(compiled_regex.search(str(text)))
    
    def regex_findall(self, pattern: str, text: str, flags: str = "") -> List[str]:
        """Find all matches of regex pattern in text"""
        compiled_regex = self._get_compiled_regex(pattern, flags)
        return compiled_regex.findall(str(text))
    
    def _get_compiled_regex(self, pattern: str, flags: str = "") -> re.Pattern:
        """Get compiled regex from cache or compile new one"""
        cache_key = f"{pattern}:{flags}"
        
        if cache_key not in self.compiled_regex_cache:
            flag_value = 0
            if 'i' in flags: flag_value |= re.IGNORECASE
            if 'm' in flags: flag_value |= re.MULTILINE
            if 's' in flags: flag_value |= re.DOTALL
            if 'x' in flags: flag_value |= re.VERBOSE
            
            self.compiled_regex_cache[cache_key] = re.compile(pattern, flag_value)
        
        return self.compiled_regex_cache[cache_key]
    
    # String testing functions
    def contains(self, substring: str, text: str) -> bool:
        """Check if text contains substring"""
        return str(substring) in str(text)
    
    def starts_with(self, prefix: str, text: str) -> bool:
        """Check if text starts with prefix"""
        return str(text).startswith(str(prefix))
    
    def ends_with(self, suffix: str, text: str) -> bool:
        """Check if text ends with suffix"""
        return str(text).endswith(str(suffix))
    
    def is_alpha(self, text: str) -> bool:
        """Check if text contains only alphabetic characters"""
        return str(text).isalpha()
    
    def is_numeric(self, text: str) -> bool:
        """Check if text contains only numeric characters"""
        return str(text).isnumeric()
    
    def is_alphanumeric(self, text: str) -> bool:
        """Check if text contains only alphanumeric characters"""
        return str(text).isalnum()
    
    def is_upper(self, text: str) -> bool:
        """Check if text is uppercase"""
        return str(text).isupper()
    
    def is_lower(self, text: str) -> bool:
        """Check if text is lowercase"""
        return str(text).islower()
    
    def is_space(self, text: str) -> bool:
        """Check if text contains only whitespace"""
        return str(text).isspace()
    
    # Encoding/decoding functions
    def encode(self, text: str, encoding: str = "utf-8") -> bytes:
        """Encode string to bytes"""
        return str(text).encode(encoding)
    
    def decode(self, data: bytes, encoding: str = "utf-8") -> str:
        """Decode bytes to string"""
        return data.decode(encoding)
    
    def base64_encode(self, text: str) -> str:
        """Encode string as base64"""
        return base64.b64encode(str(text).encode()).decode()
    
    def base64_decode(self, data: str) -> str:
        """Decode base64 string"""
        return base64.b64decode(data).decode()
    
    def url_encode(self, text: str) -> str:
        """URL encode string"""
        import urllib.parse
        return urllib.parse.quote(str(text))
    
    def url_decode(self, text: str) -> str:
        """URL decode string"""
        import urllib.parse
        return urllib.parse.unquote(str(text))
    
    # Hashing functions
    def hash_string(self, text: str, algorithm: str = "sha256") -> str:
        """Hash string using specified algorithm"""
        text = str(text).encode()
        
        if algorithm == "md5":
            return hashlib.md5(text).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(text).hexdigest()
        elif algorithm == "sha256":
            return hashlib.sha256(text).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(text).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    # Advanced analysis functions
    def entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        text = str(text)
        if not text:
            return 0.0
        
        # Count character frequencies
        char_counts = Counter(text)
        total_chars = len(text)
        
        # Calculate entropy
        entropy = 0.0
        for count in char_counts.values():
            prob = count / total_chars
            entropy -= prob * math.log2(prob)
        
        return entropy
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings (0-1)"""
        text1, text2 = str(text1), str(text2)
        return difflib.SequenceMatcher(None, text1, text2).ratio()
    
    def distance(self, text1: str, text2: str, algorithm: str = "levenshtein") -> int:
        """Calculate edit distance between strings"""
        text1, text2 = str(text1), str(text2)
        
        if algorithm == "levenshtein":
            return self._levenshtein_distance(text1, text2)
        elif algorithm == "hamming":
            return self._hamming_distance(text1, text2)
        else:
            raise ValueError(f"Unsupported distance algorithm: {algorithm}")
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _hamming_distance(self, s1: str, s2: str) -> int:
        """Calculate Hamming distance (strings must be same length)"""
        if len(s1) != len(s2):
            raise ValueError("Strings must be same length for Hamming distance")
        
        return sum(c1 != c2 for c1, c2 in zip(s1, s2))
    
    # Pattern analysis
    def find_patterns(self, text: str, min_length: int = 3, min_occurrences: int = 2) -> List[Dict[str, Any]]:
        """Find repeated patterns in text"""
        text = str(text)
        patterns = {}
        
        # Find all substrings of minimum length
        for i in range(len(text) - min_length + 1):
            for j in range(i + min_length, len(text) + 1):
                pattern = text[i:j]
                if pattern not in patterns:
                    patterns[pattern] = []
                patterns[pattern].append(i)
        
        # Filter patterns by minimum occurrences
        result = []
        for pattern, positions in patterns.items():
            if len(positions) >= min_occurrences:
                result.append({
                    'pattern': pattern,
                    'length': len(pattern),
                    'occurrences': len(positions),
                    'positions': positions
                })
        
        # Sort by occurrences (descending)
        result.sort(key=lambda x: x['occurrences'], reverse=True)
        return result
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, str(text))
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+'
        return re.findall(url_pattern, str(text))
    
    def extract_ips(self, text: str) -> List[str]:
        """Extract IP addresses from text"""
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        return re.findall(ip_pattern, str(text))
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        matches = re.findall(phone_pattern, str(text))
        return [''.join(match) for match in matches]
    
    # String formatting and cleaning
    def remove_duplicates(self, text: str, preserve_order: bool = True) -> str:
        """Remove duplicate characters"""
        text = str(text)
        if preserve_order:
            seen = set()
            result = []
            for char in text:
                if char not in seen:
                    seen.add(char)
                    result.append(char)
            return ''.join(result)
        else:
            return ''.join(set(text))
    
    def remove_whitespace(self, text: str, all_whitespace: bool = False) -> str:
        """Remove whitespace from string"""
        text = str(text)
        if all_whitespace:
            return re.sub(r'\s+', '', text)
        else:
            return ' '.join(text.split())
    
    def pad_left(self, text: str, width: int, fill_char: str = ' ') -> str:
        """Pad string on the left"""
        return str(text).rjust(width, str(fill_char))
    
    def pad_right(self, text: str, width: int, fill_char: str = ' ') -> str:
        """Pad string on the right"""
        return str(text).ljust(width, str(fill_char))
    
    def pad_center(self, text: str, width: int, fill_char: str = ' ') -> str:
        """Pad string in the center"""
        return str(text).center(width, str(fill_char))
    
    def truncate(self, text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate string to maximum length"""
        text = str(text)
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    # Advanced encoding detection and decoding
    def detect_encodings(self, text: str) -> List[Dict[str, Any]]:
        """Detect possible encodings in text and return decoded variants"""
        text = str(text)
        detected = []
        
        # Base64 detection and decoding
        if self._is_base64(text):
            try:
                decoded = base64.b64decode(text).decode('utf-8', errors='ignore')
                if decoded.strip():
                    detected.append({'type': 'base64', 'decoded': decoded, 'confidence': 0.9})
            except:
                pass
        
        # Hex detection and decoding
        if self._is_hex(text):
            try:
                clean_hex = re.sub(r'[^0-9a-fA-F]', '', text)
                if len(clean_hex) % 2 == 0:
                    decoded = bytes.fromhex(clean_hex).decode('utf-8', errors='ignore')
                    if decoded.strip():
                        detected.append({'type': 'hex', 'decoded': decoded, 'confidence': 0.8})
            except:
                pass
        
        # URL encoding detection
        if '%' in text:
            try:
                decoded = urllib.parse.unquote(text)
                if decoded != text:
                    detected.append({'type': 'url', 'decoded': decoded, 'confidence': 0.8})
            except:
                pass
        
        # Unicode escape sequences
        if '\\u' in text:
            try:
                decoded = text.encode().decode('unicode_escape')
                if decoded != text:
                    detected.append({'type': 'unicode', 'decoded': decoded, 'confidence': 0.9})
            except:
                pass
        
        # HTML entities
        if '&#' in text or '&' in text:
            try:
                decoded = html.unescape(text)
                if decoded != text:
                    detected.append({'type': 'html', 'decoded': decoded, 'confidence': 0.8})
            except:
                pass
        
        # ROT13
        if text.isalpha():
            try:
                decoded = codecs.decode(text, 'rot13')
                if decoded != text:
                    detected.append({'type': 'rot13', 'decoded': decoded, 'confidence': 0.6})
            except:
                pass
        
        # Binary detection
        if self._is_binary(text):
            try:
                binary_str = text.replace(' ', '').replace('\n', '').replace('\t', '')
                if len(binary_str) % 8 == 0:
                    decoded = ''.join(chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8))
                    if all(32 <= ord(c) <= 126 or c in '\n\r\t' for c in decoded):
                        detected.append({'type': 'binary', 'decoded': decoded, 'confidence': 0.9})
            except:
                pass
        
        # Octal detection
        if self._is_octal(text):
            try:
                parts = re.findall(r'\\?([0-7]{3})', text)
                if parts:
                    decoded = ''.join(chr(int(p, 8)) for p in parts)
                    if decoded.strip():
                        detected.append({'type': 'octal', 'decoded': decoded, 'confidence': 0.7})
            except:
                pass
        
        # ASCII decimal encoding
        if self._is_ascii_decimal(text):
            try:
                numbers = re.findall(r'\b([0-9]{2,3})\b', text)
                if numbers:
                    decoded = ''.join(chr(int(n)) for n in numbers if 32 <= int(n) <= 126)
                    if decoded.strip():
                        detected.append({'type': 'ascii_decimal', 'decoded': decoded, 'confidence': 0.6})
            except:
                pass
        
        return detected
    
    def decode_all(self, text: str) -> str:
        """Try to decode text using all supported encodings, return best result"""
        text = str(text)
        detected = self.detect_encodings(text)
        
        if detected:
            # Return the highest confidence result
            best = max(detected, key=lambda x: x['confidence'])
            return best['decoded']
        
        return text
    
    def _is_base64(self, text: str) -> bool:
        """Check if text might be Base64"""
        text = text.strip().replace('\n', '').replace(' ', '')
        if len(text) < 4 or len(text) % 4 != 0:
            return False
        return bool(re.match(r'^[A-Za-z0-9+/]*={0,2}$', text))
    
    def _is_hex(self, text: str) -> bool:
        """Check if text might be hex encoded"""
        clean = re.sub(r'[^0-9a-fA-F]', '', text)
        return len(clean) >= 8 and len(clean) % 2 == 0 and len(clean) / len(text) > 0.6
    
    def _is_binary(self, text: str) -> bool:
        """Check if text might be binary"""
        clean = re.sub(r'[^01]', '', text)
        return len(clean) >= 16 and len(clean) % 8 == 0 and len(clean) / len(text) > 0.8
    
    def _is_octal(self, text: str) -> bool:
        """Check if text contains octal escape sequences"""
        return bool(re.search(r'\\?[0-7]{3}', text)) and len(re.findall(r'[0-7]', text)) > len(text) * 0.3
    
    def _is_ascii_decimal(self, text: str) -> bool:
        """Check if text might be ASCII decimal encoded"""
        numbers = re.findall(r'\b([0-9]{2,3})\b', text)
        valid_ascii = sum(1 for n in numbers if 32 <= int(n) <= 126)
        return len(numbers) >= 3 and valid_ascii / len(numbers) > 0.7
    
    def auto_decode_and_analyze(self, text: str) -> Dict[str, Any]:
        """Automatically decode text and analyze all variants"""
        text = str(text)
        results = {
            'original': text,
            'decoded_variants': [],
            'all_content': [text]  # Include original
        }
        
        # Get all decoded variants
        decoded_variants = self.detect_encodings(text)
        results['decoded_variants'] = decoded_variants
        
        # Add all decoded content for analysis
        for variant in decoded_variants:
            results['all_content'].append(variant['decoded'])
            # Try recursive decoding (encoded inside encoded)
            recursive = self.detect_encodings(variant['decoded'])
            for rec in recursive:
                if rec['decoded'] not in results['all_content']:
                    results['all_content'].append(rec['decoded'])
                    results['decoded_variants'].append({
                        'type': f"{variant['type']}_nested_{rec['type']}",
                        'decoded': rec['decoded'],
                        'confidence': variant['confidence'] * rec['confidence']
                    })
        
        return results
