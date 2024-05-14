from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from app.oauth2 import get_current_active_organization
from app.static_enums.role import RoleEnum
from ..schemas import client_schemas as schemas
from ..crud import client_crud as crud
from ..dependencies import get_db
from email_validator import validate_email, EmailNotValidError
from ..schemas.organization_schemas import OrganizationSecurity
import logging

router = APIRouter(tags=["client"])

@router.post("/clients", response_model=schemas.ClientResponse, status_code=status.HTTP_201_CREATED)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    try:
        valid = validate_email(client.contact_email)
        client.contact_email = valid.email
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    client = crud.create_client(db=db, client=client, organization_id=current_organization.id)
    logging.info("Client created: " + client.uuid)
    return client

@router.get("/clients", response_model=list[schemas.ClientResponse])
def get_all_clients_by_organization_id(offset: int = 0, limit: int = 100, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    if offset < 0 or limit < 0:
        logging.exception("Invalid query parameters")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query parameters")
    clients = crud.get_all_clients_by_organization_id(db=db, offset=offset, limit=limit,organization_id=current_organization.id)
    if clients is None or len(clients) == 0:
        logging.exception("Client not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    logging.info("Clients Retrieved")
    return clients

@router.get("/clients/all_clients", response_model=list[schemas.ClientResponse])
def get_all_clients(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if offset < 0 or limit < 0:
        logging.exception("Invalid query parameters")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query parameters")
    clients = crud.get_all_clients(db, offset=offset, limit=limit)
    if clients is None or len(clients) == 0:
        logging.exception("Client not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    logging.info("Clients Retrieved")
    return clients

@router.get("/clients/{client_id}", response_model=schemas.ClientResponse)
def get_client(client_id: str, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_client = crud.get_client_by_uuid_and_organization_id(db, client_id=client_id, organization_id=current_organization.id)
    if db_client is None:
        logging.exception("Client not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    logging.info("Client retrieved: " + db_client.uuid)
    return db_client

@router.put("/clients", response_model=schemas.ClientResponse)
def update_client(client: schemas.ClientUpdate, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    if all(value is None for value in dict(client).values()):
        logging.exception("Invalid request body")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
    db_client = crud.get_client_by_uuid_and_organization_id(db, client_id=client.id, organization_id=current_organization.id)
    if db_client is None:
        logging.exception("Client not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    updated_client = crud.update_client(db=db, client=client)
    logging.info("User updated: " + updated_client.uuid)
    return updated_client

@router.delete("/clients/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_client = crud.get_client_by_uuid_and_organization_id(db, client_id=client_id, organization_id=current_organization.id)
    if db_client is None:
        logging.exception("Client not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    deleted_client = crud.delete_client(db=db, client_id=client_id)
    logging.info("Client Deleted: " + db_client.uuid)
    return deleted_client