from pydantic import BaseModel, Field

class EventDocumentResponse(BaseModel):
    uuid: str = Field(serialization_alias="id")
    conference_uuid: str = Field(serialization_alias="conference_id")
    document_url: str = Field(serialization_alias="url")
    name: str
    content_type: str
    size: str
    
class EventDocumentRequest(BaseModel):
    conference_id: int
    file_url: str
    name: str
    content_type: str
    size: float