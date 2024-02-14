from pydantic import BaseModel, field_validator, validator, Field, ValidationInfo
from fastapi import HTTPException, status
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

    @validator('name')
    def name_is_not_empty(cls, v):
        if v is None or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('contact_name')
    def contact_name_is_not_empty(cls, v):
        if v is None or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid contact name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Contact name too long")
        return v
    
    @validator('contact_email')
    def contact_email_is_not_empty(cls, v):
        if v is None or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid contact email")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Contact email too long")
        return v
    
    @validator('contact_phone')
    def contact_phone_is_not_empty(cls, v):
        if v is None or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid contact phone")
        elif len(v) > 15 or len(v) < 10:
            raise HTTPException(status_code=400, detail="Invalid Phone Number")
        return v
    
    @validator('address')
    def address_not_empty(cls, v):
        if v is None or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid address")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Address too long")
        return v
    
    @validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise HTTPException(status_code=400, detail="Profile image url too long")
            if not check_url(v):
                raise ValueError("Broken profile image url link or invalid url")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(client.ClientEnum.__members__):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v

class ClientUpdate(BaseModel):
    id: str
    name: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    status: str | None = None
    address: str | None = None
    profile_image_url: str | None = None

    @field_validator('id')
    def id_is_not_empty(cls, v, info: ValidationInfo):
        if v == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('contact_email', 'contact_name', 'name', 'address', 'profile_image_url')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v is not None:
            if v == "":
                return None
            if len(v) > 256:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('contact_phone')
    def contact_phone_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 15 or len(v) < 10:
                raise HTTPException(status_code=400, detail="Invalid Phone Number")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(client.ClientEnum.__members__):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v

    @field_validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v is not None:
            if not check_url(v):
                raise ValueError("Broken profile image url link or invalid url")
        return v

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    uuid: str = Field(serialization_alias="id")

    class Config:
        orm_mode = True