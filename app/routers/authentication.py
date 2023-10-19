from datetime import timedelta
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from ..crud import users_crud
from ..dependencies import get_db
from app.token import Token, create_access_token
from sqlalchemy.orm import Session
from validate_email_address import validate_email
from jose import JWTError, jwt
from ..token import token_cache

router = APIRouter(tags=["authentication"])

class User(BaseModel):
    email: str
    first_name: str
    last_name: str
    account_type: str
    bussiness_type: str
    is_active: bool

def authenticate_user(db: Session, username: str, password: str, token_jti: str):
    user =  users_crud.get_user_by_email_and_password(db=db,email=username, password=password)
    if token_jti in token_cache:
        raise HTTPException(status_code=401, detail="Token is invalid", headers={"WWW-Authenticate": "Bearer"})
    return user

@router.post("/login", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm= Depends()):
    
    # validation = validate_email(form_data.username)
    # if validation==False:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email ID format")
    
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password, token_jti=None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    
    load_dotenv()
    
    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email, "id":user.id}, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(jwt_token: str):
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti:
            token_cache[jti] = True
            return {"message": "Token invalidated"}
        else:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")