from pydantic import BaseModel, Field

class QueryInput(BaseModel):
    question: str = Field(..., description="The question to be asked")
    conference_id: str = Field(..., description="The conference ID")
    
class QueryInputStream(BaseModel):
    question: str = Field(..., description="The question to be asked")
    conference_id: str = Field(..., description="The conference ID")
    session_id: str = Field(..., description="The chat session ID")