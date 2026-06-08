from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.base import Base


class Deployment(Base):
    """SQLAlchemy model for deployment records."""

    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(150), nullable=False, index=True)
    environment = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False)
    deployed_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
