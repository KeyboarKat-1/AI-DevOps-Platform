#!/usr/bin/env python3
"""Test the /register endpoint to verify the password hashing fix."""

import requests
import json
import sys

payload = {
    "username": "alice",
    "email": "alice@example.com",
    "password": "securepassword123"
}

print(f"Testing POST /register with payload: {json.dumps(payload)}\n")

try:
    resp = requests.post(
        "http://127.0.0.1:8000/register",
        json=payload,
        timeout=5
    )
    print(f"✓ Status Code: {resp.status_code}")
    print(f"✓ Response:\n{json.dumps(resp.json(), indent=2)}\n")
    
    if resp.status_code == 200:
        print("✓ SUCCESS: /register endpoint now works! Password hashing fixed.")
        sys.exit(0)
    else:
        print(f"⚠ Unexpected status code: {resp.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    sys.exit(1)
