from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from datetime import date as Date, time

#pydantic model for session create
class SessionBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    description: str 
    date: Date
    location: str
    speakers: list[str]
    tags: list[str]

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('start_time')
    def start_time_must_not_be_empty(cls, v):
        if v is None or v == "":
            raise HTTPException(status_code=400, detail="Invalid start time")
        return v
    
    @validator('end_time')
    def end_time_must_not_be_empty(cls, v):
        if v is None or v == "":
            raise HTTPException(status_code=400, detail="Invalid end time")
        return v
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid description")
        elif len(v) > 2048:
            raise HTTPException(status_code=400, detail="Description too long")
        return v
    
    @validator('date')
    def date_must_not_be_empty(cls, v):
        if v is None or v == "":
            raise HTTPException(status_code=400, detail="Invalid date")
        return v
    
    @validator('location')
    def location_must_not_be_empty(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid location")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Location too long")
        return v
    
    @validator('speakers')
    def speakers_must_not_be_empty(cls, v):
        if v is None or v == "" or len(v) == 0:
            raise HTTPException(status_code=400, detail="Invalid speakers")
        for speaker in v:
            if speaker is None or speaker == "" or speaker == "string":
                raise HTTPException(status_code=400, detail="Invalid speaker")
            elif len(speaker) > 256:
                raise HTTPException(status_code=400, detail="Speaker name too long")
        return v
    
    @validator('tags')
    def tags_must_not_be_empty(cls, v):
        if v is None or v == "" or len(v) == 0:
            raise HTTPException(status_code=400, detail="Invalid tags")
        for tag in v:
            if tag is None or tag == "" or tag == "string":
                raise HTTPException(status_code=400, detail="Invalid tag")
            elif len(tag) > 256:
                raise HTTPException(status_code=400, detail="Tag name too long")
        return v
    
class SessionCreate(SessionBase):
    conference_id: str
    
    @validator('conference_id')
    def conference_id_must_not_be_empty(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid conference id")
        return v
    
#pydantic model for session
class Session(SessionBase):
    uuid: str = Field(serialization_alias="id")
    class Config:
        orm_mode = True

#pydantic model for session update
class SessionUpdate(BaseModel):
    id: str
    conference_id: str
    name: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    description: str | None = None
    date: Date | None = None
    location: str | None = None
    speakers: list[str] | None = None
    tags: list[str] | None = None

    @validator('id')
    def id_must_not_be_empty(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid id")
        return v
    
    @validator('conference_id')
    def conference_id_must_not_be_empty(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid conference id")
        return v
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('start_time')
    def start_time_must_not_be_empty(cls, v):
        if v == "":
            raise HTTPException(status_code=400, detail="Invalid start time")
        return v
    
    @validator('end_time')
    def end_time_must_not_be_empty(cls, v):
        if v == "":
            raise HTTPException(status_code=400, detail="Invalid end time")
        return v
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid description")
        elif len(v) > 2048:
            raise HTTPException(status_code=400, detail="Description too long")
        return v
    
    @validator('date')
    def date_must_not_be_empty(cls, v):
        if v == "":
            raise HTTPException(status_code=400, detail="Invalid date")
        return v
    
    @validator('location')
    def location_must_not_be_empty(cls, v):
        if v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid location")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Location too long")
        return v
    
    @validator('speakers')
    def speakers_must_not_be_empty(cls, v):
        if v == "":
            raise HTTPException(status_code=400, detail="Invalid speakers")
        for speaker in v:
            if speaker == "" or speaker == "string":
                raise HTTPException(status_code=400, detail="Invalid speaker")
            elif len(speaker) > 256:
                raise HTTPException(status_code=400, detail="Speaker name too long")
        return v
    
    @validator('tags')
    def tags_must_not_be_empty(cls, v):
        if v == "":
            raise HTTPException(status_code=400, detail="Invalid tags")
        for tag in v:
            if tag == "" or tag == "string":
                raise HTTPException(status_code=400, detail="Invalid tag")
            elif len(tag) > 256:
                raise HTTPException(status_code=400, detail="Tag name too long")
        return v
    
    class Config:
        orm_mode = True