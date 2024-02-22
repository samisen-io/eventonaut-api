from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
# from app import my_token
from app import token
from app.schemas.user_schemas import UserAuthentication as User
from .dependencies import get_db
from .crud import users_crud
from sqlalchemy.orm import Session

oauth_2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes={"ATTENDEE": "ATTENDEE", "ORGANIZATION_ADMIN": "ORGANIZATION_ADMIN", "ORGANIZATION_USER": "ORGANIZATION_USER"},
    )

def get_current_user(
    security_scopes: SecurityScopes, db: Session = Depends(get_db),data: str = Depends(oauth_2_scheme)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"    
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    token_data = token.verify_token(data, credentials_exception, db) 
    user = users_crud.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    
    if token_data.scopes[0] not in security_scopes.scopes:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect scope",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return user

async def get_current_active_user(current_user: User = Security(get_current_user)):
    if current_user.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def get_current_user_RT(data: str, db):
    
    token_data = get_token_data(data,db)
    
    user = users_crud.get_active_user_by_email(db, email=token_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    if user.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

def get_token_data(data: str, db: Session):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    return token.verify_token_RT(data, credentials_exception, db)