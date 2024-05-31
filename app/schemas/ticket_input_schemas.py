from pydantic import BaseModel
from datetime import date, time

class TicketInput(BaseModel):
    title: str
    event: str
    order_number: str
    logo: str
    ticket_type: str
    address: str
    date_time: str
    order_type: str
    customer_name: str
    order_date: date
    order_time: time
    