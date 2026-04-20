"""
core/security_guidance.py — Official-Inspired Security Hooks
Inspired by Anthropic's security_reminder_hook.py (ddworken)
"""
import re
import os
from typing import List, Dict

# Dangerous patterns based on official security guidance
DANGEROUS_PATTERNS = {
    "python": [
        r"eval\(",
        r"exec\(",
        r"pickle\.loads\(",
        r"pickle\.load\(",
        r"subprocess\.run\(.*shell=True",
        r"os\.system\(",
        r"yaml\.load\(.*Loader=", # Insecure YAML loading
    ],
    "javascript": [
        r"eval\(",
        r"new Function\(",
        r"child_process\.exec\(",
        r"innerHTML\s*=", # Potential XSS
    ]
}

def scan_patterns(content: str, language: str = "python") -> List[Dict]:
    """
    Scans for prohibited security patterns in the provided content.
    """
    findings = []
    patterns = DANGEROUS_PATTERNS.get(language, DANGEROUS_PATTERNS["python"])
    
    lines = content.splitlines()
    for i, line in enumerate(lines):
        for pattern in patterns:
            if re.search(pattern, line):
                findings.append({
                    "line": i + 1,
                    "content": line.strip(),
                    "pattern": pattern,
                    "severity": "HIGH",
                    "reminder": f"Potentially unsafe pattern detected: {pattern}. Consider safer alternatives."
                })
    return findings

def get_security_reminder_prompt(findings: List[Dict]) -> str:
    """
    Generates a security guidance prompt based on detected patterns.
    """
    reminders = "\n".join([f"- Line {f['line']}: {f['reminder']}" for f in findings])
    return f"""
SECURITY GUIDANCE REQUIRED:
The system has detected potentially unsafe code patterns in the current target.
Detected Issues:
{reminders}

Please analyze these patterns and provide a recommendation for refactoring them into secure implementations.
"""
