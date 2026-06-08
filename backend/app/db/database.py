"""Database module that exposes the shared SQLAlchemy Base and engine.

This module reuses the engine created in `app.db.session` so there is a
single engine instance and a consistent fallback behavior.
"""
from app.db.session import engine, SessionLocal
from app.db.base import Base

# Exported: engine, SessionLocal, Base
