from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator

from app.schemas.registration_order_schema_temp import RegistrationOrder
from app.schemas.registration_ticket_schema_temp import RegistrationTicket

class RegistrationOrderItemBase(BaseModel):
    registration_order_id: int
    description: str | None = None
    quantity: int
    unit_price: float
    total_amount: float
    registration_setup_item_id: int
    code: str
    
    @field_validator("registration_order_id")
    def check_registration_order_id(cls, v):
        if v < 0:
            raise ValueError("Invalid registration_order_id")
        return v
    
    @field_validator("description")
    def check_description(cls, v):
        if v is not None:
            if v.strip() == "":
                raise ValueError("Invalid description")
            elif len(v) > 256:
                raise ValueError("Invalid description")
        return v
    
    @field_validator("quantity")
    def check_quantity(cls, v):
        if v < 0:
            raise ValueError("Invalid quantity")
        return v
    
    @field_validator("unit_price")
    def check_unit_price(cls, v):
        if v < 0:
            raise ValueError("Invalid unit_price")
        return v
    
    @field_validator("total_amount")
    def check_total_amount(cls, v):
        if v < 0:
            raise ValueError("Invalid total_amount")
        return v
    
    @field_validator("registration_setup_item_id")
    def check_registration_setup_item_id(cls, v):
        if v < 0:
            raise ValueError("Invalid registration_setup_item_id")
        return v
    
    @field_validator("code")
    def check_code(cls, v):
        if v is not None:
            if v.strip() == "":
                raise ValueError("Invalid code")
        return v
        
class RegistrationOrderItemCreate(RegistrationOrderItemBase):
    pass

class RegistrationOrderItem(RegistrationOrderItemBase):
    uuid: str = Field(serialization_alias="id")

    class Config:
        orm_mode = True
        
class RegistrationOrderItemResponse(RegistrationOrderItem):
    registration_order: Optional[RegistrationOrder] = Field(None, alias="order")
    registration_ticket: Optional[List[RegistrationTicket]] = Field(None, alias="tickets")
    ticket_data: Optional[Any] = Field(None, alias="ticketData")
    event: Optional[Any] = Field(None, alias="event")

    class Config:
        orm_mode = True
        from_attributes = True    