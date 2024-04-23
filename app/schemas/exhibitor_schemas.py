from pydantic import BaseModel, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status

class ExhibitorBase(BaseModel):
    name: str
    address: str
    about: str
    contact_name: str
    contact_phone: str
    contact_email: str
    booth_number: str
    category: str
    exhibitor_logo: str | None = None
    exhibitor_banner: str | None = None