from pydantic import BaseModel, Field

class SessionDocumentResponse(BaseModel):
    uuid: str = Field(serialization_alias="id")
    session_uuid: str = Field(serialization_alias="session_id")
    document_url: str = Field(serialization_alias="url")