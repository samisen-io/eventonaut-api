from pydantic import BaseModel, field_validator, ValidationInfo
import logging
from ..schemas.attendee_schemas import Attendee

class TicketCheckIn(BaseModel):
    ticket_id: str
    event_id: str
    
    @field_validator('ticket_id','event_id')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        return v
    
class Ticket(BaseModel):
    ticket_id: str
    type: str
    event_id: str
    checked_in: bool
    
class CheckInResponse(BaseModel):
    message: str
    ticket: Ticket
    
class AttendeeTickets(Attendee):
    tickets: list[Ticket]