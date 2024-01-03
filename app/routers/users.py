from fastapi import APIRouter, Depends, HTTPException, Security, status
import logging
from sqlalchemy.orm import Session
from app.oauth2 import get_current_active_user
from ..schemas import user_schemas as schemas
from ..crud import users_crud as crud
from ..dependencies import get_db
from email_validator import validate_email, EmailNotValidError
from app.schemas.user_schemas import UserAuthentication as User
from .. import basicauth

router = APIRouter(tags=["users"])


@router.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    try:
        valid = validate_email(user.email)
        user.email = valid.normalized.lower()
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logging.exception("Email already registered")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = crud.create_user(db=db, user=user)
    logging.info("User created: " + user.uuid)
    return user

@router.get("/users/all_users", response_model=list[schemas.User])
def get_users(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, offset=offset, limit=limit)
    if users is None or len(users) == 0:
        logging.exception("Users not found")
        raise HTTPException(status_code=404, detail="User not found")
    logging.info("Users retrieved")
    return users

@router.get("/users", response_model=schemas.User)
def get_user(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    logging.info("User retrieved: " + db_user.uuid)
    return db_user

#update user by user id and check if email is already registered
@router.put("/users", response_model=schemas.User)
def update_user(user: schemas.UserBaseUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if all(value is None for value in dict(user).values()):
        logging.exception("Invalid request body")
        raise HTTPException(status_code=400, detail="Invalid request body")
    if current_user.id <= 0:
        logging.exception("Invalid user id")
        raise HTTPException(status_code=400, detail="Invalid user id")
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    logging.info("User updated: " + db_user.uuid)
    return crud.update_user(db=db, user=user, user_id=current_user.id)

# upddate password by user id
@router.put("/users/password", response_model=schemas.User)
def update_user_password(user: schemas.UserPasswordUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    if user.old_password == user.new_password:
        logging.exception("New password cannot be same as old password")
        raise HTTPException(status_code=400, detail="New password cannot be same as old password")
    if not crud.get_user_by_email_and_password(db, email=db_user.email, password=user.old_password):
        logging.exception("Invalid old password")
        raise HTTPException(status_code=400, detail="Invalid old password")
    logging.info("User password updated: " + db_user.uuid)
    return crud.update_user_password(db=db, user=user, user_id=current_user.id)

#delete user
@router.delete("/users")
def delete_user(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    logging.info("User deleted: " + db_user.uuid)
    return crud.delete_user(db=db, user_id=current_user.id)