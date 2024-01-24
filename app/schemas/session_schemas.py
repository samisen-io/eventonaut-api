from pydantic import BaseModel, validator, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status
from datetime import date as Date, time
import logging

class SessionBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    description: str 
    date: Date
    location: str
    session_image_url: str | None = None
    speakers: list[str]
    tags: list[str]

    @field_validator('name','description','location')
    def values_validation(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        max_length = 2048 if info.field_name == "description" else 256
        if len(v) > max_length:
            logging.exception(f"{info.field_name} cannot be longer than {max_length} characters")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than {max_length} characters")
        return v

    @field_validator('session_image_url')
    def session_image_url_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                logging.exception(f"{info.field_name} cannot be longer than 256 characters")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than 256 characters") 
        return v
    
    @field_validator('speakers','tags')
    def speakers_and_tags_validation(cls, v, info: ValidationInfo):
        if len(v) == 0:
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{info.field_name} cannot be empty")
        for val in v:
            if val.strip() == "":
                logging.exception(f"{info.field_name} cannot be empty")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"{info.field_name} cannot be empty")
            elif len(val) > 256:
                logging.exception(f"{info.field_name} cannot be longer than 256 characters")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than 256 characters") 
        return v

class SessionCreate(SessionBase):
    conference_id: str
    
    @field_validator('conference_id')
    def conference_id_must_not_be_empty(cls, v):
        if v.strip() == "":
            logging.exception(f"conferece_id cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"conference_id cannot be empty")
        return v
    
class SessionUpdate(BaseModel):
    conference_id: str
    id: str
    name: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    description: str | None = None
    date: Date | None = None
    location: str | None = None
    session_image_url: str | None = None
    speakers: list[str] | None = None
    tags: list[str] | None = None

    @field_validator('conference_id','id')
    def conference_id_and_id_validation(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        return v

    @field_validator('name','description','location','session_image_url')
    def values_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_length = 2048 if info.field_name == "description" else 256
            if len(v) > max_length:
                logging.exception(f"{info.field_name} cannot be longer than {max_length} characters")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than {max_length} characters")
        return v
    
    @field_validator('speakers','tags')
    def speakers_and_tags_validation(cls, v:list, info: ValidationInfo):
        if v is not None:
            if len(v) == 0:
                return None
            for val in v:
                if v is None:
                    logging.exception(f"{info.field_name} cannot be empty")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
                if len(val) > 256:
                    logging.exception(f"{info.field_name} cannot be longer than 256 characters")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than 256 characters") 
        return v  
    class Config:
        orm_mode = True

class Session(SessionBase):
    uuid: str = Field(serialization_alias="id")
    class Config:
        orm_mode = True