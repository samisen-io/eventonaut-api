import os
import uuid
from cachetools import TTLCache
from dotenv import load_dotenv
from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.schemas.token_schemas import Token, TokenData
from pydantic import BaseModel, ValidationError

token_cache = TTLCache(maxsize=1000, ttl=timedelta(days=10))
    
load_dotenv()
REFRESH_TOKEN_SECRET_KEY = os.getenv("REFRESH_TOKEN_SECRET_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  
    issue_time = datetime.utcnow().timestamp()  
    to_encode.update({"iat":issue_time, "exp": expire, "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30)
    issue_time = datetime.utcnow().timestamp()
    to_encode.update({"iat":issue_time,"exp": expire, "jti": str(uuid.uuid4())})
    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        if username is None:
            raise credentials_exception
        if jti and jti in token_cache:
            raise HTTPException(status_code=401, detail="Token is invalid", headers={"WWW-Authenticate": "Bearer"})
        token_scopes = payload.get("scopes", [])
        # print(token_scopes)
        token_data = TokenData(username=username, scopes=token_scopes)
        # print(token_data)
    except (JWTError, ValidationError):
        raise credentials_exception
    return token_data


def verify_token_RT(token:str, credentials_exception):
    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        if username is None:
            raise credentials_exception
        if jti and jti in token_cache:
            raise HTTPException(status_code=401, detail="Token is invalid")
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data

def invalidate_refresh_token(jwt_token:str):
    try:
        payload = jwt.decode(jwt_token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if jti:
            token_cache[jti] = True
            return {"message": "Token invalidated"}
        else:
            raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")

