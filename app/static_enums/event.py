from enum import Enum

class EventEnum(Enum):
    """Enum for event types"""
    ACTIVE = 1
    INACTIVE = 2
    COMPLETED = 3
    ABANDONED = 4