from pydantic import BaseModel, validator, Field, field_validator, ValidationInfo
from fastapi import HTTPException

class SpeakerBase(BaseModel):
    name: str
    title: str
    bio: str
    profile_image_url: str | None = None

    @validator('name')
    def validate_name(cls, v):
        if v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v

    @validator('bio')
    def validate_bio(cls, bio):
        if bio.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid bio")
        elif len(bio) > 2048:
            raise HTTPException(status_code=400, detail="Bio too long")
        return bio
    
    @validator('title')
    def validate_title(cls, title):
        if title.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid title")
        elif len(title) > 256:
            raise HTTPException(status_code=400, detail="Title too long")
        return title
    
    @validator('profile_image_url')
    def validate_profile_image_url(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise HTTPException(status_code=400, detail="Profile image url too long")
        return v


class SpeakerCreate(SpeakerBase):
    conference_id: str

    @validator('conference_id')
    def validate_conference_id(cls, v):
        if v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid conference id")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Conference id too long")
        return v

class SpeakerUpdate(BaseModel):
    id: str
    conference_id: str | None = None
    name: str | None = None
    title: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None

    @validator('id')
    def validate_id(cls, v):
        if v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid id")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Id too long")
        return v

    @field_validator('conference_id','name','title','bio','profile_image_url')
    def validate_update(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_length = 2048 if info.field_name == "bio" else 256
            if len(v) > max_length:
                raise HTTPException(status_code=400, detail=f"{info.field_name} must be less than {max_length} characters")
        return v

class Speaker(SpeakerBase):
    uuid: str = Field(serialization_alias="id")

    class Config:
        orm_mode = True