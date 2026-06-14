"""SQLAlchemy model for agent API keys used for authentication."""
from datetime import datetime
import secrets

from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.db.base import Base


class AgentApiKey(Base):
    """
    Stores API keys used by monitoring agents for secure communication.
    
    Each user can have multiple agent API keys for different machines.
    Keys are long random strings generated securely.
    """

    __tablename__ = "agent_api_keys"

    # Primary key: unique identifier for each key record
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key linking to the user who owns this key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # The actual API key (hashed or plaintext - we'll store plaintext with secure generation)
    # This is a long random string that agents use in request headers
    api_key = Column(String(255), unique=True, nullable=False, index=True)

    # Human-readable name for this key (e.g., "Office Desktop", "Server 1")
    name = Column(String(255), nullable=False)

    # Whether this key is currently active
    is_active = Column(Boolean, default=True, nullable=False)

    # Optional: associated hostname for this key
    hostname = Column(String(255), nullable=True)

    # Timestamp when the key was created
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Timestamp when the key was last used
    last_used = Column(DateTime(timezone=True), nullable=True)

    # Index for efficient queries
    __table_args__ = (
        Index('ix_agent_api_keys_user_active', 'user_id', 'is_active'),
    )

    # Relationship to User
    user = relationship("User", back_populates="agent_api_keys")

    def __repr__(self) -> str:
        masked_key = f"{self.api_key[:8]}..." if self.api_key else "None"
        return (
            f"<AgentApiKey(id={self.id}, name={self.name}, "
            f"key={masked_key}, active={self.is_active}, "
            f"created_at={self.created_at})>"
        )

    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a secure random API key.
        
        Returns a 32-byte random string encoded as hex (64 characters).
        """
        return secrets.token_hex(32)
