from pydantic import BaseModel

#item
class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

#user
class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True

#pydantic model for conference
class Conference(BaseModel):
    name: str
    location: str
    start_date: str
    end_date: str
    description: str | None = None

#pydantic model for conference create
class ConferenceCreate(Conference):
    pass