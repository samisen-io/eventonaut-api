from pydantic import BaseModel, Field, field_validator
from datetime import date
import uuid

class PromotionBase(BaseModel):
    todate: date
    fromdate: date
    image_url: str
    promotion_name: str
    rank: int = Field(gt=0, lt=6)

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

class Promotion(PromotionBase):
    uuid: str = Field(serialization_alias='id')
    location: str
    conference_id: str
    class Config:
        orm_mode = True