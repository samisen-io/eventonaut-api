from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.oauth2 import get_current_active_user
from ..schemas import user_schemas as schemas
from ..crud import users_crud as crud
from ..dependencies import get_db
from email_validator import validate_email, EmailNotValidError


router = APIRouter(tags=["users"])


@router.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        valid = validate_email(user.email)
        user.email = valid.normalized.lower()
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.get("/users/all_users", response_model=list[schemas.User])
def get_users(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, offset=offset, limit=limit)
    if users is None or len(users) == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return users

@router.get("/users", response_model=schemas.User)
def get_user(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#update user by user id and check if email is already registered
@router.put("/users", response_model=schemas.User)
def update_user(user: schemas.UserBaseUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    if all(value is None for value in dict(user).values()):
        raise HTTPException(status_code=400, detail="Invalid request body")
    if current_user.id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.email is not None and user.email.strip() != "" and user.email != "string":
        try:
            valid = validate_email(user.email)
            user.email = valid.normalized.lower()
        except EmailNotValidError as e:
            raise HTTPException(status_code=400, detail="Invalid email")
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user and db_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
    return crud.update_user(db=db, user=user, user_id=current_user.id)

# upddate password by user id
@router.put("/users/password", response_model=schemas.User)
def update_user_password(user: schemas.UserPasswordUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.old_password == user.new_password:
        raise HTTPException(status_code=400, detail="New password cannot be same as old password")
    if not crud.get_user_by_email_and_password(db, email=db_user.email, password=user.old_password):
        raise HTTPException(status_code=400, detail="Invalid old password")
    return crud.update_user_password(db=db, user=user, user_id=current_user.id)

#delete user
@router.delete("/users")
def delete_user(db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=current_user.id)