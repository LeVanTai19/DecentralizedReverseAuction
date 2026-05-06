from fastapi import FastAPI
from routers.auction import router as auction_router
from routers.auth import router as auth_router

app = FastAPI(title="Decentralized Auction API")

app.include_router(auction_router, prefix="/api/auction")

app.include_router(auth_router, prefix="/api/auth")