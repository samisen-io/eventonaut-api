import os
from datetime import timedelta
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user_schemas import UserAuthentication as User
from app.schemas.token_schemas import TokenInput
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

from app.oauth2 import get_current_active_user, get_current_user_RT, oauth_2_scheme

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
        raise HTTPException(status_code=401, detail="Token is invalid", headers={"WWW-Authenticate": "Bearer"})
    return user

@router.post("/login", response_model=Token)
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm= Depends(), basic_auth = Depends(basicauth.basic_auth)):
    form_data.username = form_data.username.lower().strip()
    scopes = form_data.scopes if form_data.scopes else None
    user = authenticate_user(db=db, username=form_data.username, password=form_data.password, token_jti=None)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    if not scopes or user.role not in scopes or len(scopes) != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect scope",
                            headers={"WWW-Authenticate": "Bearer"})
    if user.role == "organizer":
        access_token_expires = timedelta(minutes=ORGANIZER_ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=ORGANIZER_REFRESH_TOKEN_EXPIRE_MINUTES)

    elif user.role == "attendee":
        access_token_expires = timedelta(days=ATTENDEE_ACCESS_TOKEN_EXPIRE_DAYS)
        refresh_token_expires = timedelta(days=ATTENDEE_REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_token = create_refresh_token(data={"sub": user.email, "scopes": [user.role]}, expires_delta=refresh_token_expires)
    rt_jti = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM]).get("jti")
    access_token = create_access_token(data={"sub": user.email, "id":user.id, "rt_jti":rt_jti, "scopes": [user.role]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@router.get("/print_something_attendee")
def print_something(current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    return {"message": "Hello World"}

@router.get("/print_something_organizer")
def print_something2(current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    return {"message": "Hello World"}
    
@router.post("/refresh_token", response_model = Token)
async def create_new_access_and_refresh_token(token:TokenInput,  db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    try:
        jwt_token = token.token
        # validate refresh token
        current_user: User = get_current_user_RT(jwt_token,db)
        invalidate_refresh_token(jwt_token=jwt_token, db=db)

        if current_user.role == "organizer":
            access_token_expires = timedelta(minutes=ORGANIZER_ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expires = timedelta(minutes=ORGANIZER_REFRESH_TOKEN_EXPIRE_MINUTES)
        
        elif current_user.role == "attendee":
            access_token_expires = timedelta(days=ATTENDEE_ACCESS_TOKEN_EXPIRE_DAYS)
            refresh_token_expires = timedelta(days=ATTENDEE_REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_token = create_refresh_token(data={"sub": current_user.email}, expires_delta=refresh_token_expires)
        rt_jti = jwt.decode(refresh_token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM]).get("jti")
        access_token = create_access_token(data={"sub": current_user.email, "id":current_user.id, "rt_jti":rt_jti, "scopes": [current_user.role]}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
    
@router.post("/invalidate_refresh_token")
async def invalidate_RT(token:TokenInput, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    try:
        jwt_token = token.token
        current_user: User = get_current_user_RT(jwt_token,db)
        invalidate_refresh_token(jwt_token=jwt_token, db=db)
        return {"message": "Token invalidated"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

@router.post("/logout")
async def logout(jwt_token: str=Depends(oauth_2_scheme), current_user: User = Security(get_current_active_user, scopes=["organizer", "attendee"]),db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        jti_expires = datetime.fromtimestamp(payload.get("exp"))
        rt_jti = payload.get("rt_jti")
        rt_jti_expires =datetime.fromtimestamp(payload.get("exp"))
        if jti:
            if rt_jti:
                # token_cache[rt_jti] = True 
                logout_token_crud.insert_token(db=db, token_jti=rt_jti, expire_time=jti_expires, is_invalidated=True)           
            # token_cache[jti] = True
            logout_token_crud.insert_token(db=db, token_jti=jti, expire_time=rt_jti_expires, is_invalidated=True)
            return {"message": "Token invalidated"}
        else:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")