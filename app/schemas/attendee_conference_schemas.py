from pydantic import BaseModel, field_validator, Field

class AttendeeConferenceCreate(BaseModel):
    conference_identifier: str
    
    @field_validator('conference_identifier')
    def validate_conference_identifier(cls, v):
        if v.strip() == '':
            raise ValueError("Conference identifier cannot be empty")
        elif len(v) < 6:
            raise ValueError("Conference identifier cannot be less than 6 characters")
        return v

class AttendeeConference(BaseModel):
    uuid: str = Field(serialization_alias='id')
    attendee_id: str 
    conference_id: str
    
    class Config:
        orm_mode = True