from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app import token
from app.schemas.user_schemas import User
from .dependencies import get_db
from .crud import users_crud
from sqlalchemy.orm import Session

oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(db: Session = Depends(get_db),data: str = Depends(oauth_2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token_data = token.verify_token(data, credentials_exception) 
    user = users_crud.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def get_current_user_RT(data: str, db):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    token_data = token.verify_token_RT(data, credentials_exception)
    user = users_crud.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    if user.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

async def get_current_active_user_RT(current_user: User = Depends(get_current_user_RT)):
    if current_user.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user