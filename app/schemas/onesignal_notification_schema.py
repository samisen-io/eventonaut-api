from pydantic import BaseModel


class PushNotification(BaseModel):
    conference_id: str
    message: str
    title: str
    picture: str | None = None
    