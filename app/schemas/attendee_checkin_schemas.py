from pydantic import BaseModel, field_validator, ValidationInfo
import logging

class AttendeeCheckin(BaseModel):
    ticket_id: str
    event_id: str
    
    @field_validator('ticket_id','event_id')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        return v