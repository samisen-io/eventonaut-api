from fastapi import APIRouter, Depends, HTTPException, Security, status
import logging
from sqlalchemy.orm import Session
from app.oauth2 import get_current_active_user
from ..schemas import user_schemas as schemas
from ..crud import users_crud as crud
from ..dependencies import get_db
from email_validator import validate_email, EmailNotValidError
from app.schemas.user_schemas import UserAuthentication as User
from .. import basicauth, hashing
from ..crud import role_crud

router = APIRouter(tags=["users"])

from fastapi import HTTPException, status

@router.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    try:
        valid = validate_email(user.email)
        user.email = valid.normalized.lower()
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    role_ids = []
    for role_id in user.user_role_ids:
        db_role = role_crud.get_role(db, role_id=role_id)
        if db_role is None:
            logging.exception("Role not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        role_ids.append(db_role.id)
    try:
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            logging.exception("Email already registered")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        user = crud.create_user(db=db, user=user, role_ids=role_ids)
        logging.info("User created: " + user.uuid)
        return user
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/users/all_users", response_model=list[schemas.User])
def get_all_users(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, offset=offset, limit=limit)
    if users is None or len(users) == 0:
        logging.exception("No user found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    logging.info("Users retrieved")
    return users

@router.get("/users", response_model=schemas.User)
def get_user(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logging.info("User retrieved: " + db_user.uuid)
    return db_user

@router.put("/users", response_model=schemas.User)
def update_user(user: schemas.UserBaseUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_user = crud.get_db_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated_user = crud.update_user(db=db, user=user, db_user=db_user)
    logging.info("User updated: " + updated_user.uuid)
    return updated_user

@router.put("/users/password", response_model=schemas.User)
def update_user_password(user: schemas.UserPasswordUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_user = crud.get_db_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.old_password == user.new_password:
        logging.exception("New password cannot be same as old password")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be same as old password")
    if not hashing.verify_password(user.old_password, db_user.hashed_password):
        logging.exception("Incorrect old password")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")
    updated_user = crud.update_user_password(db=db, user=user, db_user=db_user)
    logging.info("User password updated: " + updated_user.uuid)
    return updated_user

@router.delete("/users")
def delete_user(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    deleted_user = crud.delete_user(db=db, user=db_user)
    logging.info("User deleted: " + db_user.uuid)
    return deleted_user