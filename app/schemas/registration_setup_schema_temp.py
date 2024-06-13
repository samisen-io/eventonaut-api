from datetime import datetime
from pydantic import BaseModel, Field, ValidationInfo, field_validator

class RegistrationSetupBaseTemp(BaseModel):
    event_id: int
    end_date: datetime
    registration_note: str | None = None
    tax_name: str | None = None
    tax_rate: float | None = None
    fee_name: str | None = None
    fee_amount: float | None = None
    refund_policy: str | None = None
    is_live: bool
    start_date: datetime
    
class RegistrationSetupCreateTemp(RegistrationSetupBaseTemp):
    pass

class RegistrationSetupUpdateTemp(RegistrationSetupBaseTemp):
    uuid: str = Field(serialization_alias='id')
    
    class Config:
        orm_mode = True
    
    