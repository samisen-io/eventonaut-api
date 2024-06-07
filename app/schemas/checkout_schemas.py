from pydantic import BaseModel, ValidationInfo, field_validator
from datetime import datetime

class Ticket(BaseModel):
    id: str
    count: int
    
    @field_validator('id')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        return v
    
    @field_validator('count')
    def value_not_negative(cls, v, info: ValidationInfo):
        if v < 0:
            raise ValueError(f"{info.field_name} cannot be negative")
        return v
    
class CheckoutRequest(BaseModel):
    event_id: str
    tickets: list[Ticket]
    
    @field_validator('event_id')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        return v
    
class CheckoutResponse(BaseModel):
    session_id: str
    expiration_timestamp: datetime
    
class Details(BaseModel):
    event_id: str
    session_id: str
    first_name: str
    last_name: str
    email: str
    
    @field_validator('event_id', 'session_id', 'first_name', 'last_name', 'email')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 255:
            raise ValueError(f"{info.field_name} cannot be more than 255 characters")
        return v