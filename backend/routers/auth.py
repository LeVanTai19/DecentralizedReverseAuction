from fastapi import APIRouter, HTTPException
from services.auth_logic import verify_login

from schemas.dto import LoginDTO

router = APIRouter(tags=["Authentication"])

@router.post("/login")
def login_endpoint (payload: LoginDTO):

    result = verify_login(payload.username, payload.password)

    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result