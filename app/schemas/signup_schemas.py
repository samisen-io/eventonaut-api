from pydantic import BaseModel, Field, field_validator, ValidationInfo
from ..static_enums.role import RoleEnum
import logging

class SignupOrganizerAdminRequest(BaseModel):
    email: str
    organization_name: str
    first_name: str | None = None
    last_name: str | None = None
    timezone: str | None = None
    profile_image_url: str | None = None
    
    @field_validator("email", "organization_name")
    def check_email_organization_name(cls, value, info: ValidationInfo):
        if value.strip() == "":
            logging.error(f"Invalid {info.field_name}: {value}")
            raise ValueError(f"Invalid {info.field_name}: {value}")
        return value
    
class SignupOrganizerUserRequest(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None
    user_role: str
    timezone: str | None = None
    profile_image_url: str | None = None
    
    @field_validator("email")
    def check_email(cls, value):
        if value.strip() == "":
            logging.error(f"Invalid email: {value}")
            raise ValueError(f"Invalid email: {value}")
        return value
    
    @field_validator("user_role")
    def check_user_role(cls, value):
        value = value.upper()
        allowed_roles = [RoleEnum.ORGANIZATION_USER.name, RoleEnum.REGISTRATION_STAFF.name, RoleEnum.ORGANIZATION_ADMIN.name]
        if value not in allowed_roles:
            logging.error(f"Invalid user_role: {value}")
            raise ValueError(f"Invalid user_role: {value}")
        return value

class SignupResponseBase(BaseModel):
    uuid: str = Field(serialization_alias="id")
    db_id: int
    email: str
    first_name: str | None = None
    last_name: str | None = None
    timezone: str | None = None
    profile_image_url: str | None = None
    organization_name: str
    status: str
    organization_id: str
    list_of_roles: list[str]
    is_verified: bool
    
class SignupOrganizerResponse(BaseModel):
    uuid: str = Field(serialization_alias="id")
    user: SignupResponseBase