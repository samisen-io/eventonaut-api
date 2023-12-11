from pydantic import BaseModel, validator, Field
from fastapi import HTTPException, status

class AttendeeConferenceCreate(BaseModel):
    conference_code: str
    
    @validator('conference_code')
    def validate_conference_code(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Conference code cannot be null')
        return v

class AttendeeConferenceCreateId(BaseModel):
    conference_id: str
    
    @validator('conference_id')
    def validate_conference_id(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Conference id cannot be null')
        return v

class AttendeeConference(BaseModel):
    uuid: str = Field(serialization_alias='id')
    attendee_id: str
    conference: dict
    class Config:
        orm_mode = True