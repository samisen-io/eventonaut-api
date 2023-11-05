from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from .agenda_schemas import Agenda

#pydantic model for attendeebase
class AttendeeBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    
    @validator('first_name')
    def first_name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid first name")
        return v
    
    @validator('last_name')
    def last_name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid last name")
        return v
    
#pydantic model for attendee create
class AttendeeCreate(AttendeeBase):
    hashed_password: str

    @validator('hashed_password')
    def hashed_password_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" ") or len(v) < 8 or len(v) > 16:
            raise HTTPException(status_code=400, detail="Invalid password")
        return v

#pydantic model for attendee password
class AttendePassword(BaseModel):
    id: str
    hashed_password: str

    @validator('id')
    def id_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid id")
        return v
    
    @validator('hashed_password')
    def hashed_password_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" ") or len(v) < 8 or len(v) > 16:
            raise HTTPException(status_code=400, detail="Invalid password")
        return v

class AttendeeUpdate(BaseModel):
    id: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None

    @validator('id')
    def id_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid id")
        return v
    
    @validator('first_name')
    def first_name_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid first name")
        return v
    
    @validator('last_name')
    def last_name_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid last name")
        return v

#pydantic model for attendee
class Attendee(AttendeeBase):
    uuid: str = Field(serialization_alias="id")
    agenda: list[Agenda] = []
    is_active: bool
    class Config:
        orm_mode = True