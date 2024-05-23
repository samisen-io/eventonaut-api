from pydantic import BaseModel, Field, field_validator, ValidationInfo

class TemplateResponse(BaseModel):
    uuid: str = Field(serialization_alias="id")
    template_name: str
    template_url: str