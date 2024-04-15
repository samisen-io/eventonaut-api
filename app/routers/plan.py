from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from ..basicauth import basic_auth
from ..dependencies import get_db
from ..schemas import plan_schemas as schemas
from ..crud import plan_crud as crud
import logging

router = APIRouter(tags=["plan"])

@router.get("/plans", response_model=list[schemas.Plan])
def get_plans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    plans = crud.get_plans(db, skip=skip, limit=limit)
    if not plans or len(plans) == 0:
        logging.exception("No plans found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No plans found")
    logging.info("Plans retrieved")
    return plans

@router.get("/plans/{plan_id}", response_model=schemas.Plan)
def get_plan_by_plan_id(plan_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    plan = crud.get_plan_by_plan_id(db, plan_id=plan_id)
    if plan is None:
        logging.exception("Plan not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    logging.info("Plan retrieved: " + plan.uuid)
    return plan

@router.post("/plans", response_model=schemas.Plan, status_code=status.HTTP_201_CREATED)
def create_plan(plan: schemas.PlanBase, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    if crud.get_plan_by_plan_id(db, plan_id=plan.plan_id):
        logging.exception("Plan already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Plan already exists")
    plan = crud.create_plan(db=db, plan=plan)
    logging.info("Plan created: " + plan.uuid)
    return plan

@router.put("/plans/{id}", response_model=schemas.Plan)
def update_plan(id: str, plan: schemas.PlanUpdate, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    db_plan = crud.get_plan_by_uuid(db, uuid=id)
    if db_plan is None:
        logging.exception("Plan not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    plan = crud.update_plan(db=db, update_plan=plan, db_plan=db_plan)
    logging.info("Plan updated: " + plan.uuid)
    return plan

@router.delete("/plans/{plan_id}")
def delete_plan(id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    db_plan = crud.get_plan_by_plan_id(db, plan_id=id)
    if db_plan is None:
        logging.exception("Plan not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    plan = crud.delete_plan(db=db, db_plan=db_plan)
    logging.info("Plan deleted: " + plan.uuid)
    return True