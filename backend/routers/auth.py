from fastapi import APIRouter, HTTPException, Depends

from sqlalchemy.orm import Session
from database import get_db
from models import User

from schemas.dto import LoginDTO

router = APIRouter(tags=["Authentication"])

@router.post("/login")
def login_endpoint (payload: LoginDTO, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == payload.username)

    if not user:
        raise HTTPException(status_code=401, detail= "Tài khoản không tồn tại trong hệ thống!")
    
    return {
        "success": "Đăng nhập thành công!",
        "user_id": user.id,
        "role": user.role,
        "name": "Chủ Đầu Tư" if user.role == "admin" else f"Nhà thầu {user.id}"
    }