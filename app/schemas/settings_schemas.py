from pydantic import BaseModel

#pydantic model for settings
class SettingsCreate(BaseModel):
    conference_id: int
    body: dict

#pydantic model for settings
class Settings(SettingsCreate):
    id: int
    owner_id: int
    class Config:
        orm_mode = True