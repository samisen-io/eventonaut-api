from pydantic import BaseModel, field_validator, Field
from fastapi import HTTPException, status
from datetime import date

class AttendeeConferenceCreate(BaseModel):
    conference_identifier: str
    
    @field_validator('conference_identifier')
    def validate_conference_identifier(cls, v):
        if v.strip() == '':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conference identifier cannot be empty")
        elif len(v) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conference identifier")
        return v

class AttendeeConference(BaseModel):
    uuid: str = Field(serialization_alias='id')
    attendee_id: str 
    conference_id: str
    
    class Config:
        orm_mode = True