from pydantic import BaseModel

class CommitRequestDTO (BaseModel):
    user_id: str
    hash_value: str

class RevealRequestDTO (BaseModel):
    user_id: str
    real_price: int
    secret_salt: str

class ChangePhaseRequestDTO (BaseModel):
    new_phase: str