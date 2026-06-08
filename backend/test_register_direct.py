#!/usr/bin/env python3
"""Test register endpoint logic directly."""

import sys
sys.path.insert(0, 'c:\\Users\\vatal\\New folder (2)\\AI-DevOps-Platform\\backend')

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.services.auth import get_password_hash
from app.schemas.user import UserCreate

print("Testing user registration logic directly:\n")

# Create a test user
test_user = UserCreate(
    username="directtest",
    email="directtest@example.com",
    password="testpassword123"
)

try:
    # Hash the password
    print(f"1. Hashing password...")
    hashed_pwd = get_password_hash(test_user.password)
    print(f"   ✓ Password hashed successfully")
    
    # Create user object
    print(f"2. Creating User model...")
    db_user = User(
        username=test_user.username,
        email=test_user.email,
        hashed_password=hashed_pwd,
    )
    print(f"   ✓ User model created")
    
    # Get database session
    print(f"3. Getting database session...")
    db = SessionLocal()
    print(f"   ✓ Session created: {db}")
    
    # Add to database
    print(f"4. Adding user to database...")
    db.add(db_user)
    print(f"   ✓ User added")
    
    # Commit
    print(f"5. Committing to database...")
    db.commit()
    print(f"   ✓ Commit successful")
    
    # Refresh
    print(f"6. Refreshing user object...")
    db.refresh(db_user)
    print(f"   ✓ User refreshed, ID: {db_user.id}")
    
    print(f"\n✓ SUCCESS: User registered with ID {db_user.id}")
    
    # Cleanup
    db.close()
    
except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
