from pydantic import BaseModel, Field, field_validator, ValidationInfo
from ..url_validator import check_url

class SponsorBase(BaseModel):
    email: str
    name: str
    description: str | None = None
    contact_name: str
    contact_phone: str
    logo_image_url: str | None = None
    sponsorship_level: str

    @field_validator('email','name','contact_name','sponsorship_level')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('description','logo_image_url')
    def check_none(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
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
        if v is not None:
            try:
                if not check_url(v):
                    raise ValueError(f"Broken {info.field_name} link or invalid url")
            except Exception as e:
                raise ValueError(f"Broken {info.field_name} link or invalid url - {str(e)}")
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
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
        
    @field_validator('contact_phone')
    def check_phone_number(cls, v: str, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif not 10 <= len(v) <= 15 :
                raise ValueError(f"Invalid {info.field_name}")
        return v
        
    @field_validator('name','description','contact_name','logo_image_url','sponsorship_level')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('logo_image_url')
    def validate_url(cls, v, info: ValidationInfo):
        if v is not None:
            try:
                if not check_url(v):
                    raise ValueError(f"Broken {info.field_name} link or invalid url")
            except Exception as e:
                raise ValueError(f"Broken {info.field_name} link or invalid url - {str(e)}")
        return v

class Sponsor(BaseModel):
    email: str
    name: str
    description: str | None
    contact_name: str
    contact_phone: str
    logo_image_url: str | None
    sponsorship_level: str        
    
class SponsorResponse(Sponsor):
    uuid: str = Field(serialization_alias='id')
    
    class Config:
        orm_mode = True
        
class SponsorResponseWithConference(Sponsor):
    spn_uuid: str = Field(serialization_alias='id')
    
    class Config:
        orm_mode = True