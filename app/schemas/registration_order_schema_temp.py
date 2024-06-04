from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class RegistrationOrderBase(BaseModel):
    event_id: int
    attendee_id: int
    amount: float
    tax_amount: float
    fee_amount: float
    

class RegistrationOrderCreate(RegistrationOrderBase):
    pass

class RegistrationOrder(RegistrationOrderBase):
    uuid: str = Field(serialization_alias="id")
    total_amount: float
    order_id: str
    
    class Config:
        orm_mode = True