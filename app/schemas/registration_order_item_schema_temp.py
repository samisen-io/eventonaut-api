from pydantic import BaseModel, Field, field_validator

class RegistrationOrderItemBase(BaseModel):
    registration_order_id: int
    description: str | None = None
    quantity: int
    unit_price: float
    total_amount: float
    type: int
    code: str
    
    @field_validator("registration_order_id")
    def check_registration_order_id(cls, v):
        if v < 0:
            raise ValueError("Invalid registration_order_id")
        return v
    
    @field_validator("description")
    def check_description(cls, v):
        if v is not None:
            if v.strip() == "":
                raise ValueError("Invalid description")
            elif len(v) > 256:
                raise ValueError("Invalid description")
        return v
    
    @field_validator("quantity")
    def check_quantity(cls, v):
        if v < 0:
            raise ValueError("Invalid quantity")
        return v
    
    @field_validator("unit_price")
    def check_unit_price(cls, v):
        if v < 0:
            raise ValueError("Invalid unit_price")
        return v
    
    @field_validator("total_amount")
    def check_total_amount(cls, v):
        if v < 0:
            raise ValueError("Invalid total_amount")
        return v
    
    @field_validator("type")
    def check_type(cls, v):
        if v < 0 or v >= 4:
            raise ValueError("Invalid type")
        return v
    
    @field_validator("code")
    def check_code(cls, v):
        if v is not None:
            if v.strip() == "":
                raise ValueError("Invalid code")
        return v
        
class RegistrationOrderItemCreate(RegistrationOrderItemBase):
    pass

class RegistrationOrderItem(RegistrationOrderItemBase):
    uuid: str = Field(serialization_alias="id")

    class Config:
        orm_mode = True

    
