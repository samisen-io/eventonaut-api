from sqlalchemy.orm import Session

from app.schemas import signup_schemas as schemas

def signup(db: Session, user: schemas.OrganizationBase):
    return "User created successfully!"