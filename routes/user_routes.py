# modulos externos
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# modulos internos
from schemas.user_schemas import UserLogin, UserRequest, UserResponse, UserUpdate
from schemas.auth_schemas import Token

from services.user_services import get_all_users, create_admin, update_user, delete_user_by_id

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/")
def get_users(token: Token = Depends(oauth2_scheme)):
    return get_all_users(token)

@router.post("/")
def post_user(user: UserRequest, token: Token = Depends(oauth2_scheme)):
    return create_admin(user, token)

@router.put("/{id}")
def put_user(id: int, user: UserUpdate, token: Token = Depends(oauth2_scheme)):
    return update_user(id, user, token)

@router.delete("/{id}")
def delete_user(id: int, token: Token = Depends(oauth2_scheme)):
    return delete_user_by_id(id, token)
