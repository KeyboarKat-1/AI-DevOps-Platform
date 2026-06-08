#!/usr/bin/env python3
"""Test the /db/health endpoint to check if DB is accessible."""

import urllib.request
import json

print("Testing GET /db/health...\n")

try:
    req = urllib.request.Request(
        "http://127.0.0.1:8000/db/health",
        method="GET"
    )
    
    with urllib.request.urlopen(req, timeout=5) as response:
        status_code = response.status
        response_data = json.loads(response.read().decode('utf-8'))
        print(f"✓ Status Code: {status_code}")
        print(f"✓ Response: {json.dumps(response_data, indent=2)}\n")
        
except urllib.error.HTTPError as e:
    print(f"✗ HTTP Error {e.code}: {e.reason}\n")
        
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
