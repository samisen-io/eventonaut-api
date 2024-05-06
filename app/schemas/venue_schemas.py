from pydantic import BaseModel, Field, field_validator, ValidationInfo

class VenuBase(BaseModel):
    name: str
    location: str
    address: str | None = None
    geo_location: str | None = None

    @field_validator('name','location')
    def check_empty(cls, v: str, info: ValidationInfo):
        if v.strip() == '':
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v
    
    @field_validator('geo_location', 'address')
    def check_geo_location(cls, v: str, info: ValidationInfo):
        if v is not None:
            if v.strip() == '':
                return None
            elif len(v) > 256:
                raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v

class VenueCreate(VenuBase):
    pass

class VenueUpdate(VenuBase):
    id: str
    name: str | None = None
    location: str | None = None
    address: str | None = None

    @field_validator('id')
    def check_id(cls, v: str, info: ValidationInfo):
        if v.strip() == '':
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v

    @field_validator('name','location','address')
    def check_empty(cls, v: str, info: ValidationInfo):
        if v is not None:
            if v.strip() == '':
                return None
            elif len(v) > 256:
                raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v
    
class VenueResponse(BaseModel):
    uuid: str = Field(serialization_alias='id')
    name: str
    location: str
    address: str | None = None
    geo_location: str | None = None
    
    class Config:
        orm_mode = True