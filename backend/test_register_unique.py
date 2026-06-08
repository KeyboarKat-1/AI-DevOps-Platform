#!/usr/bin/env python3
"""Test register with unique user data."""

import urllib.request
import json
import sys
import uuid

# Generate unique credentials
unique_id = str(uuid.uuid4())[:8]
payload = {
    "username": f"user_{unique_id}",
    "email": f"user_{unique_id}@example.com",
    "password": "testpass123"
}

print(f"Testing POST /register with unique user")
print(f"Payload: {json.dumps(payload)}\n")

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
        print(f"✓ Response:\n{json.dumps(response_data, indent=2)}\n")
        print("✓ SUCCESS: Registration worked!")
        
except urllib.error.HTTPError as e:
    print(f"✗ HTTP Error {e.code}: {e.reason}\n")
    try:
        error_response = e.read().decode('utf-8')
        print(f"Error Response Body:\n{error_response}")
    except:
        print("(Could not read error response body)")
        
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
