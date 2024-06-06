from pydantic import BaseModel

class Ticket(BaseModel):
    name: str
    count: int

class TicketSession(BaseModel):
    event_id: int
    attendee_id: int
    tickets: list[Ticket]