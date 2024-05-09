from pydantic import BaseModel, Field

class ExhibitorDocumentResponse(BaseModel):
    uuid: str = Field(serialization_alias="id")
    exhibitor_uuid: str = Field(serialization_alias="exhibitor_id")
    document_url: str = Field(serialization_alias="url")
    name: str
    content_type: str
    size: str
    
class ExhibitorDocumentRequest(BaseModel):
    exhibitor_id: int
    file_url: str
    original_file_name: str
    content_type: str
    size: float