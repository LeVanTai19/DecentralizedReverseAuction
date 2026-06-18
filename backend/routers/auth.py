from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session
from database import get_db

from schemas.dto import LoginDTO, RegisterWalletDTO
from services.auth_logic import register_user_logic, verify_login_logic

router = APIRouter(tags=["Authentication"])

@router.post("/register")
def register_wallet_endpoint(payload: RegisterWalletDTO, db: Session = Depends(get_db)):
    result = register_user_logic(db, payload.username, payload.public_key)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result
    

@router.post("/login")
def login_endpoint (payload: LoginDTO, db: Session = Depends(get_db)):

    result = verify_login_logic(db, payload.username, payload.password)

    if "error" in result:
        raise HTTPException(status_code=401, detail= result["error"])
    
    return result
    