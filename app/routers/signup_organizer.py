from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import signup_schemas as schemas
from app.dependencies import get_db
from app.services import signup_service

router = APIRouter(tags=["signup_organizer"])

@router.post("/signup")
def signup(user: schemas.UserBase, organization: schemas.OrganizationBase, db: Session = Depends(get_db)):
    return signup_service.signup(db=db, user=schemas.OrganizationBase)