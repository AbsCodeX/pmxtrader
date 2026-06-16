#!/usr/bin/env python3
"""
Pre-commit secret scanner for pmxtrader
Scans staged files for common secret patterns before allowing commit.
"""

import re
import subprocess
import sys
from pathlib import Path

# Patterns that often indicate secrets
SECRET_PATTERNS = [
    r'AKIA[0-9A-Z]{16}',                    # AWS Access Key
    r'AIza[0-9A-Za-z\-_]{35}',              # Google API Key
    r'sk-[a-zA-Z0-9]{48}',                  # OpenAI API Key
    r'xox[baprs]-[0-9a-zA-Z]{10,48}',       # Slack Token
    r'ghp_[a-zA-Z0-9]{36}',                 # GitHub Personal Access Token
    r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----',
    r'private_key|privateKey|PRIVATE_KEY',
    r'api_key|apiKey|API_KEY',
    r'secret_key|secretKey|SECRET_KEY',
    r'password\s*=\s*["\'][^"\']+["\']',
    r'\.env',
]

def get_staged_files():
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True, text=True
    )
    return result.stdout.strip().split('\n') if result.stdout.strip() else []

def scan_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return []

    issues = []
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(pattern)
    return issues

def main():
    staged_files = get_staged_files()
    blocked = False

    for file in staged_files:
        if not file or not Path(file).exists():
            continue
        issues = scan_file(file)
        if issues:
            print(f"🚨 Potential secret detected in: {file}")
            blocked = True

    if blocked:
        print("\nCommit blocked. Remove secrets before committing.")
        sys.exit(1)
    else:
        print("✅ No secrets detected. Proceeding with commit.")
        sys.exit(0)

if __name__ == "__main__":
    main()
