from fastapi import FastAPI
from routers.auction import router as auction_router

app = FastAPI(title="Decentralized Auction API")

app.include_router(auction_router, prefix="/api/auction")