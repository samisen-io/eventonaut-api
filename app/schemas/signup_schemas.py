from pydantic import BaseModel

class SignupOrganizer(BaseModel):
    email: str
    password: str
    organization_name: str
    