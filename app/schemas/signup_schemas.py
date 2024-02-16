from pydantic import BaseModel

class SignupUserBase(BaseModel):
    email: str
    organization_name: str

class SignupOrganizerRequest(SignupUserBase):
    email: str
    password: str
    organization_name: str
    
class SignupOrganizerResponse(SignupUserBase):
    email: str
    organization_name: str
    status: str
    organization_id: str
    user_id: str
    list_of_roles: list[str]