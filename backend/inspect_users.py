from sqlalchemy import inspect, create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
print('has_users_table=', 'users' in inspector.get_table_names())
print('columns=', [col['name'] for col in inspector.get_columns('users')])
