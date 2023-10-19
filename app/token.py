from datetime import datetime, timedelta
import os
import uuid
from cachetools import TTLCache
from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic import BaseModel
from jose import JWTError, jwt

token_cache = TTLCache(maxsize=1000, ttl=3600)

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    username: str or None = None
    
def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
    
    load_dotenv()
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str, credentials_exception):
    load_dotenv()
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if username is None:
            raise credentials_exception
        
        if jti and jti in token_cache:
            raise HTTPException(status_code=401, detail="Token is invalid", headers={"WWW-Authenticate": "Bearer"})
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    return token_data