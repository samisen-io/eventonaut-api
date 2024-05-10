from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, Request, Security, UploadFile
from sqlalchemy.orm import Session
import requests
from app.crud import conferences_crud, users_crud
from app.eventbrite_operations import add_event, add_venue, create_webhook, get_organization_id, get_organization_id_from_url, update_eventbrite_status, update_from_eventbrite, update_venue_from_eventbrite
from app.oauth2 import get_current_active_user
from app.crud.organization_settings_crud import create_organization_settings, get_organization_settings, get_organization_settings_by_eventbrite_org_id
from app.schemas import organization_settings_schemas as os_schemas
from app.schemas.user_schemas import UserAuthentication as User
from app.schemas import organization_settings_schemas as os_schemas
from app.schemas.user_schemas import UserAuthentication as User
from app.dependencies import get_db
from app.crud.organization_crud import get_organization_by_external_id, get_organization_by_id, get_organization_by_user_id, get_organization_by_uuid
from app.static_enums.role import RoleEnum
from starlette.requests import ClientDisconnect

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

@router.get("/update_eventbrite_events/")
def update_eventbrite_events(db: Session = Depends(get_db),current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    organization = get_organization_by_user_id(db, current_user.id)
    if organization is None:
        raise HTTPException(status_code=400, detail="Organization not found.")
    private_token = get_organization_settings(db, organization.id).event_brite_access_token
    eventbrite_organization_id = get_organization_id(private_token)
    url = f"https://www.eventbriteapi.com/v3/organizations/{eventbrite_organization_id}/events/?status=live"
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Incorrect request. Please check your private token and organization ID.")
    response = response.json()
    owner_id = current_user.id
    organization = get_organization_by_user_id(db, owner_id)
    organization_id = organization.id
    for event in response["events"]:
        event_id = event["id"] 
        db_event = conferences_crud.get_conference_by_external_id(db, event_id)
        if not db_event:
            # create venue
            event_venue = get_eventbrite_venue(event_id, private_token)
            # print(event_venue)
            event_venue = add_venue(db,event_venue,organization_id)
            event_venue_id = event_venue.id
            #add event
            event = add_event(db,event,owner_id,event_venue_id)
            create_webhook(event_id, private_token, eventbrite_organization_id)
        else:
            conference_venue = db_event.venue
            conference_venue_id = conference_venue.uuid
            # updated venue
            event_venue = get_eventbrite_venue(event_id, private_token)
            event_venue = update_venue_from_eventbrite(db,event_venue,organization_id, conference_venue_id)
            # updated event
            update_from_eventbrite(db, event, organization, db_event)
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
    try:
        data = await request.json()
    except ClientDisconnect:
        return {"error": "Client disconnected"}
    endpoint_url = data['config']['endpoint_url']
    organization_id = data['config']['user_id']
    api_url = data['api_url']
    action = data['config']['action']
    eb_event_id = get_organization_id_from_url(api_url)
    org_settings = get_organization_settings_by_eventbrite_org_id(db,organization_id)
    organization = get_organization_by_external_id(db, organization_id)
    private_token = org_settings.event_brite_access_token
    
    url = f"https://www.eventbriteapi.com/v3/organizations/{organization_id}/events/?status=live"
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    event = None
    response = requests.get(url, headers=headers)
    for event in response.json()["events"]:
        if event["id"] == eb_event_id:
            event = event
            break
        
    if action == 'event.updated':
        conference = conferences_crud.get_conference_by_external_id(db, eb_event_id)
        conference_venue = conference.venue
        conference_venue_id = conference_venue.uuid
        # updated venue
        event_venue = get_eventbrite_venue(eb_event_id, private_token)
        event_venue = update_venue_from_eventbrite(db,event_venue,organization_id, conference_venue_id)
        # updated event
        update_from_eventbrite(db, event, organization, conference)
        
    elif action == 'event.published' or action == 'event.unpublished':
        update_eventbrite_status(db, event, organization)
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

@router.post('/create_webhook/')
def create_eventbrite_webhook(event_id: str, private_token: str, organization_id: str):
    return create_webhook(event_id, private_token, organization_id)