from pydantic import BaseModel, validator
from fastapi import HTTPException

#pydantic model for settings
class SettingsBase(BaseModel):
    body: dict

    
    @validator('body')
    def body_must_not_be_empty(cls, v):
        if v is None or len(v) == 0:
            raise HTTPException(status_code=400, detail="Body is empty")
        return v

class SettingsCreate(SettingsBase):
    conference_uuid: str

    @validator('conference_uuid')
    def id_must_be_positive(cls, v):
        if v is None or len(v) == 0:
            raise HTTPException(status_code=400, detail="Invalid conference id")
        return v
    
#pydantic model for settings
class Settings(SettingsBase):
    uuid: str
    conference_id: int
    owner_id: int
    class Config:
        orm_mode = True