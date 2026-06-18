from pydantic import BaseModel
from typing import Optional

class LoginDTO (BaseModel):
    username: str
    password: Optional[str] = None

class RegisterWalletDTO(BaseModel):
    username: str
    public_key: str

class CreateAuctionDTO(BaseModel):
    title: str

class CommitRequestDTO (BaseModel):
    auction_id: int # THÊM MỚI: multi-projects
    user_id: str
    hash_value: str
    signature: str # THÊM MỚI: chữ ký số RSA

class RevealRequestDTO (BaseModel):
    auction_id: int
    user_id: str
    real_price: int
    secret_salt: str
    signature: str

class ChangePhaseRequestDTO (BaseModel):
    auction_id: int
    new_phase: str


