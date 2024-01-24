from pydantic import BaseModel, validator, Field
from fastapi import HTTPException

class ClientBase(BaseModel):
    name: str
    contact_name: str
    contact_email: str
    contact_phone: str
    address: str
    status: bool
    profile_image_url: str

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
        if v is None or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid profile image url")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Profile image url too long")
        return v

class ClientUpdate(BaseModel):
    id: str
    name: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    status: bool | None = None
    address: str | None = None
    profile_image_url: str | None = None

    @validator('id')
    def id_is_not_empty(cls, v):
        if v is None or v.strip() == "":
            return None
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Id too long")
        return v

    @validator('name')
    def name_is_not_empty(cls, v):
        if v is not None and v.strip() == "":
            return None
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('contact_name')
    def contact_name_is_not_empty(cls, v):
        if v is not None and v.strip() == "" :
            return None
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Contact name too long")
        return v
    
    @validator('contact_email')
    def contact_email_is_not_empty(cls, v):
        if v is not None and v.strip() == "":
            return None
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Contact email too long")
        return v
    
    @validator('contact_phone')
    def contact_phone_is_not_empty(cls, v):
        if v is not None and v.strip() == "":
            return None
        elif len(v) > 15:
            raise HTTPException(status_code=400, detail="Contact phone too long")
        return v
    
    @validator('address')
    def address_is_not_empty(cls, v):
        if v is not None and v.strip() == "":
            return None
        elif len(v) > 15:
            raise HTTPException(status_code=400, detail="Address too long")
        return v

    @validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v is not None and v.strip() == "":
            return None
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Profile image url too long")
        return v

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    uuid: str = Field(serialization_alias="id")

    class Config:
        orm_mode = True