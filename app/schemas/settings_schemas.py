from pydantic import BaseModel

#pydantic model for settings
class SettingsCreate(BaseModel):
    body: dict

#pydantic model for settings
class Settings(SettingsCreate):
    id: int
    conference_id: int
    owner_id: int
    class Config:
        orm_mode = True