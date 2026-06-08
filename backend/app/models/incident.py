from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.base import Base


class Incident(Base):
    """SQLAlchemy model representing an incident or alert record."""

    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    service_name = Column(String(150), nullable=False, index=True)
    environment = Column(String(50), nullable=False)
    priority = Column(String(50), nullable=False, default="medium")
    status = Column(String(50), nullable=False, default="active")
    detected_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
