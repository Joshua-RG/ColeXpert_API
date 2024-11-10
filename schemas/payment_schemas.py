from pydantic import BaseModel, constr
from typing_extensions import Annotated
from typing import Optional
from datetime import datetime

class PaymentRequest(BaseModel):
    amount: float
    method: Annotated[str, constr(max_length=255)]
    date: datetime
    state: str
    item_id: int
    user_id: int

class PaymentResponse(BaseModel):
    id: Optional[int]
    amount: float
    method: str
    date: datetime
    state: str
    item_name: str
    user_name: str

class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    method: Optional[str] = None
    date: Optional[datetime] = None
    state: Optional[str] = None
    item_id: Optional[int] = None
    user_id: Optional[int] = None