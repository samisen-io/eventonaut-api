from datetime import datetime
import json
import os
import tempfile
from urllib.parse import urlparse
from fastapi import UploadFile
import requests
from app.crud.organization_crud import get_organization_by_user_id
from app.schemas import conference_schemas as c_schemas
from app.schemas import venue_schemas as v_schemas
from app.crud.conferences_crud import create_user_conference, update_user_conference, update_user_conference_externally
from app.crud.venue_crud import create_venue, create_venue, update_venue_by_id
from app.routers.upload_image import upload_file


def create_webhook(event_id: str, private_token: str, organization_id: str):
    values = {
        "endpoint_url": "https://dev.api.eventonaut.app/webhook/",
        # "endpoint_url": "https://d5c6-14-97-147-123.ngrok-free.app/webhook/",
        "actions": "event.updated,event.published,event.unpublished",
        "event_id": event_id,
    }
    headers = {
        'Authorization': f'Bearer {private_token}',
        'Content-Type': 'application/json',
    }
    url = f'https://www.eventbriteapi.com/v3/organizations/{organization_id}/webhooks/'
    response = requests.post(url, data=json.dumps(values), headers=headers)
    return response.json()

def get_organization_id(private_token: str):
    headers = {
        'Authorization': f'Bearer   {private_token}',
    }
    url = 'https://www.eventbriteapi.com/v3/users/me/organizations/'
    response = requests.get(url, headers=headers)
    response = response.json()
    organization_id = response["organizations"][0]["id"]
    return organization_id

def add_venue(db,event_venue,organization_id):
    venue_payload = {
        'name': event_venue["venue"]["name"],
        'location': event_venue["venue"]["address"]["city"]+", "+event_venue["venue"]["address"]["region"]+", "+event_venue["venue"]["address"]["country"],
        'address': event_venue["venue"]["address"]["localized_address_display"],
        'gio_location': str(event_venue["venue"]["latitude"])+", "+str(event_venue["venue"]["longitude"])
    }
    venue_obj = v_schemas.VenueCreate(**venue_payload)
    venue = create_venue(db,venue_obj,organization_id)
    return venue

def update_venue_from_eventbrite(db,event_venue,owner_id,venue_id):
    venue_payload = {
        'id': venue_id,
        'name': event_venue["venue"]["name"],
        'location': event_venue["venue"]["address"]["city"]+", "+event_venue["venue"]["address"]["region"]+", "+event_venue["venue"]["address"]["country"],
        'address': event_venue["venue"]["address"]["localized_address_display"],
        'gio_location': str(event_venue["venue"]["latitude"])+", "+str(event_venue["venue"]["longitude"])
    }
    venue_obj = v_schemas.VenueUpdate(**venue_payload)
    venue = update_venue_by_id(db, venue_obj)
    return venue
    
def add_event(db,event,owner_id,venue_id):
    # upload photo
    event_logo_url = event["logo"]["original"]["url"]
    response = requests.get(event_logo_url, stream=True)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            for chunk in response.iter_content(1024):
                temp_file.write(chunk)
            temp_filename = temp_file.name
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
                'conference_banner_url': event_logo_url,
                'conference_logo': None,
                'information_guide': event['url'],
                'status': "active" if event["status"] else "inactive",
                'external_id': event['id'],
                'organization_id': organization.id,
                'venue_id': str(venue_id),
                'event_type': 'other'
            }
            event = c_schemas.ConferenceCreate(**event_payload)
            event = create_user_conference(db, event, owner_id, venue_id, None, None)
            os.remove(temp_filename)
            return event
        
def get_organization_id_from_url(url: str):
    path_parts = urlparse(url).path.split('/')
    return path_parts[-1] if path_parts[-1] else path_parts[-2]

def update_from_eventbrite(db, event, organization, conference):
    # upload photo
    event_logo_url = event["logo"]["original"]["url"]
    response = requests.get(event_logo_url, stream=True)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            for chunk in response.iter_content(1024):
                temp_file.write(chunk)
            temp_filename = temp_file.name
        with open(temp_filename, 'rb') as f:
            upload_file_response = upload_file(UploadFile(filename=temp_filename, file=f))
            event_logo_url = upload_file_response['url']
            event_payload = {
                'id': conference.uuid,
                'name': event["name"]["text"],
                'start_date': datetime.strptime(event["start"]["utc"], "%Y-%m-%dT%H:%M:%SZ").date(),
                'end_date': datetime.strptime(event["end"]["utc"], "%Y-%m-%dT%H:%M:%SZ").date(),
                'description': event["description"]["text"],
                'timezone': event["start"]["timezone"],
                'registration_link': event["url"],
                'conference_banner_url': event_logo_url,
                'conference_logo': None,
                'information_guide': event['url'],
                'status': "active" if event["status"] else "inactive",
                'external_id': event['id'],
                'organization_id': organization.id,
                'venue_id': str(conference.venue.uuid),
                'event_type': 'other'
            }
            event = c_schemas.ConferenceUpdate(**event_payload)
            event = update_user_conference_externally(db, event)
            return event

def update_eventbrite_status(db, event, conference):
    event_payload = {
        'id': conference.uuid,
        'status': "active" if event["status"] else "inactive",
    }
    event = c_schemas.ConferenceUpdate(**event_payload)
    event = update_user_conference_externally(db, event)
    return event