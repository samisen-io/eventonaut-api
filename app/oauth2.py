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
    scopes={"organizer": "organizer", "attendee": "attendee"},
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
    token_data = token.verify_token(data, credentials_exception) 
    user = users_crud.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    # print(security_scopes.scopes)
    # print(token_data.scopes)
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
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
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    token_data = token.verify_token_RT(data, credentials_exception)
    user = users_crud.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    if user.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user