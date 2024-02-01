from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException, status as statuscode
from ..static_enums import organizer, attendee, client, event, session
  
class StaticOrganizer(BaseModel):
    status: str
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(organizer.OrganizerEnum.__members__):
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v
    
class StaticClient(BaseModel):
    status: str
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(client.ClientEnum.__members__):
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v
    
class StaticEvent(BaseModel):
    status: str
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(event.EventEnum.__members__):
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v
    
class StaticSession(BaseModel):
    status: str
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(session.SessionEnum.__members__):
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v
    
class StaticAttendee(BaseModel):
    status: str
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(attendee.AttendeeEnum.__members__):
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v    
    
class StaticTableOutput(BaseModel):
    uuid: str = Field(serialization_alias="id")
    status: str
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True