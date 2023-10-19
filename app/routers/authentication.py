from datetime import timedelta
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.crud import get_user_by_email_and_password
from ..dependencies import get_db
from app.token import Token, create_access_token
from sqlalchemy.orm import Session


router = APIRouter(tags=["authentication"])

class User(BaseModel):
    email: str
    first_name: str
    last_name: str
    account_type: str
    bussiness_type: str
    is_active: bool

def authenticate_user(db: Session, username: str, password: str):
    user =  get_user_by_email_and_password(db=db,email=username, password=password)
    return user

class LoginRequestModeL(BaseModel):
    username: str
    password: str

@router.post("/login", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: LoginRequestModeL= Depends()):
# async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm= Depends()):
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password)
   
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    
    load_dotenv()
    
    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email, "id":user.id}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}