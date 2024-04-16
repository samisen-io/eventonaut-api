import json
from fastapi import APIRouter, HTTPException, Request
import requests

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
    response = response.json()
    for event in response["events"]:
        print('=========================================================')
        print('Event Name: '+event["name"]["text"])
        print('Event Timezone: '+event["start"]["timezone"])
        print('Event Start-Time: '+event["start"]["utc"])
        print('Event End-Time: '+event["end"]["utc"])
        print('Event URL: '+event["url"])
        print('Event ID: '+event["id"])
        print('Event Status: '+str(event["status"]))
        print('Event Is-Online: '+str(event["online_event"]))
        print('Event Logo-URL: '+event["logo"]["original"]["url"])
        print('Event Summary: '+event["summary"])
        print('Event Description: '+event["description"]["text"])
        print('=========================================================')
    return {"message": "Eventbrite events retrieved successfully."}

@router.get("/save_eventbrite_events/")
def save_eventbrite_events(private_token: str, organization_id: str):
    url = f"https://www.eventbriteapi.com/v3/organizations/{organization_id}/events/?status=live"
    headers = {
        'Authorization': f'Bearer {private_token}',
    }
    response = requests.get(url, headers=headers)
    # Validate the response
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Incorrect request. Please check your private token and organization ID.")
    response = response.json()
    # Save it in the database
    # Create webhooks for each event
    for event in response["events"]:
        event_id = event["id"]
        create_webhook(event_id, private_token, organization_id)
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
        "endpoint_url": "https://b1d0-14-97-147-123.ngrok-free.app/webhook/",
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