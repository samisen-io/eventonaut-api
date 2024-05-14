from pydantic import BaseModel, Field, field_validator, ValidationInfo

class OrganizationBase(BaseModel):
    name: str
    business_type: str | None = None
    description: str | None = None
    address: str | None = None
    logo_image_url: str | None = None
    website_url: str | None = None
    external_id: str | None = None

    @field_validator('name')
    @classmethod
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} should be less than 256 characters")
        return v

    @field_validator('description', 'address', 'logo_image_url', 'website_url', 'external_id')
    @classmethod
    def optional_field_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            if len(v) > 256:
                raise ValueError(f"{info.field_name} should be less than 256 characters")
        return v

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    id: str
    name: str | None = None
    business_type: str | None = None
    description: str | None = None
    address: str | None = None
    logo_image_url: str | None = None
    website_url: str | None = None
    external_id: str | None = None

    @field_validator('name', 'business_type', 'description', 'address', 'logo_image_url', 'website_url', 'external_id')
    @classmethod
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            if len(v) > 256:
                raise ValueError(f"{info.field_name} should be less than 256 characters")
        return v

class Organization(BaseModel):
    uuid: str = Field(serialization_alias='id')
    name: str
    business_type: str
    description: str | None = None
    address: str | None = None
    contact_email: str
    contact_phone: str | None = None
    logo_image_url: str | None = None
    website_url: str | None = None
    external_id: str | None = None
    is_archived: bool

    class Config:
        orm_mode = True
        
class OrganizationSecurity(Organization):
    id: int