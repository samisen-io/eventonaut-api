from pydantic import BaseModel, validator, Field, field_validator, ValidationInfo
from ..url_validator import check_url

class SpeakerBase(BaseModel):
    name: str
    email: str
    title: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None

    @field_validator('name','email')
    def validate_fields(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('title','bio')
    def validate_optional_fields(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_length = 2048 if info.field_name == "bio" else 256
            if len(v) > max_length:
                raise ValueError(f"{info.field_name} cannot be longer than {max_length} characters")
        return v
    
    @field_validator('profile_image_url')
    def validate_profile_image_url(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
            if v is not None:
                try:
                    if not check_url(v):
                        raise ValueError(f"Broken {info.field_name} link or invalid url")
                except Exception as e:
                    raise ValueError(f"Broken {info.field_name} link or invalid url - {str(e)}")
        return v

class SpeakerCreate(SpeakerBase):
    sessions: list[str] | None = None
    
    @field_validator('sessions')
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

class SpeakerUpdate(BaseModel):
    id: str
    name: str | None = None
    title: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None
    sessions: list[str] | None = None

    @validator('id')
    def validate_id(cls, v):
        if v.strip() == "":
            raise ValueError("Id cannot be empty")
        elif len(v) > 256:
            raise ValueError("Id cannot be longer than 256 characters")
        return v

    @field_validator('name','title','bio','profile_image_url')
    def validate_update(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_length = 2048 if info.field_name == "bio" else 256
            if len(v) > max_length:
                raise ValueError(f"{info.field_name} cannot be longer than {max_length} characters")
        return v
    
    @field_validator('profile_image_url')
    def validate_profile_image_url(cls, v, info: ValidationInfo):
        if v is not None:
            try:
                if not check_url(v):
                    raise ValueError(f"Broken {info.field_name} link or invalid url")
            except Exception as e:
                raise ValueError(f"Broken {info.field_name} link or invalid url - {str(e)}")
        return v
    
    @field_validator('sessions')
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

class Speaker(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    email: str
    title: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None