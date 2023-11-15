from pydantic import BaseModel, validator, Field
from .conference_schemas import Conference

class AttendeeConferenceCreate(BaseModel):
    attendee_id: str
    conference_id: str

    @validator('attendee_id')
    def validate_attendee_id(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise ValueError('Attendee id cannot be null')
        elif len(v) > 36:
            raise ValueError('Attendee id cannot be more than 36 characters')
        return v
    
    @validator('conference_id')
    def validate_conference_id(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise ValueError('Conference id cannot be null')
        elif len(v) > 36:
            raise ValueError('Conference id cannot be more than 36 characters')
        return v
    
class AttendeeConference(BaseModel):
    uuid: str = Field(serialization_alias='id')
    attendee_id: str
    conference_id: list[str] = []
    class Config:
        orm_mode = True