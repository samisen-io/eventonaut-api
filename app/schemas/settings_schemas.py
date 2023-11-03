from pydantic import BaseModel, validator, Field
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
    conference_id: str

    @validator('conference_id')
    def conference_id_must_be_positive(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid conference id")
        return v
    
#pydantic model for settings
class Settings(SettingsBase):
    uuid: str = Field(serialization_alias="id")
    class Config:
        orm_mode = True