from pydantic import BaseModel, Field
import requests
from pydantic import BaseModel, Field, validator

class BackdropGalleryBase(BaseModel):
    backdrop_url: str = Field(..., max_length=256)

    @validator('backdrop_url')
    def url_must_be_reachable(cls, v):
        try:
            response = requests.get(v)
            response.raise_for_status()
        except (requests.exceptions.RequestException, ValueError):
            raise ValueError('Invalid URL or the URL is not reachable')

        if not any(ext in v for ext in ['.jpeg', '.jpg', '.png']):
            raise ValueError('URL must point to a .jpeg, .jpg, or .png image')

        return v

    class Config:
        orm_mode = True

class BackdropGalleryCreate(BackdropGalleryBase):
    conference_id: str

class BackdropGalleryResponse(BackdropGalleryBase):
    conference_id: str
    uuid: str = Field(serialization_alias="id")

class BackdropGalleryUpdate(BackdropGalleryBase):
    id: str

class BackdropGalleryUpdateResponse(BackdropGalleryBase):
    uuid: str = Field(serialization_alias="id")