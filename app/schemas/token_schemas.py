from pydantic import BaseModel
from typing import List

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    
class TokenData(BaseModel):
    username: str | None = None
    scopes: List[str] = []
    id: int
    
class TokenInput(BaseModel):
    token: str