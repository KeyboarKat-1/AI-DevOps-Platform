from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """SQLAlchemy model representing a user account."""

    __tablename__ = "users"

    # Primary key: unique identifier for each user record.
    id = Column(Integer, primary_key=True, index=True)

    # Username used for login and display; must be unique.
    username = Column(String(150), unique=True, nullable=False, index=True)

    # Email address for the user; must be unique and required.
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Hashed password stored securely; never store raw passwords in production.
    hashed_password = Column(String(256), nullable=False)

    # Whether the user account is active and allowed to log in.
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamp for when the record was created.
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships to agent-related tables
    system_metrics = relationship("SystemMetric", back_populates="user", cascade="all, delete-orphan")
    agent_api_keys = relationship("AgentApiKey", back_populates="user", cascade="all, delete-orphan")
