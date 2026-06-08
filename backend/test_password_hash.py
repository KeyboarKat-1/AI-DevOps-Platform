#!/usr/bin/env python3
"""Test password hashing directly to debug the issue."""

import sys
sys.path.insert(0, 'c:\\Users\\vatal\\New folder (2)\\AI-DevOps-Platform\\backend')

from app.services.auth import get_password_hash, verify_password

test_passwords = [
    "shortpass",
    "this is a longer password with more characters",
    "this is a very long password that is way over 72 bytes which is the bcrypt limit for passwords so lets test this one too"
]

print("Testing password hashing with truncation:\n")

for pwd in test_passwords:
    print(f"Original password ({len(pwd)} bytes): {pwd[:30]}...")
    try:
        hashed = get_password_hash(pwd)
        print(f"✓ Hashed successfully: {hashed[:50]}...")
        
        verified = verify_password(pwd, hashed)
        print(f"✓ Verification: {verified}")
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
    print()
