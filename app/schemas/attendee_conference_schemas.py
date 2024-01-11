from pydantic import BaseModel, field_validator, Field
from fastapi import HTTPException, status
from datetime import date

class AttendeeConferenceCreate(BaseModel):
    conference_identifier: str
    
    @field_validator('conference_identifier')
    def validate_conference_identifier(cls, v):
        if v.strip() == '':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conference identifier cannot be empty")
        elif v == 'string':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Conference identifier cannot be string")
        elif len(v) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conference identifier")
        return v

class Conference(BaseModel):
    id: str = Field(alias='uuid', serialization_alias='id')
    name: str
    location: str
    start_date: date
    end_date: date
    description: str
    conference_logo: str

class AttendeeConference(BaseModel):
    uuid: str = Field(serialization_alias='id')
    attendee_id: str
    conference: Conference
    class Config:
        orm_mode = True