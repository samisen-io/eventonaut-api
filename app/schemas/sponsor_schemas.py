from pydantic import BaseModel, Field, field_validator, ValidationInfo
from ..url_validator import check_url

class SponsorBase(BaseModel):
    email: str
    name: str
    description: str
    contact_name: str
    contact_phone: str
    logo_image_url: str
    sponsorship_level: str

    @field_validator('email','name','description','contact_name','logo_image_url','sponsorship_level')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif v == 'string':
            raise ValueError(f"Invalid {info.field_name}")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v

    @field_validator('contact_phone')
    def check_phone_number(cls, v: str, info: ValidationInfo):
        if not 10 <= len(v) <= 15 :
            raise ValueError(f"Invalid {info.field_name}")
        return v
    
    @field_validator('logo_image_url')
    def validate_url(cls, v, info: ValidationInfo):
        if not check_url(v):
            raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v

class SponsorCreate(SponsorBase):
    pass

class SponsorUpdate(BaseModel):
    id: str
    name: str | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    logo_image_url: str | None = None
    sponsorship_level: str | None = None

    @field_validator('id')
    def check_id(cls, v, info: ValidationInfo):
        if v == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
        
    @field_validator('contact_phone')
    def check_phone_number(cls, v: str, info: ValidationInfo):
        if v is not None:
            if v == "":
                return None
            elif not 10 <= len(v) <= 15 :
                raise ValueError(f"Invalid {info.field_name}")
        return v
        
    @field_validator('name','description','contact_name','logo_image_url','sponsorship_level')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v is not None:
            if v == "":
                return None
            elif len(v) > 256:
                raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('logo_image_url')
    def validate_url(cls, v, info: ValidationInfo):
        if v is not None:
            if not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v
            
class Sponsor(SponsorBase):
    uuid: str = Field(serialization_alias='id')

    class Config:
        orm_mode = True