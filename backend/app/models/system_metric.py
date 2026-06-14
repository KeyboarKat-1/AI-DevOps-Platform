"""SQLAlchemy model for system metrics collected from monitoring agents."""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Index, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class SystemMetric(Base):
    """
    Stores system metrics collected from installed monitoring agents.
    
    Each agent reports CPU, memory, and disk usage periodically.
    Metrics are associated with a user through their agent API key.
    """

    __tablename__ = "system_metrics"

    # Primary key: unique identifier for each metric record
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key linking to the user who owns this agent
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Hostname of the monitored machine
    hostname = Column(String(255), nullable=False, index=True)

    # CPU usage percentage (0-100)
    cpu_usage = Column(Float, nullable=False)

    # Memory/RAM usage percentage (0-100)
    memory_usage = Column(Float, nullable=False)

    # Disk usage percentage (0-100)
    disk_usage = Column(Float, nullable=False)

    # Operating system name (e.g., "Windows", "Linux", "Darwin")
    operating_system = Column(String(50), nullable=False)

    # Timestamp when the metric was collected (UTC)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)

    # Index for efficient queries on user_id + timestamp (for historical data)
    __table_args__ = (
        Index('ix_system_metrics_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_system_metrics_hostname_timestamp', 'hostname', 'timestamp'),
    )

    # Relationship to User
    user = relationship("User", back_populates="system_metrics")

    def __repr__(self) -> str:
        return (
            f"<SystemMetric(id={self.id}, hostname={self.hostname}, "
            f"cpu={self.cpu_usage}%, mem={self.memory_usage}%, "
            f"disk={self.disk_usage}%, timestamp={self.timestamp})>"
        )
