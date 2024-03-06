from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..schemas import promotion_schemas
from ..crud import promotions_crud
from ..dependencies import get_db
from ..basicauth import basic_auth
import logging
from urllib.parse import urlparse

router = APIRouter(tags=['promotions'])

@router.post('/promotions', response_model=promotion_schemas.Promotion, status_code=status.HTTP_201_CREATED)
def create_promotion(promotion: promotion_schemas.PromotionCreate, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    db_promotion = promotions_crud.get_promotion_by_conference(db=db, conference_id=promotion.conference_id)
    if db_promotion:
        logging.exception("Promotion already registered")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Promotion already registered")
    if promotion.fromdate > promotion.todate:
        logging.exception("Invalid date range")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date range")
    promotion = promotions_crud.create_promotion(db=db, promotion=promotion)
    logging.info("Promotion created: " + promotion.uuid)
    return promotion

@router.get('/promotions', response_model=list[promotion_schemas.Promotion])
def get_promotions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    promotions = promotions_crud.get_promotions(db=db, skip=skip, limit=limit)
    if promotions is None or len(promotions) == 0:
        logging.exception("Promotions not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotions not found")
    logging.info("Promotions retrieved")
    return promotions

@router.get('/promotions/get-all', response_model=list[promotion_schemas.Promotion])
def get_all_promotions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    promotions = promotions_crud.get_all_promotions(db, skip=skip, limit=limit)
    if promotions is None or len(promotions) == 0:
        logging.exception("Promotions not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotions not found")
    logging.info("Promotions retrieved")
    return promotions

@router.get('/promotions/{promotion_id}', response_model=promotion_schemas.Promotion)
def get_promotion(promotion_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    promotion = promotions_crud.get_promotion(db, promotion_id=promotion_id)
    if promotion is None:
        logging.exception("Promotion not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")
    logging.info("Promotion retrieved: " + promotion.uuid)
    return promotion

@router.put('/promotions', response_model=promotion_schemas.Promotion)
def update_promotion(promotion: promotion_schemas.PromotionUpdate, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    promotion_dict: dict = promotion.model_dump()
    promotion_dict.pop('id')
    promotion_dict['rank'] = promotion_dict['rank'] if promotion_dict['rank'] != 0 else None
    if all(value is None for value in promotion_dict.values()):
        logging.exception("Invalid request body")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
    db_promotion = promotions_crud.get_promotion(db, promotion_id=promotion.id)
    if db_promotion is None:
        logging.exception("Promotion not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")
    promotion = promotions_crud.update_promotion(db=db, promotion=promotion)
    logging.info("Promotion updated: " + promotion.uuid)
    return promotion

@router.delete('/promotions/{promotion_id}')
def delete_promotion(promotion_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    db_promotion = promotions_crud.get_promotion(db, promotion_id=promotion_id)
    if db_promotion is None:
        logging.exception("Promotion not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promotion not found")
    promotion = promotions_crud.delete_promotion(db=db, promotion_id=promotion_id)
    if not promotion:
        logging.exception("Promotion not deleted")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Promotion not deleted")
    logging.info("Promotion deleted: " + db_promotion.uuid)
    return promotion