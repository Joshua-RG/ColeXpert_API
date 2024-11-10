# modulos externos
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# modulos internos
from schemas.user_schemas import UserLogin, UserRequest
from schemas.auth_schemas import Token

from services.auth_services import login_user, read_access_token, create_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/login")
def login(user: UserLogin):
    return login_user(user)

@router.post("/register")
def register(user: UserRequest):
    return create_user(user)

@router.get("/verify_token")
def verify_token(token: Token = Depends(oauth2_scheme)):
    return read_access_token(token)
