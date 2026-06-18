from fastapi import APIRouter, HTTPException, Depends
from services.contract import auction_service

from sqlalchemy.orm import Session
from database import get_db # Hàm tạo connection từ database.py

from schemas.dto import CommitRequestDTO
from schemas.dto import RevealRequestDTO
from schemas.dto import ChangePhaseRequestDTO

router = APIRouter(tags=["Auction system"])

@router.post("/commit")
def commit_endpoint (payload: CommitRequestDTO, db: Session = Depends(get_db)):

    result = auction_service.commit_bid(db, payload.user_id, payload.hash_value, payload.signature)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/reveal")
def reveal_endpoint(payload: RevealRequestDTO, db: Session = Depends(get_db)):

    result = auction_service.reveal_bid(db, payload.user_id, payload.real_price, payload.secret_salt, payload.signature)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result

"""@router.get("/winner")
def get_winner_endpoint():
    
    result = auction_service.get_winner()

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result"""

@router.post("/phase")
def change_phase_endpoint (payload: ChangePhaseRequestDTO, db: Session = Depends(get_db)):

    result = auction_service.change_phase (db, payload.new_phase)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/admin/dashboard")
def admin_dashboard_endpoint(db: Session = Depends(get_db)):

    return auction_service.get_admin_dashboard(db)


@router.get("/user/{user_id}/dashboard")
def user_dashboard_endpoint(user_id: str, db: Session = Depends(get_db)):

    return auction_service.get_user_info(db, user_id)

    
