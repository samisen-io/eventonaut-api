from pydantic import BaseModel, Field

class SignupOrganizerAdminRequest(BaseModel):
    email: str
    organization_name: str
    first_name: str | None = None
    last_name: str | None = None
    timezone: str | None = None
    profile_image_url: str | None = None
    
class SignupOrganizerUserRequest(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None
    timezone: str | None = None
    profile_image_url: str | None = None

class SignupOrganizerResponse(BaseModel):
    uuid: str = Field(serialization_alias="id")
    email: str
    first_name: str | None = None
    last_name: str | None = None
    timezone: str | None = None
    profile_image_url: str | None = None
    organization_name: str
    status: str
    organization_id: str
    list_of_roles: list[str]