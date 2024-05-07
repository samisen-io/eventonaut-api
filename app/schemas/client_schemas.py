from pydantic import BaseModel, field_validator, validator, Field, ValidationInfo
from ..static_enums import client
from ..url_validator import check_url

class ClientBase(BaseModel):
    name: str
    contact_name: str
    contact_email: str
    contact_phone: str
    address: str
    profile_image_url: str | None = None
    status: str

    @field_validator('name','contact_name','contact_email','address')
    def check_empty(cls, v: str, info: ValidationInfo):
        if v.strip() == '':
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v
    
    @field_validator('contact_phone')
    def contact_phone_is_not_empty(cls, v):
        if v.strip() == "":
            raise ValueError(f"Phone number cannot be empty")
        elif not 10 <= len(v) <= 15:
            raise ValueError(f"Invalid Phone Number")
        return v
    
    @field_validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise ValueError(f"Profile image url too long")
            if not check_url(v):
                raise ValueError("Broken profile image url link or invalid url")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(client.ClientEnum.__members__):
            raise ValueError("Invalid status")
        return v

class ClientUpdate(BaseModel):
    id: str
    name: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    status: str | None = None
    address: str | None = None
    profile_image_url: str | None = None

    @field_validator('id')
    def id_is_not_empty(cls, v, info: ValidationInfo):
        if v == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('contact_name', 'name', 'address', 'profile_image_url')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v is not None:
            if v == "":
                return None
            if len(v) > 256:
                raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('contact_phone')
    def contact_phone_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            elif not 10 <= len(v) <= 15:
                raise ValueError(f"Invalid Phone Number")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(client.ClientEnum.__members__):
                raise ValueError("Invalid status")
        return v

    @field_validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v is not None:
            if not check_url(v):
                raise ValueError("Broken profile image url link or invalid url")
        return v

class ClientCreate(ClientBase):
    pass

class ClientResponse(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    contact_name: str
    contact_email: str
    contact_phone: str
    address: str
    profile_image_url: str | None = None
    status: str

    class Config:
        orm_mode = True