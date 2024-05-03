from pydantic import BaseModel, Field, field_validator, ValidationInfo

class OrganizationSettingsBase(BaseModel):
    event_brite_access_token: str
    
    @field_validator('event_brite_access_token')
    @classmethod
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} should be less than 256 characters")
        return v
    
class OrganizationSettingsCreate(OrganizationSettingsBase):
    pass

class OrganizationSettingsUpdate(BaseModel):
    event_brite_access_token: str | None = None
    
    @field_validator('event_brite_access_token')
    @classmethod
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            if len(v) > 256:
                raise ValueError(f"{info.field_name} should be less than 256 characters")
        return v
    
class OrganizationSettings(BaseModel):
    uuid: str = Field(serialization_alias='id')
    organization_id: str
    event_brite_org_id: str
    event_brite_access_token: str
    
    class Config:
        orm_mode = True