from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..basicauth import basic_auth
from ..crud import role_crud as crud
from ..dependencies import get_db
from ..schemas import role_schemas as schemas

router = APIRouter(tags=["role"])

@router.post("/role", response_model=schemas.RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role: schemas.RoleCreate,
    db: Session = Depends(get_db),
    basic_auth=Depends(basic_auth),
):
    try:
        return crud.create_role(db=db, role=role)
    except HTTPException as e:
        raise e

@router.get("/roles", response_model=List[schemas.RoleResponse])
def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    basic_auth=Depends(basic_auth),
):
    try:
        roles = crud.get_roles(db, skip=skip, limit=limit)
        return roles
    except HTTPException as e:
        raise e

@router.get("/role/{name}", response_model=schemas.RoleResponse)
def read_role(
    role_name: str, db: Session = Depends(get_db), basic_auth=Depends(basic_auth)
):
    db_role = crud.get_role(db, role_name=role_name)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.put("/role/{name}", response_model=schemas.RoleResponse)
def update_role(
    role: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    basic_auth=Depends(basic_auth),
):
    db_role = crud.update_role(db=db, role=role)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.delete("/role/{name}")
def delete_role(
    role_name: str, db: Session = Depends(get_db), basic_auth=Depends(basic_auth)
):
    db_role = crud.delete_role(db=db, role_name=role_name)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role