from fastapi import APIRouter, HTTPException
from services.contract import auction_service

from schemas.dto import CommitRequestDTO
from schemas.dto import RevealRequestDTO
from schemas.dto import ChangePhaseRequestDTO

router = APIRouter(tags=["Auction system"])

@router.post("/commit")
def commit_endpoint (payload: CommitRequestDTO):

    result = auction_service.commit_bid(payload.user_id, payload.hash_value)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/reveal")
def reveal_endpoint(payload: RevealRequestDTO):

    result = auction_service.reveal_bid(payload.user_id, payload.real_price, payload.secret_salt)

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
def change_phase_endpoint (payload: ChangePhaseRequestDTO):

    result = auction_service.change_phase (payload.new_phase)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@router.get("/admin/dashboard")
def admin_dashboard_endpoint():

    return auction_service.get_admin_dashboard()


@router.get("/user/{user_id}/dashboard")
def user_dashboard_endpoint(user_id: str):

    return auction_service.get_user_info(user_id)

    
