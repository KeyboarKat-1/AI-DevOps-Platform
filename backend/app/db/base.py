from sqlalchemy.orm import declarative_base


# Base is the foundation for all ORM models in the application.
# Model classes will inherit from Base to gain SQLAlchemy mapping behavior.
Base = declarative_base()
