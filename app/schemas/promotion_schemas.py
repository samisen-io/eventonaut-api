from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import date
from ..url_validator import check_url
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import date
from ..url_validator import check_url

class PromotionBase(BaseModel):
    todate: date
    fromdate: date
    image_url: str | None = None
    promotion_name: str
    rank: int = Field(gt=0, lt=6)

class PromotionCreate(PromotionBase):
    conference_id: str

    @field_validator('promotion_name')
    def check_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        return v

    @field_validator('image_url')
    def validate_url(cls, v, info: ValidationInfo):
        if v is not None:
            if v == "":
                return None
            elif not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v

class PromotionUpdate(PromotionBase):
    id: str
    conference_id: str | None = None
    todate: date | None = None
    fromdate: date | None = None
    image_url: str | None = None
    promotion_name: str | None = None
    rank: int = Field(gt=0, lt=6, default=0)

    @field_validator('promotion_name','image_url')
    def check_empty(cls, v, info: ValidationInfo):
        if v is not None and v.strip() == "":
            return None
        return v

    @field_validator('image_url')
    def validate_url(cls, v, info: ValidationInfo):
        if v is not None:
            if v == "":
                return None
            elif not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v

class Promotion(BaseModel):
    uuid: str = Field(serialization_alias='id')
    location: str
    event_id: str = Field(serialization_alias='conference_id')
    conference_start_date: date
    conference_end_date: date
    todate: date
    fromdate: date
    image_url: str | None
    promotion_name: str
    conference_name: str
    conference_image_url: str | None
    rank: int = Field(gt=0, lt=6)
    
    class Config:
        orm_mode = True