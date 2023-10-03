from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    conferences: List["Conference"] = []

    class Config:
        orm_mode = True


class ConferenceBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime


class ConferenceCreate(ConferenceBase):
    pass


class Conference(ConferenceBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True