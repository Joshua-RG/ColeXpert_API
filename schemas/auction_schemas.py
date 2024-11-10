from pydantic import BaseModel, constr
from typing_extensions import Annotated
from typing import Optional
from datetime import datetime

class AuctionRequest(BaseModel):
    name: Annotated[str, constr(max_length=255)]
    description: Annotated[str, constr(max_length=255)]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    type: Optional[str] = None
    state: Optional[str] = None
    item_id: int

class AuctionResponse(BaseModel):
    id: int
    name: str
    description: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    type: Optional[str] = None
    state: Optional[str] = None
    item_name: str

class AuctionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    type: Optional[str] = None
    state: Optional[str] = None
    item_id: Optional[int] = None