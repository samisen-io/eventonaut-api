from pydantic import BaseModel, Field, field_validator

class CreateTicket(BaseModel):
    event_id: int
    amount: float
    tax_amount: float
    fee_amount: float
    order_id: str
    description: str
    quantity: int
    type: int