from datetime import datetime
from pydantic import BaseModel, Field, ValidationInfo, field_validator


class RegistrationSetupItemBaseTemp(BaseModel):
    name: str
    description: str
    registration_setup_id: int
    price: float
    available_from: datetime
    available_to: datetime
    image_url: str | None = None
    product_id: str | None = None
    total_quantity: int
    
class RegistrationSetupItemCreateTemp(RegistrationSetupItemBaseTemp):
    pass

    class Config:
        orm_mode = True
    
    
class RegistrationSetupItemTemp(RegistrationSetupItemBaseTemp):
    available_quantity: int
    uuid: str = Field(serialization_alias="id")
    
    @field_validator('name', 'description')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 255:
            raise ValueError(f"{info.field_name} cannot be more than 255 characters")
        return v
    
    class Config:
        orm_mode = True
        
class RegistrationSetupItemUpdateTemp(BaseModel):
    uuid: str = Field(serialization_alias="id")
    available_quantity: int | None = None
    name: str | None = None
    description: str | None = None
    registration_setup_id: int | None = None
    price: float | None = None
    available_from: datetime | None = None
    available_to: datetime | None = None
    image_url: str | None = None
    product_id: str | None = None
    
    @field_validator('name', 'description')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                raise ValueError(f"{info.field_name} cannot be empty")
            elif len(v) > 255:
                raise ValueError(f"{info.field_name} cannot be more than 255 characters")
        return v
    
    class Config:
        orm_mode = True