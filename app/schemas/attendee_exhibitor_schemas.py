from pydantic import BaseModel, field_validator, Field
import logging
from ..schemas.exhibitor_schemas import ExhibitorResponse

class AttendeeExhibitorCreate(BaseModel):
    conference_id: str
    exhibitor_ids: list[str] | None = None
    
    @field_validator("conference_id")
    def check_conference_id(cls, v):
        if v.strip() == "":
            logging.exception("Invalid conference_id")
            raise ValueError("Invalid conference_id")
        elif len(v) > 256:
            logging.exception("Invalid conference_id")
            raise ValueError("Invalid conference_id")
        return v
    
    @field_validator("exhibitor_ids")
    def check_exhibitor_ids(cls, v):
        if v is not None:
            if len(v) == 0 or (len(v) == 1 and v[0].strip() == ""):
                return
            for val in v:
                if val.strip() == "":
                    logging.exception("Invalid exhibitor_id")
                    raise ValueError("exhibitor_id cannot be empty")
                elif len(val) > 256:
                    logging.exception("Invalid exhibitor_id")
                    raise ValueError("exhibitor_ids cannot be longer than 256 characters")
        return v
    
class AttendeeExhibitorResponse(BaseModel):
    conference_id: str
    exhibitors: list[ExhibitorResponse]
    
    class Config:
        from_attributes = True