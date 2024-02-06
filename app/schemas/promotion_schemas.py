from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import date
from fastapi import HTTPException, status
import logging

class PromotionBase(BaseModel):
    todate: date
    fromdate: date
    image_url: str
    promotion_name: str
    rank: int = Field(gt=0, lt=6)
    
    @field_validator('promotion_name','image_url')
    def check_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        return v

class PromotionCreate(PromotionBase):
    conference_id: str

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

class Promotion(PromotionBase):
    uuid: str = Field(serialization_alias='id')
    location: str
    conference_id: str
    class Config:
        orm_mode = True