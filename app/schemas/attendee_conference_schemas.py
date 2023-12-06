from pydantic import BaseModel, validator, Field

class AttendeeConferenceCreate(BaseModel):
    conference_code: str
    
    @validator('conference_code')
    def validate_conference_code(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise ValueError('Conference code cannot be null')
        return v
    
class AttendeeConference(BaseModel):
    uuid: str = Field(serialization_alias='id')
    attendee_id: str
    conference: dict
    class Config:
        orm_mode = True