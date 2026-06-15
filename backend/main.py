from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from routers.auction import router as auction_router
from routers.auth import router as auth_router

from database import engine, Base, SessionLocal
from models import User, Auction

Base.metadata.create_all(bind=engine) # lệnh giúp tự tạo file auction.db và tạo bảng

app = FastAPI(title="Decentralized Auction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi FE gọi đến BE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Tạo dữ liệu mồi lúc khởi động =====
def seed_data():
    db = SessionLocal()

    # Tạo gói thầu mặc định
    if not db.query(Auction).first():
        default_auction = Auction(title = "Dự án xây cầu Alpha", phase = "COMMIT")
        db.add(default_auction)

    # Tạo các User mặc định
    users_to_seed = [
        {"id": "admin", "role": "admin", "balance": 0},
        {"id": "user1", "role": "user", "balance": 10000},
        {"id": "user2", "role": "user", "balance": 10000}
    ]

    for u in users_to_seed:
        if not db.query(User).first():
            new_user = User(id = u["id"], role = u["role"], balance = u["balance"])
            db.add(new_user)

    db.commit()
    db.close()     

seed_data()   

app.include_router(auction_router, prefix="/api/auction")

app.include_router(auth_router, prefix="/api/auth")