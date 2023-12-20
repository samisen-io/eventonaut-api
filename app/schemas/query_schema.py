from pydantic import BaseModel, Field

class QueryInput(BaseModel):
    question: str = Field(..., description="The question to be asked")
    conference_id: str = Field(..., description="The conference ID")