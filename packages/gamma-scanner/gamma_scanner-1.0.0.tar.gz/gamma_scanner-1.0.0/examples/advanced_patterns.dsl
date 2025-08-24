# StringForge DSL Advanced Pattern Examples
# These rules demonstrate advanced pattern matching and analysis

# Advanced malware detection rule
rule detect_malware_patterns {
    regex_match("(eval|exec|system|shell_exec|passthru)\\s*\\(") and
    (contains("base64_decode") or contains("gzinflate") or contains("str_rot13")) and
    entropy > 4.5
}

# Detect obfuscated JavaScript
rule detect_obfuscated_js {
    contains("javascript") and
    (count("\\x", text) > 10 or count("\\u", text) > 10) and
    length > 500
}

# Advanced SQL injection detection
rule detect_advanced_sqli {
    regex_match("(UNION|SELECT|INSERT|UPDATE|DELETE|DROP).*?(\\-\\-|\\/\\*|#)") or
    regex_match("'\\s*(OR|AND)\\s+['\"]?\\w+['\"]?\\s*[=<>]\\s*['\"]?\\w+['\"]?") or
    regex_match("\\bhex\\(|\\bchar\\(|\\bascii\\(|\\bord\\(|\\bsubstring\\(")
}

# Detect potential data exfiltration
rule detect_data_exfiltration {
    (contains("curl") or contains("wget") or contains("POST") or contains("PUT")) and
    (find_emails.matched or find_credit_cards.matched or find_ip_addresses.matched) and
    length > 100
}

# Detect encoded payloads
rule detect_encoded_payloads {
    regex_match("(powershell|cmd|bash).*?(-e|-enc|-encoded)") or
    (contains("frombase64") and contains("invoke")) or
    regex_match("\\$\\w+\\s*=\\s*\\[.*?\\]\\s*\\(.*?\\)")
}

# Advanced log analysis for intrusion detection
rule detect_intrusion_attempts {
    regex_match("(\\b(admin|root|administrator)\\b.*?(login|auth|password))") and
    (count("failed", text) > 3 or count("error", text) > 3 or count("invalid", text) > 3)
}

# Detect suspicious network traffic patterns
rule detect_suspicious_network {
    regex_match("\\b(?:GET|POST|PUT|DELETE)\\s+.*?(?:\\.\\.|\\/\\/|%2e%2e)") or
    regex_match("User-Agent:.*?(bot|crawler|spider|scan)") or
    contains("X-Forwarded-For") and count(".", text) > 20
}

# Advanced crypto-mining detection
rule detect_crypto_mining {
    contains("stratum") or contains("mining") or contains("hashrate") or
    regex_match("\\b[a-fA-F0-9]{64}\\b") and contains("pool") or
    regex_match("(monero|bitcoin|ethereum|litecoin).*?(mine|mining|miner)")
}

# Detect configuration disclosure
rule detect_config_disclosure {
    regex_match("(password|secret|key|token)\\s*[=:]\\s*['\"]?[^\\s'\"]{8,}") and
    not contains("*****") and not contains("xxxx")
}

# Advanced phishing detection
rule detect_phishing {
    (contains("verify your account") or contains("suspend") or contains("urgent")) and
    (contains("click here") or contains("login") or contains("update")) and
    (find_urls.matched and not regex_match("https://[^/]*\\.(gov|edu|org)"))
}

# Detect steganography indicators
rule detect_steganography {
    (ends_with(".jpg") or ends_with(".png") or ends_with(".gif")) and
    (contains("LSB") or contains("steghide") or contains("hidden") or contains("embedded")) or
    (regex_match("\\b[A-Za-z0-9+/]{100,}={0,2}\\b") and entropy > 5.0)
}

# Advanced log tampering detection
rule detect_log_tampering {
    regex_match("\\b\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2}\\b") and
    (count("deleted", text) > 0 or count("modified", text) > 0 or count("cleared", text) > 0) and
    regex_match("(rm|del|unlink|truncate).*?log")
}
