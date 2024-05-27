from enum import Enum

class RoleEnum(Enum):
    """Enum for Role types"""
    ATTENDEE = 1
    ORGANIZATION_ADMIN = 2
    ORGANIZATION_USER = 3
    REGISTRATION_STAFF = 4