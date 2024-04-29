from pydantic import BaseModel, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status as statuscode
from ..static_enums.role import RoleEnum
import logging

class OTPBase(BaseModel):
    email: str
    role: str
    
    @field_validator('email')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} should be less than 256 characters")
            raise ValueError(f"{info.field_name} should be less than 256 characters")
        return v
    
    @field_validator('role')
    def check_role(cls, v):
        v = v.upper()
        if v not in list(RoleEnum.__members__):
            logging.exception("Invalid role")
            raise ValueError("Invalid role")
        return v
    
class SendOtp(OTPBase):
    email_subject: str
    
    @field_validator('email_subject')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} should be less than 256 characters")
            raise ValueError(f"{info.field_name} should be less than 256 characters")
        return v
    
class VerifyOtp(OTPBase):
    otp: str
    
    @field_validator('otp')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) != 6:
            logging.exception(f"{info.field_name} should be 6 characters long")
            raise ValueError(f"{info.field_name} should be 6 characters long")
        return v
    
class PasswordReset(OTPBase):
    password: str
    
    @field_validator('password')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "" or v.__contains__(" "):
            logging.exception(f"Invalid {info.field_name}")
            raise ValueError(f"Invalid {info.field_name}")
        if not 8 <= len(v) <= 16:
            logging.exception(f"{info.field_name} should be between 8 and 16 characters")
            raise ValueError(f"{info.field_name} should be between 8 and 16 characters")
        return v
    
class PasswordResetForAttendee(OTPBase):
    otp: str
    password: str
    
    @field_validator('password')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "" or v.__contains__(" "):
            logging.exception(f"Invalid {info.field_name}")
            raise ValueError(f"Invalid {info.field_name}")
        if not 8 <= len(v) <= 16:
            logging.exception(f"{info.field_name} should be between 8 and 16 characters")
            raise ValueError(f"{info.field_name} should be between 8 and 16 characters")
        return v
    
    @field_validator('otp')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) != 6:
            logging.exception(f"{info.field_name} should be 6 characters long")
            raise ValueError(f"{info.field_name} should be 6 characters long")
        return v