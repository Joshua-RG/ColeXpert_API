from pydantic import BaseModel, constr
from typing_extensions import Annotated
from typing import Optional

class ItemRequest(BaseModel):
    name: Annotated[str, constr(max_length=255)]
    description: Annotated[str, constr(max_length=255)]
    img: Optional[str] = None
    init_price: float
    category_id: int
    user_id: Optional[int] = None

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    img: Optional[str] = None
    init_price: float
    final_price: float
    category_name: str
    user_name: Optional[str] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    img: Optional[str] = None
    final_price: Optional[float] = None
    category_id: Optional[int] = None
    user_id: Optional[int] = None 

