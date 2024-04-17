from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import requests
from app.schemas import organization_settings_schemas as os_schemas
from app.schemas import conference_schemas as c_schemas
from app.crud.organization_settings_crud import create_organization_settings
from app.dependencies import get_db
from app.crud.organization_crud import get_organization_by_id
from app.models import OrganizationSettings

router = APIRouter(tags=["Eventbrite Connector"])

@router.get("/get_eventbrite_events/")
def get_eventbrite_events(private_token: str, organization_id: str):
    url = f"https://www.eventbriteapi.com/v3/organizations/{organization_id}/events/?status=live"
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    response = requests.get(url, headers=headers)
    # Validate the response
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Incorrect request. Please check your private token and organization ID.")
    # events = response.json()["events"]
    events = response.json()
    # event_details = []
    # for event in events:
    #     event_detail = {
    #         'Event Name': event["name"]["text"],
    #         'Event Timezone': event["start"]["timezone"],
    #         'Event Start-Time': event["start"]["utc"],
    #         'Event End-Time': event["end"]["utc"],
    #         'Event URL': event["url"],
    #         'Event ID': event["id"],
    #         'Event Status': str(event["status"]),
    #         'Event Is-Online': str(event["online_event"]),
    #         'Event Logo-URL': event["logo"]["original"]["url"],
    #         'Event Summary': event["summary"],
    #         'Event Description': event["description"]["text"],
    #     }
    #     event_details.append(event_detail)
    return events

@router.get("/save_eventbrite_events/")
def save_eventbrite_events( organization_id: str, private_token: str, eventbrite_organization_id: str, db: Session = Depends(get_db)):
    url = f"https://www.eventbriteapi.com/v3/organizations/{eventbrite_organization_id}/events/?status=live"
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    response = requests.get(url, headers=headers)
    # Validate the response
    organization = get_organization_by_id(db, organization_id)
    if organization is None:
        raise HTTPException(status_code=400, detail="Organization not found in Command Center. Please check your organization ID.")
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Incorrect request. Please check your private token and organization ID.")
    response = response.json()
    # Save it in the database
    organization_settings = {
        'organization_id': organization_id,
        'event_brite_org_id': eventbrite_organization_id,
        'event_brite_access_token': private_token
        }
    org_settings = os_schemas.OrganizationSettingsCreate(**organization_settings)
    # create_organization_settings(db, org_settings, organization_id)
    # Create webhooks for each event
    for event in response["events"]:
        event_id = event["id"] 
        print(event["logo"]["original"]["url"])
        payload = {
            'name': event["name"]["text"],
            'start_date': datetime.strptime(event["start"]["utc"], "%Y-%m-%dT%H:%M:%SZ").date(),
            'end_date': datetime.strptime(event["end"]["utc"], "%Y-%m-%dT%H:%M:%SZ").date(),
            'description': event["description"]["text"],
            'timezone': event["start"]["timezone"],
            'registration_link': event["url"],
            'conference_banner_url': event["logo"]["original"]["url"],
            'information_guide': event['url'],
            'status': "active" if event["status"] else "inactive",
            'external_id': f"ebt_{organization_id}_{event['id']}"
        }
        event = c_schemas.ConferenceCreate(**payload)
        print(event)
        # create_webhook(event_id, private_token, eventbrite_organization_id)
        # Save the event details in the database
    return {"message": "Eventbrite events retrieved successfully."}

@router.get('/sync_eventbrite_events/')
def sync_eventbrite_events(private_token: str, organization_id: str):
    url = f"https://www.eventbriteapi.com/v3/organizations/{organization_id}/events/?status=live"
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    response = requests.get(url, headers=headers)
    # Validate the response
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Incorrect request. Please check your private token and organization ID.")
    # Save events in the database
    for event in response['events']:
        event_id = event['id']
        # Check the organization id 
    
@router.get('/get_webhooks/')
async def get_webhooks(private_token: str, organization_id: str):
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    url = f'https://www.eventbriteapi.com/v3/organizations/{organization_id}/webhooks/'
    response = requests.get(url, headers=headers)
    return response.json()

@router.delete('/delete_webhook/')
async def delete_webhook(webhook_id: str, private_token: str, organization_id: str):
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    url = f'https://www.eventbriteapi.com/v3/webhooks/{webhook_id}/'
    response = requests.delete(url, headers=headers)
    return response.json()
    
@router.post('/webhook/')
async def webhook(request: Request):
    data = await request.json()
    print(data)
    return {'received': True}

def create_webhook(event_id: str, private_token: str, organization_id: str):
    values = {
        "endpoint_url": "https://c272-14-97-147-123.ngrok-free.app/webhook/",
        # "endpoint_url": "https://event-data-api.azurewebsites.net/webhook/",
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