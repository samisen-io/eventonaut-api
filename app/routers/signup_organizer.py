from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas import signup_schemas as schemas
from app.dependencies import get_db
from app.services import signup_service

router = APIRouter(tags=["signup_organizer"])

@router.post("/signup")
def signup(organizer_signup_request: schemas.SignupOrganizer, db: Session = Depends(get_db)):
    
    response = signup_service.signup_organizer(db=db, organizer_signup_request = organizer_signup_request)
    
    return response