from enum import Enum

class BlobContainer(Enum):
    """Enum for blob containers"""
    
    TEMPORARY_IMAGES = "temporary-images"
    PROFILE_IMAGES = "profile-images"
    ATTENDE_PROFILE_IMAGES = "attende-profile-images"
    CLIENT_LOGOS = "client-logos"
    EVENT_BANNERS = "event-banners"
    EVENT_LOGOS = "event-logos"
    SESSION_IMAGES = "session-images"
    SPEAKER_IMAGES = "speaker-images"
    SPONSOR_LOGOS = "sponsor-logos"
    PROMOTION_IMAGES = "promotion-images"