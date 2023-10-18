from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer

from app import token
from app.routers.authentication import get_user, db, User

oauth_2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(data: str = Depends(oauth_2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    
    token_data = token.verify_token(data, credentials_exception) 
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user
    
    # return token.verify_token(data, credentials_exception)

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    token_data = current_user
    # request.state.token_data = token_data
    return current_user
