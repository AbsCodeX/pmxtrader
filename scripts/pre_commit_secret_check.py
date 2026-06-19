#!/usr/bin/env python3
"""
Pre-commit secret scanner for pmxtrader
"""

import re
import subprocess
import sys
from pathlib import Path

SECRET_PATTERNS = [
    r'AKIA[0-9A-Z]{16}',
    r'AIza[0-9A-Za-z\-_]{35}',
    r'sk-[a-zA-Z0-9]{48}',
    r'xox[baprs]-[0-9a-zA-Z]{10,48}',
    r'ghp_[a-zA-Z0-9]{36}',
    r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----',
]

IGNORE_DIRS = ['node_modules', '.git', 'dist', 'build']

def get_staged_files():
    result = subprocess.run(['git', 'diff', '--cached', '--name-only'], capture_output=True, text=True)
    return [f for f in result.stdout.strip().split('\n') if f] if result.stdout.strip() else []

def should_ignore(filepath):
    path = Path(filepath)
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
    return False

def scan_file(filepath):
    if should_ignore(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except:
        return []
    
    issues = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('//'):
            continue
        if 'SECRET_PATTERNS' in line or 'example' in stripped.lower():
            continue
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, line):
                issues.append(i)
    return issues

def main():
    blocked = False
    for file in get_staged_files():
        if not file:
            continue
        issues = scan_file(file)
        if issues:
            print(f"Potential secret in: {file}")
            blocked = True
    if blocked:
        print("Commit blocked.")
        sys.exit(1)
    print("No secrets detected.")
    sys.exit(0)

if __name__ == "__main__":
    main()
