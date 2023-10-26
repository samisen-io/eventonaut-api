from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.oauth2 import get_current_active_user
from ..schemas import user_schemas as schemas
from ..crud import users_crud as crud
from ..dependencies import get_db
from email_validator import validate_email, EmailNotValidError

router = APIRouter(tags=["users"])

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # validate email
    try:
        valid = validate_email(user.email)
        user.email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail="Invalid email")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/users/", response_model=list[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    users = crud.get_users(db, skip=skip, limit=limit)
    if users is None or len(users) == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return users

@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#update user by user id and check if email is already registered
@router.put("/users/email/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserBase, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # validate email
    try:
        valid = validate_email(user.email)
        user.email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail="Invalid email")
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user and db_user.id != user_id:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.update_user(db=db, user=user, user_id=user_id)

# upddate password by user id
@router.put("/users/password/{user_id}", response_model=schemas.User)
def update_user_password(user_id: int, user: schemas.UserPassword, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user_password(db=db, user=user, user_id=user_id)

#delete user
@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=user_id)

#get user by account_type
@router.get("/users/account_type/{account_type}", response_model=list[schemas.User])
def read_user_by_account_type(account_type: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if account_type.isnumeric():
        raise HTTPException(status_code=400, detail="Invalid account type")
    db_user = crud.get_users_by_account_type(db, account_type=account_type)
    if db_user is None or len(db_user) == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#get user by bussiness_type
@router.get("/users/bussiness_type/{bussiness_type}", response_model=list[schemas.User])
def read_user_by_bussiness_type(bussiness_type: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if bussiness_type.isnumeric():
        raise HTTPException(status_code=400, detail="Invalid bussiness type")
    db_user = crud.get_users_by_bussiness_type(db, bussiness_type=bussiness_type)
    if db_user is None or len(db_user) == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
