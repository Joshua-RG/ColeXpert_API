from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from typing_extensions import Annotated

class UserRequest(BaseModel):
    name: Annotated[str, constr(max_length=100)]
    email: EmailStr
    password: Annotated[str, constr(min_length=5, max_length=255)]
    adress: Optional[Annotated[str, constr(max_length=255)]] = None
    phone: Optional[Annotated[str, constr(max_length=15)]] = None
    img: Optional[Annotated[str, constr(max_length=255)]] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    adress: Optional[str] = None
    role: str
    phone: Optional[str] = None
    img: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[Annotated[str, constr(max_length=100)]] = None
    email: Optional[EmailStr] = None
    password: Optional[Annotated[str, constr(min_length=5, max_length=255)]] = None
    adress: Optional[Annotated[str, constr(max_length=255)]] = None
    phone: Optional[Annotated[str, constr(max_length=15)]] = None
    img: Optional[Annotated[str, constr(max_length=255)]] = None

class UserLogin(BaseModel):
    email: EmailStr 
    password: str

class User(BaseModel):
    name: str
    email: EmailStr
