from pydantic import BaseModel, constr
from typing_extensions import Annotated
from typing import Optional
from datetime import datetime

class PaymentRequest(BaseModel):
    item_id: int
    user_id: int

class PaymentResponse(BaseModel):
    id: Optional[int] = None
    amount: float
    method: str
    date: datetime
    state: str
    item_name: str
    user_name: str

class PaymentUpdate(BaseModel):
    date: Optional[datetime] = None
    state: Optional[str] = None
    item_id: Optional[int] = None
    user_id: Optional[int] = None