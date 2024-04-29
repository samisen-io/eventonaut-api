from datetime import datetime
import json
import os
import tempfile
from urllib.parse import urlparse
from fastapi import UploadFile
import requests
from app.crud.organization_crud import get_organization_by_user_id
# from app.routers.eventbrite_connector import get_eventbrite_venue
from app.schemas import conference_schemas as c_schemas
from app.schemas import venue_schemas as v_schemas
from app.crud.conferences_crud import create_user_conference
from app.crud.venue_crud import create_venue, create_venue_using_organization_id
from app.routers.upload_image import upload_file


def create_webhook(event_id: str, private_token: str, organization_id: str):
    values = {
        "endpoint_url": "https://event-data-api.azurewebsites.net/webhook/",
        "actions": "event.created,event.updated,event.published,event.unpublished",
        "event_id": event_id,
    }
    headers = {
        'Authorization': f'Bearer {private_token}',
        'Content-Type': 'application/json',
    }
    url = f'https://www.eventbriteapi.com/v3/organizations/{organization_id}/webhooks/'
    response = requests.post(url, data=json.dumps(values), headers=headers)
    return response.json()

def add_venue(db,event_venue,owner_id):
    organization = get_organization_by_user_id(db, owner_id)
    organization_id = organization.id
    venue_payload = {
        'name': event_venue["venue"]["name"],
        'location': event_venue["venue"]["address"]["city"]+", "+event_venue["venue"]["address"]["region"]+", "+event_venue["venue"]["address"]["country"],
        'address': event_venue["venue"]["address"]["localized_address_display"],
        'gio_location': str(event_venue["venue"]["latitude"])+", "+str(event_venue["venue"]["longitude"])
    }
    venue_obj = v_schemas.VenueCreate(**venue_payload)
    venue = create_venue_using_organization_id(db,venue_obj,owner_id)
    return venue

def update_venue(db,event_venue,owner_id):
    organization = get_organization_by_user_id(db, owner_id)
    venue_payload = {
        'name': event_venue["venue"]["name"],
        'location': event_venue["venue"]["address"]["city"]+", "+event_venue["venue"]["address"]["region"]+", "+event_venue["venue"]["address"]["country"],
        'address': event_venue["venue"]["address"]["localized_address_display"],
        'gio_location': str(event_venue["venue"]["latitude"])+", "+str(event_venue["venue"]["longitude"])
    }
    
def add_event(db,event,owner_id,venue_id):
    # upload photo
    event_logo_url = event["logo"]["original"]["url"]
    response = requests.get(event_logo_url, stream=True)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            for chunk in response.iter_content(1024):
                temp_file.write(chunk)
            temp_filename = temp_file.name
            print(temp_filename)
        with open(temp_filename, 'rb') as f:
            upload_file_response = upload_file(UploadFile(filename=temp_filename, file=f))
            event_logo_url = upload_file_response['url']
            organization = get_organization_by_user_id(db, owner_id)
            event_payload = {
                'name': event["name"]["text"],
                'start_date': datetime.strptime(event["start"]["utc"], "%Y-%m-%dT%H:%M:%SZ").date(),
                'end_date': datetime.strptime(event["end"]["utc"], "%Y-%m-%dT%H:%M:%SZ").date(),
                'description': event["description"]["text"],
                'timezone': event["start"]["timezone"],
                'registration_link': event["url"],
                'conference_banner_url': None,
                'conference_logo': event_logo_url,
                'information_guide': event['url'],
                'status': "active" if event["status"] else "inactive",
                'external_id': event['id'],
                'organization_id': organization.id,
                'venue_id': str(venue_id),
                'event_type': 'OTHER'
            }
            event = c_schemas.ConferenceCreate(**event_payload)
            event = create_user_conference(db, event, owner_id, venue_id, None)
            os.remove(temp_filename)
            return event
        
def get_organization_id_from_url(url: str):
    path_parts = urlparse(url).path.split('/')
    return path_parts[-1] if path_parts[-1] else path_parts[-2]

def update_from_eventbrite(db, eb_event_id, organization_id, endpoint_url):
    # print("Eventbrite event updated. Event ID: ", eb_event_id)
    pass