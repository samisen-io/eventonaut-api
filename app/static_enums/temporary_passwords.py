from enum import Enum

class TemporaryPasswordEnum(Enum):
    """Enum for Temporary Password types"""
    ADMIN_PASSWORD = "admin_password"
    USER_PASSWORD = "user_password"