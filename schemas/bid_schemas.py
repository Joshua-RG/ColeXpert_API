from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BidRequest(BaseModel):
    amount: float
    auction_id: int

class BidResponse(BaseModel):
    id: Optional[int] = None
    amount: float
    date: datetime
    auction_name: str
    user_name: str

class BidUpdate(BaseModel):
    amount: Optional[float] = None
    date: Optional[datetime] = None
    auction_id: Optional[int] = None
    user_id: Optional[int] = None