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
    SESSION_BANNERS = "session-banners"
    SPEAKER_IMAGES = "speaker-images"
    SPONSOR_LOGOS = "sponsor-logos"
    PROMOTION_IMAGES = "promotion-images"
    EVENT_DOCUMENTS = "event-documents"
    SESSION_DOCUMENTS = "session-documents"
    BACKDROP_IMAGES = "backdrop-images"
    EXHIBITOR_LOGOS = "exhibitor-logos"
    EXHIBITOR_BANNERS = "exhibitor-banners"
    EXHIBITOR_DOCUMENTS = "exhibitor-documents"
    TEMPLATES = "templates"