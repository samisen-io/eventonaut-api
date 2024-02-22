import os
from datetime import timedelta
import logging
from typing import Dict, List
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user_schemas import UserAuthentication as User
from app.schemas.token_schemas import TokenInput
from app.static_enums.role import RoleEnum
from ..crud import users_crud
from ..dependencies import get_db
from app.token import Token, create_access_token
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from ..token import create_refresh_token, invalidate_refresh_token
from .. import basicauth
from ..crud import logout_token_crud
from datetime import datetime
# from ..my_token import token_cache

from app.oauth2 import get_current_active_user, get_current_user_RT, get_token_data, oauth_2_scheme

import app

router = APIRouter(tags=["authentication"])

load_dotenv()

ORGANIZER_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ORGANIZER_ACCESS_TOKEN_EXPIRE_MINUTES"))
ATTENDEE_ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ATTENDEE_ACCESS_TOKEN_EXPIRE_DAYS"))

ORGANIZER_REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("ORGANIZER_REFRESH_TOKEN_EXPIRE_MINUTES"))
ATTENDEE_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("ATTENDEE_REFRESH_TOKEN_EXPIRE_DAYS"))

REFRESH_TOKEN_SECRET_KEY = os.getenv("REFRESH_TOKEN_SECRET_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def authenticate_user(db: Session, username: str, password: str, token_jti: str):
    user =  users_crud.get_user_by_email_and_password(db=db,email=username, password=password)
    db_tokens = logout_token_crud.get_all_jti_in_tokens(db=db)
    if token_jti in db_tokens:
        logging.exception("Token is invalid")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid", headers={"WWW-Authenticate": "Bearer"})
    return user

@router.post("/login", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm= Depends(), basic_auth = Depends(basicauth.basic_auth)):
    form_data.username = sanitize_username(form_data.username)
    scopes = get_scopes(form_data.scopes)
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password, token_jti=None)
    
    validate_user_and_scope(user, scopes)
    
    token_expirations = get_token_expirations(scopes[0])
    
    refresh_token = create_refresh_token(data={"sub": user.email, "scopes": scopes[0]}, expires_delta=token_expirations['refresh_token_expires'])
    rt_jti = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM]).get("jti")
    access_token = create_access_token(data={"sub": user.email, "id":user.id, "rt_jti":rt_jti, "scopes": scopes[0]}, expires_delta=token_expirations['access_token_expires'])
    
    logging.info("User logged in: " + user.uuid)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

def sanitize_username(username: str) -> str:
    return username.lower().strip()

def get_scopes(scopes: List[str]) -> List[str]:
    return scopes if scopes else None

def validate_user_and_scope(user: User, scopes: List[str]) -> None:
    if not user:
        logging.exception("Incorrect username or password")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    if not scopes or not any(scope in user.role for scope in scopes):
        logging.exception("Incorrect scope")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect scope",
                            headers={"WWW-Authenticate": "Bearer"})

def get_token_expirations(role: str) -> Dict[str, timedelta]:
    if role == RoleEnum.ATTENDEE.name:
        return {'access_token_expires': timedelta(days=ATTENDEE_ACCESS_TOKEN_EXPIRE_DAYS), 
                'refresh_token_expires': timedelta(days=ATTENDEE_REFRESH_TOKEN_EXPIRE_DAYS)}
    elif role == RoleEnum.ORGANIZATION_ADMIN.name or role == RoleEnum.ORGANIZATION_USER.name:
        return {'access_token_expires': timedelta(minutes=ORGANIZER_ACCESS_TOKEN_EXPIRE_MINUTES), 
                'refresh_token_expires': timedelta(minutes=ORGANIZER_REFRESH_TOKEN_EXPIRE_MINUTES)}
    else:
        logging.exception("Invalid role")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

@router.get("/print_something_attendee")
def print_something(current_user: User = Security(get_current_active_user, scopes=["ATTENDEE"])):
    logging.info("Attendee logged in: " + current_user.uuid)
    return {"message": "Hello World"}

@router.get("/print_something_organizer")
def print_something2(current_user: User = Security(get_current_active_user, scopes=["ORGANIZATION_ADMIN"])):
    logging.info("Organizer logged in: " + current_user.uuid)
    return {"message": "Hello World"}

@router.get("/print_something_organizer")
def print_something3(current_user: User = Security(get_current_active_user, scopes=["ORGANIZATION_USER"])):
    logging.info("Organizer logged in: " + current_user.uuid)
    return {"message": "Hello World"}
    
@router.post("/refresh_token", response_model = Token)
async def create_new_access_and_refresh_token(token:TokenInput,  db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    try:
        jwt_token = token.token
        token_data = get_token_data(jwt_token,db)
        
        current_user: User = get_current_user_RT(jwt_token,db)
        invalidate_refresh_token(jwt_token=jwt_token, db=db)

        token_expirations = get_token_expirations(token_data.scopes[0])
        
        refresh_token = create_refresh_token(data={"sub": current_user.email, "scopes": token_data.scopes[0]}, expires_delta=token_expirations['refresh_token_expires'])
        rt_jti = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM]).get("jti")
        access_token = create_access_token(data={"sub": current_user.email, "id":current_user.id, "rt_jti":rt_jti, "scopes": [token_data.scopes[0]]}, expires_delta=token_expirations['access_token_expires'])
        
        logging.info("Refresh token created: " + current_user.uuid)
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    except JWTError:
        logging.exception("Invalid token")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    
@router.post("/invalidate_refresh_token")
async def invalidate_RT(token:TokenInput, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    try:
        jwt_token = token.token
        current_user: User = get_current_user_RT(jwt_token,db)
        invalidate_refresh_token(jwt_token=jwt_token, db=db)
        logging.info("Refresh token invalidated: " + current_user.uuid)
        return {"message": "Token invalidated"}
    except JWTError:
        logging.exception("Invalid token")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

@router.post("/logout")
async def logout(jwt_token: str=Depends(oauth_2_scheme), current_user: User = Security(get_current_active_user, scopes=["ATTENDEE", "ORGANIZATION_ADMIN", "ORGANIZATION_USER"]),db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        jti_expires = datetime.fromtimestamp(payload.get("exp"))
        rt_jti = payload.get("rt_jti")
        rt_jti_expires =datetime.fromtimestamp(payload.get("exp"))
        if jti:
            if rt_jti:
                logout_token_crud.insert_token(db=db, token_jti=rt_jti, expire_time=jti_expires, is_invalidated=True)           
            logout_token_crud.insert_token(db=db, token_jti=jti, expire_time=rt_jti_expires, is_invalidated=True)
            logging.info("Token invalidated: " + current_user.uuid)
            return {"message": "Token invalidated"}
        else:
            logging.exception("Invalid token")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    except JWTError:
        logging.exception("Invalid token")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")