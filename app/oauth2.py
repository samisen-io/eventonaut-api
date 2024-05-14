from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from app import token
from app.schemas.organization_schemas import Organization
from app.schemas.user_schemas import UserAuthentication as User
from .dependencies import get_db
from .crud import users_crud
from sqlalchemy.orm import Session
from app.crud import organization_crud

oauth_2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    scopes={"ATTENDEE": "Attendee scope", 
            "ORGANIZATION_ADMIN": "Organization admin scope", 
            "ORGANIZATION_USER": "Organization user scope"},
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

def get_current_organization(current_user: User = Security(get_current_active_user), db: Session = Depends(get_db)):
    user_id = current_user.id
    organization = organization_crud.get_organization_by_user_id(db, user_id=user_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    return organization

def get_current_active_organization(current_organization: Organization = Security(get_current_organization)):
    try:
        if current_organization.is_archived is True:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive organization")
        return current_organization
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_current_user_RT(data: str, db):
    
    token_data = get_token_data(data,db)
    
    user = users_crud.get_active_user_by_email(db, email=token_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    if user.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

def get_current_organization_RT(data: str, db):
    
    token_data = get_token_data(data,db)
    
    organization = organization_crud.get_organization_by_user_id(db, user_id=token_data.id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    if organization.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive organization")
    return organization

def get_token_data(data: str, db: Session):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    return token.verify_token_RT(data, credentials_exception, db)