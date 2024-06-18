from pydantic import BaseModel, Field, field_validator

from app.schemas import registration_order_item_schema_temp, registration_order_schema_temp
from app.schemas.conference_schemas import ConferenceResponse

class CreateTicket(BaseModel):
    event_id: str
    amount: float
    tax_amount: float
    fee_amount: float
    description: str
    quantity: int
    registration_setup_item_id: int
    code : str
    
class TicketResponse(BaseModel):
    ticket_id: str
    event_id: str
    amount: float
    tax_amount: float
    fee_amount: float
    description: str
    quantity: int
    registration_setup_item_id: int
    code : str
    
class TicketData(BaseModel):
    title: str
    event: str
    orderNumber: str
    logo: str
    ticketType: str
    tickteID: str
    address: str
    dateTime: str
    orderType: str
    customerName: str
    orderDate: str
    orderTime: str
    qrCode: str
    
class TicketDataResponse(BaseModel):
    ticket_data: TicketData
    event: ConferenceResponse
    registration_order: registration_order_schema_temp.RegistrationOrder
    registration_order_item: registration_order_item_schema_temp.RegistrationOrderItem