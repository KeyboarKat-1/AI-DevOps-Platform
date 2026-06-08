from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.deployment import Deployment
from app.schemas.deployment import DeploymentCreate, DeploymentRead

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/deployments", response_model=DeploymentRead, status_code=status.HTTP_201_CREATED)
def create_deployment(deployment_in: DeploymentCreate, db: Session = Depends(get_db)):
    """Create a new deployment record and persist it to the database."""
    deployment = Deployment(
        service_name=deployment_in.service_name,
        environment=deployment_in.environment,
        status=deployment_in.status,
        deployed_at=deployment_in.deployed_at or datetime.utcnow(),
    )

    db.add(deployment)
    try:
        db.commit()
        db.refresh(deployment)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create deployment record.",
        ) from exc

    return deployment


@router.get("/deployments", response_model=List[DeploymentRead], status_code=status.HTTP_200_OK)
def list_deployments(db: Session = Depends(get_db)):
    return db.query(Deployment).order_by(Deployment.deployed_at.desc()).all()


@router.get("/deployments/{deployment_id}", response_model=DeploymentRead, status_code=status.HTTP_200_OK)
def get_deployment(deployment_id: int, db: Session = Depends(get_db)):
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")
    return deployment


@router.put("/deployments/{deployment_id}", response_model=DeploymentRead, status_code=status.HTTP_200_OK)
def update_deployment(deployment_id: int, deployment_in: DeploymentCreate, db: Session = Depends(get_db)):
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")

    deployment.service_name = deployment_in.service_name
    deployment.environment = deployment_in.environment
    deployment.status = deployment_in.status
    deployment.deployed_at = deployment_in.deployed_at or deployment.deployed_at

    try:
        db.commit()
        db.refresh(deployment)
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update deployment record.",
        ) from exc

    return deployment


@router.delete("/deployments/{deployment_id}", status_code=status.HTTP_200_OK)
def delete_deployment(deployment_id: int, db: Session = Depends(get_db)):
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")

    try:
        db.delete(deployment)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete deployment record.",
        ) from exc

    return {"success": True}
