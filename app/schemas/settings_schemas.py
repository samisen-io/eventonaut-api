from pydantic import BaseModel

#pydantic model for settings
class SettingsBase(BaseModel):
    body: dict

class SettingsCreate(SettingsBase):
    conference_uuid: str

#pydantic model for settings
class Settings(SettingsBase):
    uuid: str
    conference_id: int
    owner_id: int
    class Config:
        orm_mode = True