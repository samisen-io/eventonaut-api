from pydantic import BaseModel, validator, Field, field_validator, ValidationInfo
from datetime import date as Date, time
from ..static_enums import session
from ..url_validator import check_url

class SessionBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    description: str 
    date: Date = Field(..., description="Date format: YYYY-MM-DD")
    location: str
    session_image_url: str | None = None
    tags: list[str]
    status: str

    @field_validator('name','description','location')
    def values_validation(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        max_length = 2048 if info.field_name == "description" else 256
        if len(v) > max_length:
            raise ValueError(f"{info.field_name} cannot be longer than {max_length} characters")
        return v

    @field_validator('session_image_url')
    def session_image_url_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
            if not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v
    
    @field_validator('tags')
    def tags_validation(cls, v, info: ValidationInfo):
        if len(v) == 0:
            raise ValueError(f"{info.field_name} cannot be empty")
        for val in v:
            if val.strip() == "":
                raise ValueError(f"{info.field_name} cannot be empty")
            elif len(val) > 256:
                raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(session.SessionEnum.__members__):
            raise ValueError("Invalid status")
        return v

class SessionCreate(SessionBase):
    conference_id: str
    speakers: list[str] | None = None
    
    @field_validator('conference_id')
    def conference_id_must_not_be_empty(cls, v):
        if v.strip() == "":
            raise ValueError(f"conferece_id cannot be empty")
        return v
    
    @field_validator('speakers')
    def tags_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if len(v) == 0 or (len(v) == 1 and v[0].strip() == ""):
                return None
            for val in v:
                if val.strip() == "":
                    raise ValueError(f"{info.field_name} cannot be empty")
                elif len(val) > 256:
                    raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
class SessionUpdate(BaseModel):
    conference_id: str
    id: str
    name: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    description: str | None = None
    date: Date | None = Field(default=None, description="Date format: YYYY-MM-DD")
    location: str | None = None
    session_image_url: str | None = None
    speakers: list[str] | None = None
    tags: list[str] | None = None
    status: str | None = None

    @field_validator('conference_id','id')
    def conference_id_and_id_validation(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        return v

    @field_validator('name','description','location','session_image_url')
    def values_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_length = 2048 if info.field_name == "description" else 256
            if len(v) > max_length:
                raise ValueError(f"{info.field_name} cannot be longer than {max_length} characters")
        return v
    
    @field_validator('speakers','tags')
    def speakers_and_tags_validation(cls, v:list, info: ValidationInfo):
        if v is not None:
            if len(v) == 0 or (len(v) == 1 and v[0].strip() == ""):
                return None
            for val in v:
                if val is None or val.strip() == "":
                    raise ValueError(f"{info.field_name} cannot be empty")
                if len(val) > 256:
                    raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v  
    
    @field_validator("status")
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(session.SessionEnum.__members__):
                raise ValueError("Invalid status")
        return v
    
    @field_validator('session_image_url')
    def session_image_url_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v
    
    class Config:
        orm_mode = True

class Session(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    start_time: time
    end_time: time
    description: str 
    date: Date = Field(..., description="Date format: YYYY-MM-DD")
    location: str
    session_image_url: str | None = None
    tags: list[str]
    status: str