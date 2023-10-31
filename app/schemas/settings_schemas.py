from pydantic import BaseModel

#pydantic model for settings
class SettingsCreate(BaseModel):
    conference_id: str
    body: dict

#pydantic model for settings
class Settings(SettingsCreate):
    id: str
    owner_id: str
    class Config:
        orm_mode = True