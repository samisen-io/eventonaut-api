from pydantic import BaseModel, field_validator
from typing import Optional

class RegistrationTicketBase(BaseModel):
    registration_order_item_id: int
    checked_in: Optional[bool] = False
    ticket_url: Optional[str] = None
    
    @field_validator("registration_order_item_id")
    def check_registration_order_item_id(cls, v):
        if v < 0:
            raise ValueError("Invalid registration_order_item_id")
        return v
    
    @field_validator("checked_in")
    def check_checked_in(cls, v):
        if v is None:
            return False
        return v

class RegistrationTicketCreate(RegistrationTicketBase):
    pass

class RegistrationTicket(RegistrationTicketBase):
    ticket_id: str
    
    class Config:
        orm_mode = True