from app.schemas.speaker_schemas import Speaker
from app.schemas.session_schemas import Session

class SessionResponse(Session):
    speakers: list[Speaker] | None

    class Config:
        orm_mode = True
        
class SpeakerResponse(Speaker):
    sessions: list[Session] | None = None

    class Config:
        orm_mode = True