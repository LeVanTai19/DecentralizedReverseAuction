from fastapi import APIRouter, HTTPException
from services.contract import auction_service

from schemas.dto import CommitRequestDTO
from schemas.dto import RevealRequestDTO

router = APIRouter()

@router.post("/commit")
def commit_endpont (payload: CommitRequestDTO):

    result = auction_service.commit_bid(payload.user_id, payload.hash_value)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/reveal")
def reveal_endpont(payload: RevealRequestDTO):

    result = auction_service.reveal_bid(payload.user_id, payload.real_price, payload.secret_salt)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result