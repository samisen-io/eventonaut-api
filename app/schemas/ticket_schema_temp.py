from pydantic import BaseModel, Field, field_validator

class CreateTicket(BaseModel):
    event_id: str
    amount: float
    tax_amount: float
    fee_amount: float
    description: str
    quantity: int
    registration_setup_item_id: int
    code : str