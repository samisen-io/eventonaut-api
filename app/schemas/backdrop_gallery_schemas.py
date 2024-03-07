from pydantic import BaseModel, Field

class BackdropGalleryBase(BaseModel):
    backdrop_url: str = Field(..., max_length=256)

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