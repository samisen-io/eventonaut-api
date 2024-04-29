from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, Request, Security, UploadFile
from sqlalchemy.orm import Session
import requests
from app.crud import conferences_crud, users_crud
from app.eventbrite_operations import add_event, add_venue, create_webhook, get_organization_id_from_url, update_from_eventbrite
from app.oauth2 import get_current_active_user
from app.crud.organization_settings_crud import create_organization_settings, get_organization_settings
from app.schemas import organization_settings_schemas as os_schemas
from app.schemas.user_schemas import UserAuthentication as User
from app.schemas import organization_settings_schemas as os_schemas
from app.schemas.user_schemas import UserAuthentication as User
from app.dependencies import get_db
from app.crud.organization_crud import get_organization_by_id, get_organization_by_user_id, get_organization_by_uuid
from app.static_enums.role import RoleEnum

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
    return events

@router.get("/sync_eventbrite_events/")
def sync_eventbrite_events(private_token: str, eventbrite_organization_id: str, db: Session = Depends(get_db),current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    url = f"https://www.eventbriteapi.com/v3/organizations/{eventbrite_organization_id}/events/?status=live"
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    response = requests.get(url, headers=headers)
    # Validate the response
    print(current_user.id)
    # organization = get_organization_by_uuid(db, organization_id)
    organization = get_organization_by_user_id(db, current_user.id)
    print(organization.uuid)
    print(organization.id)
    if organization is None:
        raise HTTPException(status_code=400, detail="Organization not found in Command Center. Please check your organization ID.")
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Incorrect request. Please check your private token and organization ID.")
    response = response.json()
    owner_id = users_crud.get_user(db, current_user.id)
    if not owner_id:
        raise HTTPException(status_code=400, detail="User not found.")
    owner_id = owner_id.id
    # Save it in the database
    
    organization_settings = {
        'organization_id': str(organization.id),
        'event_brite_org_id': eventbrite_organization_id,
        'event_brite_access_token': private_token
        }
    org_settings = os_schemas.OrganizationSettingsCreate(**organization_settings)
    create_organization_settings(db, org_settings, organization.id)
    # Create webhooks for each event
    for event in response["events"]:
        event_id = event["id"] 
        # create venue
        event_venue = get_eventbrite_venue(event_id, private_token)
        event_venue = add_venue(db,event_venue,owner_id)
        event_venue_id = event_venue.id
        #add event
        event = add_event(db,event,owner_id,event_venue_id)
        create_webhook(event_id, private_token, eventbrite_organization_id)
        # Save the event details in the database
    return {"message": "Eventbrite events retrieved successfully."}
    
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
async def webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    endpoint_url = data['config']['endpoint_url']
    organization_id = data['config']['user_id']
    api_url = data['api_url']
    action = data['config']['action']
    eb_event_id = get_organization_id_from_url(api_url)
    org_settings = get_organization_settings(db,organization_id)
    private_token = org_settings.event_brite_access_token
    if action == 'event.updated':
        # conference = conferences_crud.get_conference_by_external_id(db, eb_event_id)
        # conference_venue = conference.venue
        # print(conference_venue)
        # updated venue
        # event_venue = get_eventbrite_venue(eb_event_id, private_token)
        # event_venue = update_venue
        update_from_eventbrite(db, eb_event_id, organization_id, endpoint_url)
    
    elif action == 'event.published':
        pass
    elif action == 'event.unpublished':
        pass
    elif action == 'event.created':
        pass
    print(data)
    print(endpoint_url)
    print(organization_id)
    print(api_url)
    print(action)
    print(eb_event_id)
    return {'received': True}
        
        
@router.get('/get_eventbrite_venue/')
def get_eventbrite_venue(event_id: str, private_token: str):
    url = f"https://www.eventbriteapi.com/v3/events/{event_id}/?expand=venue"
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    response = requests.get(url, headers=headers)
    event = response.json()
    return event

@router.get('/testing/')
def testing(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    organization = get_organization_by_user_id(db, current_user.id)
    print(organization.id)
    return {'message': organization.id}



