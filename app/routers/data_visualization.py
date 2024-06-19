from collections import defaultdict
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.crud.conferences_crud import get_conference_by_conference_uuid
from app.crud.registration_order_item_crud import get_registration_order_items_by_event_id, get_registration_order_items_by_registration_setup_item_id
from app.crud.registration_setup_item_crud_temp import get_registration_setup_items_by_event_id
from app.dependencies import get_db
from app.oauth2 import get_current_active_user
from app.schemas.user_schemas import User
from app.static_enums.role import RoleEnum


router = APIRouter(tags=["data_visualization"])
    
@router.get("/event-revenue/")
def event_revenue(event_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    event = get_conference_by_conference_uuid(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    setup_items = get_registration_setup_items_by_event_id(db, event.id)
    revenue_by_setup_item = []
    for setup_item in setup_items:
        order_items = get_registration_order_items_by_registration_setup_item_id(db, setup_item.id)
        total_revenue = sum([order_item.quantity * order_item.unit_price for order_item in order_items])
        revenue_by_setup_item.append({"item": setup_item.name, "amount": total_revenue})
    return revenue_by_setup_item

@router.get("/ticket-sales/")
def ticket_sales(event_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    event = get_conference_by_conference_uuid(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    order_items = get_registration_order_items_by_event_id(db, event.id)
    date_totals = defaultdict(int)
    for order_item in order_items:
        date_totals[order_item.created_on.date()] += order_item.quantity
    daily_sales = [{'date': str(date), 'total_number': total} for date, total in date_totals.items()]
    daily_sales.sort(key=lambda x: x['date'])
    earliest_order_date = max(min(date_totals.keys()), max(date_totals.keys()) - timedelta(days=7))
    latest_order_date = max(date_totals.keys())
    day = earliest_order_date
    while day <= latest_order_date:
        if not any(d['date'] == str(day) for d in daily_sales):
            daily_sales.append({'date': str(day), 'total_number': 0})
        day += timedelta(days=1)
    daily_sales.sort(key=lambda x: x['date'])
    return daily_sales

@router.get("/items-sold-and-available/")
def items_sold_and_available(event_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    event = get_conference_by_conference_uuid(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    setup_items = get_registration_setup_items_by_event_id(db, event.id)
    total_sold = 0
    total_available = 0
    total_items = 0
    for setup_item in setup_items:
        total_available += setup_item.available_quantity
        total_items += setup_item.total_quantity
    total_sold = total_items - total_available
    return [{"category": "Total items available", "value": total_available}, {"category": "Total items sold", "value": total_sold}]