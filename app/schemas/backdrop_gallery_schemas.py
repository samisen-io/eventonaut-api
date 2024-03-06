from pydantic import BaseModel, Field

class BackdropGalleryCreate(BaseModel):
    conference_id: str
    backdrop_url: str = Field(..., max_length=256)

    class Config:
        orm_mode = True
        
class BackdropGalleryResponse(BaseModel):
    conference_id: str
    backdrop_url: str = Field(..., max_length=256)
    uuid: str = Field(serialization_alias="id")

    class Config:
        orm_mode = True
        
class BackdropGalleryUpdate(BaseModel):
    backdrop_url: str = Field(..., max_length=256)
    uuid: str = Field(serialization_alias="id")
    
    class Config:
        orm_mode = True