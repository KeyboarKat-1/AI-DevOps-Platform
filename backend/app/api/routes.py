from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.api.dependencies import get_current_user, get_db
from app.api.deployment_routes import router as deployment_router
from app.api.incident_routes import router as incident_router
from app.api.metrics_routes import router as metrics_router
from app.api.insights_routes import router as insights_router
from app.api.agent_insights_routes import router as agent_insights_router
from app.api.docker_routes import router as docker_router
from app.api.agent_metrics_routes import router as agent_metrics_router
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserProfile, UserUpdate, ProfileUpdateResponse
from app.services.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from sqlalchemy import text
from app.db.session import engine

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "Backend API Healthy"}


@router.get("/db/health")
def db_health():
    """Lightweight DB connectivity check used for monitoring and debugging."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "reachable"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}") from exc


router.include_router(deployment_router)
router.include_router(incident_router)
router.include_router(metrics_router)
router.include_router(insights_router)
router.include_router(docker_router)
router.include_router(agent_metrics_router)  # Agent-based monitoring routes
router.include_router(agent_insights_router)  # Agent-specific AI insights


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account in the database."""
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"status": "success", "user_id": db_user.id}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Registration failed: {str(exc)}"
        ) from exc


@router.post("/auth/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user and return a JWT access token."""
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
    except OperationalError as exc:
        # Database connection/authentication failed (e.g. bad credentials)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable. Check DATABASE_URL and DB server.",
        ) from exc
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email, or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    """A protected route that requires a valid JWT token."""
    return {
        "status": "success",
        "username": current_user.username,
        "email": current_user.email,
    }


@router.get("/me", response_model=UserProfile)
def get_current_profile(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return {
        "username": current_user.username,
        "email": current_user.email,
    }


@router.put("/profile/update", response_model=ProfileUpdateResponse)
def update_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    old_username = current_user.username
    """Update the authenticated user's profile information."""
    if profile_update.username:
        current_user.username = profile_update.username
    if profile_update.email:
        current_user.email = profile_update.email

    try:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists. Please choose a different value.",
        )
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Profile update failed: {str(exc)}",
        ) from exc

    result = {
        "username": current_user.username,
        "email": current_user.email,
    }
    if profile_update.username and profile_update.username != old_username:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.username}, expires_delta=access_token_expires
        )
        result["access_token"] = access_token
        result["token_type"] = "bearer"
    return result
