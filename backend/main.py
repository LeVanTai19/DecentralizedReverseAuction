from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auction import router as auction_router
from routers.auth import router as auth_router

app = FastAPI(title="Decentralized Auction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép mọi FE gọi đến BE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auction_router, prefix="/api/auction")

app.include_router(auth_router, prefix="/api/auth")