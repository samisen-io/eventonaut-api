from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..crud import organization_crud as crud
from ..schemas import organization_schemas as schemas
from ..database import SessionLocal

router = APIRouter(tags=['organizations'])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/organizations/", response_model=schemas.Organization)
def create_organization(organization: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    return crud.create_organization(db=db, organization=organization)

@router.get("/organizations/", response_model=List[schemas.Organization])
def read_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    organizations = crud.get_all_organizations(db, skip, limit)
    return organizations

@router.get("/organizations/{organization_id}", response_model=schemas.Organization)
def read_organization(organization_id: str, db: Session = Depends(get_db)):
    db_organization = crud.get_organization_by_id(db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization

@router.put("/organizations/", response_model=schemas.Organization)
def update_organization(organization: schemas.OrganizationUpdate, db: Session = Depends(get_db)):
    db_organization = crud.get_organization_by_id(db, organization_id=organization.id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return crud.update_organization(db=db, organization=organization, db_organization=db_organization)

@router.delete("/organizations/{organization_id}")
def delete_organization(organization_id: str, db: Session = Depends(get_db)):
    db_organization = crud.get_organization_by_id(db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    crud.delete_organization(db=db, db_organization=db_organization)
    return {"detail": "Organization deleted"}