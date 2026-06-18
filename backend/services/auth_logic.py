from sqlalchemy.orm import Session
from models import User

def register_user_logic(db: Session, username: str, public_key: str) -> dict:

    # check xem username (id) này đã có người nào đăng ký chưa
    existing_user = db.query(User).filter(User.id == username).first()
    if existing_user:
        return {"error": "Tên tài khoản này đã có người sử dụng!"}
    
    new_user = User(
        id = username,
        role = "user",
        balance = 10000.0,
        public_key = public_key
    )

    db.add(new_user)
    db.commit()
    return {"success": "Tạo Ví thành công!", "user_id": new_user.id}

def verify_login_logic(db: Session, username: str, password: str = None) -> dict:
    user = db.query(User).filter(User.id == username).first()

    if not user:
        return {"error": "Tài khoản không tồn tại! Vui lòng tạo Ví trước!"}
    
    if user.role == "admin" and password != "123":
        return {"error": "Sai mật khẩu Admin!"}
    
    return {
        "success": "Bạn đã đăng nhập thành công",
        "user_id": user.id,
        "role": user.role,
        "name": "Chủ Đầu Tư" if user.role == "admin" else f"Nhà thầu {user.id}"
    }