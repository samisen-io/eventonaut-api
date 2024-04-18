from pydantic import BaseModel, Field

class SessionDocumentResponse(BaseModel):
    uuid: str = Field(serialization_alias="id")
    session_uuid: str = Field(serialization_alias="session_id")
    document_url: str = Field(serialization_alias="url")
    name: str
    content_type: str
    size: str
    
class SessionDocumentRequest(BaseModel):
    session_id: int
    document_url: str
    name: str
    content_type: str
    size: float