from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from typing import Optional, Any

class SpeakerBase(BaseModel):
    conference_id: str
    name: str
    title: str
    bio: str
    profile_image_url: str = "None"

    @validator('conference_id')
    def validate_conference_id(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid conference id")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Conference id too long")
        return v

    @validator('name')
    def validate_name(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v

    @validator('bio')
    def validate_bio(cls, bio):
        if bio is None or bio.strip() == "" or bio == "string":
            raise HTTPException(status_code=400, detail="Invalid bio")
        elif len(bio) > 2000:
            raise HTTPException(status_code=400, detail="Bio too long")
        return bio
    
    @validator('title')
    def validate_title(cls, title):
        if title is None or title.strip() == "" or title == "string":
            raise HTTPException(status_code=400, detail="Invalid title")
        elif len(title) > 256:
            raise HTTPException(status_code=400, detail="Title too long")
        return title
    
    @validator('profile_image_url')
    def validate_profile_image_url(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid profile image url")
            elif len(v) > 256:
                raise HTTPException(status_code=400, detail="Profile image url too long")
        return v


class SpeakerCreate(SpeakerBase):
    pass

class SpeakerUpdate(BaseModel):
    id: str
    conference_id: str | None = None
    name: str | None = None
    title: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None

    @validator('id')
    def validate_id(cls, v):
        if v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid id")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Id too long")
        return v

    @validator('conference_id')
    def validate_conference_id(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid conference id")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Conference id too long")
        return v

    @validator('name')
    def validate_name(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('title')
    def validate_title(cls, title):
        if title is None or title.strip() == "" or title == "string":
            raise HTTPException(status_code=400, detail="Invalid title")
        elif len(title) > 256:
            raise HTTPException(status_code=400, detail="Title too long")
        return title
    
    @validator('bio')
    def validate_bio(cls, bio):
        if bio is None or bio.strip() == "" or bio == "string":
            raise HTTPException(status_code=400, detail="Invalid bio")
        elif len(bio) > 2000:
            raise HTTPException(status_code=400, detail="Bio too long")
        return bio
    
    @validator('profile_image_url')
    def validate_profile_image_url(cls, v):
        if v is not None and len(v) > 256:
            raise HTTPException(status_code=400, detail="Profile image url too long")
        return v

class Speaker(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    title: str
    bio: str
    profile_image_url: str = "None"

    class Config:
        orm_mode = True

    @validator('name')
    def validate_name(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v

    @validator('bio')
    def validate_bio(cls, bio):
        if bio is None or bio.strip() == "" or bio == "string":
            raise HTTPException(status_code=400, detail="Invalid bio")
        elif len(bio) > 2000:
            raise HTTPException(status_code=400, detail="Bio too long")
        return bio
    
    @validator('title')
    def validate_title(cls, title):
        if title is None or title.strip() == "" or title == "string":
            raise HTTPException(status_code=400, detail="Invalid title")
        elif len(title) > 256:
            raise HTTPException(status_code=400, detail="Title too long")
        return title
    
    @validator('profile_image_url')
    def validate_profile_image_url(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid profile image url")
            elif len(v) > 256:
                raise HTTPException(status_code=400, detail="Profile image url too long")
        return v