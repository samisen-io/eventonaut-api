from pydantic import BaseModel, Field, field_validator, ValidationInfo

class PlanBase(BaseModel):
    plan_id: str
    plan_name: str
    
    @field_validator("plan_id", "plan_name")
    def check_plan(cls, v, info: ValidationInfo):
        if v.strip() == "":
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 255:
            raise ValueError(f"{info.field_name} cannot be more than 255 characters")
        return v
    
class PlanCreate(PlanBase):
    pass

class PlanUpdate(BaseModel):
    plan_id: str | None
    plan_name: str | None
    
    @field_validator("plan_id", "plan_name")
    def check_plan(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 255:
                raise ValueError(f"{info.field_name} cannot be more than 255 characters")
        return v

class Plan(BaseModel):
    uuid: str = Field(serialization_alias="id")
    plan_id: str
    plan_name: str
    
    class Config:
        orm_mode = True