from pydantic import BaseModel, Field, validator
from ..url_validator import check_url

class BackdropGalleryBase(BaseModel):
    backdrop_url: str = Field(..., max_length=256)

    @validator('backdrop_url')
    def url_must_be_reachable(cls, v):
        if v == "":
            raise ValueError('URL cannot be empty')
        
        if v is not None:
            try:
                if not check_url(v):
                    raise ValueError(f"Broken backdrop_url link or invalid url")
            except Exception as e:
                raise ValueError(f"Broken backdrop_url link or invalid url - {str(e)}")

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
    name: str
    size: float
class BackdropGalleryUpdate(BackdropGalleryBase):
    id: str

class BackdropGalleryUpdateResponse(BackdropGalleryBase):
    uuid: str = Field(serialization_alias="id")
    name: str
    size: float