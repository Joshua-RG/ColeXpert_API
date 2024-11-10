from pydantic import BaseModel, constr
from typing_extensions import Annotated

class CategoryRequest(BaseModel):
    name: Annotated[str, constr(max_length=255)]

class CategoryResponse(BaseModel):
    id: int
    name: str