from pydantic import BaseModel, Field, ValidationInfo, field_validator
from datetime import datetime, date

class RegistrationSetupBase(BaseModel):
    start_date: date
    end_date: date
    registration_note: str
    tax_name: str
    tax_rate: float
    fee_name: str
    fee_amount: float
    refund_policy: str
    is_live: bool
    
class RegistrationSetup(RegistrationSetupBase):
    
    @field_validator('tax_name', 'fee_name', 'refund_policy')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 255:
            raise ValueError(f"{info.field_name} cannot be more than 255 characters")
        return v
    
class RegistrationSetupItemBase(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    description: str
    available_quantity: int
    price: float
    available_from: datetime
    available_to: datetime
    image_url: str | None = None
    product_id: str | None = None
    
class RegistrationSetupItem(RegistrationSetupItemBase):
    
    @field_validator('name', 'description')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 255:
            raise ValueError(f"{info.field_name} cannot be more than 255 characters")
        return v
    
class RegistrationSetupResponse(RegistrationSetupBase):
    registration_setup_items: list[RegistrationSetupItemBase] = Field(serialization_alias="tickets")