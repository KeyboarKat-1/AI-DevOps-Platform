from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password using bcrypt, with a temporary plaintext fallback.

    This fallback is only for existing records where `hashed_password`
    contains a plain-text password string instead of a proper hash.
    Bcrypt truncates passwords to 72 bytes, so we do the same here.
    """
    # Bcrypt only uses first 72 bytes of password
    truncated_password = plain_password[:72]
    try:
        return pwd_context.verify(truncated_password, hashed_password)
    except UnknownHashError:
        return truncated_password == hashed_password


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt. Bcrypt truncates to 72 bytes."""
    # Bcrypt has a 72-byte password limit; truncate to avoid ValueError
    truncated_password = password[:72]
    return pwd_context.hash(truncated_password)


def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    """Authenticate a user by username or email."""
    user = db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return {}
