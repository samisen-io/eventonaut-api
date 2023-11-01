from pydantic import BaseModel, validator
from fastapi import HTTPException

#pydantic model for settings
class SettingsCreate(BaseModel):
    conference_id: int
    body: dict

    @validator('conference_id')
    def id_must_be_positive(cls, v):
        if v <= 0:
            raise HTTPException(status_code=400, detail="Invalid conference id")
        return v
    
    @validator('body')
    def body_must_not_be_empty(cls, v):
        if v is None or len(v) == 0:
            raise HTTPException(status_code=400, detail="Body is empty")
        return v

#pydantic model for settings
class Settings(SettingsCreate):
    id: int
    owner_id: int
    class Config:
        orm_mode = True