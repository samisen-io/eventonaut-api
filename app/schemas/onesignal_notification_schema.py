from pydantic import BaseModel, field_validator
from ..url_validator import check_url


class PushNotification(BaseModel):
    conference_id: str
    message: str
    title: str
    picture: str | None = None
    
    @field_validator('picture')
    def check_picture_url(cls, value):
        if not value or value.strip() == '':
            return None
        if not check_url(value):
            raise ValueError("Invalid URL")