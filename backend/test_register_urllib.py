#!/usr/bin/env python3
"""Test the /register endpoint using standard library urllib."""

import urllib.request
import urllib.parse
import json
import sys

payload = {
    "username": "bob",
    "email": "bob@example.com",
    "password": "testpass123"
}

print(f"Testing POST /register\nPayload: {json.dumps(payload)}\n")

try:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        "http://127.0.0.1:8000/register",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=5) as response:
        status_code = response.status
        response_data = json.loads(response.read().decode('utf-8'))
        print(f"✓ Status Code: {status_code}")
        print(f"✓ Response: {json.dumps(response_data, indent=2)}\n")
        print("✓ SUCCESS: /register endpoint works! Password hashing fixed.")
        
except urllib.error.HTTPError as e:
    print(f"✗ HTTP Error {e.code}: {e.reason}")
    try:
        error_body = json.loads(e.read().decode('utf-8'))
        print(f"✗ Response: {json.dumps(error_body, indent=2)}")
    except:
        pass
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
