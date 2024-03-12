from pydantic import BaseModel, Field

class EventDocumentResponse(BaseModel):
    uuid: str = Field(serialization_alias="id")
    conference_uuid: str = Field(serialization_alias="conference_id")
    document_url: str = Field(serialization_alias="url")