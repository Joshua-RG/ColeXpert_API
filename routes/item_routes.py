# modulos externos
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# modulos internos
from schemas.item_schemas import ItemRequest, ItemUpdate
from schemas.auth_schemas import Token

from services.item_services import get_all_items, create_item, get_item_by_id, update_item, delete_item_by_id

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/")
def get_items(token: Token = Depends(oauth2_scheme)):
    return get_all_items(token)

@router.get("/{id}")
def get_item(id: int, token: Token = Depends(oauth2_scheme)):
    return get_item_by_id(id, token)

@router.post("/")
def post_item(item: ItemRequest, token: Token = Depends(oauth2_scheme)):
    return create_item(item, token)

@router.put("/{id}")
def put_item(id: int, item: ItemUpdate, token: Token = Depends(oauth2_scheme)):
    return update_item(id, item, token)

@router.delete("/{id}")
def delete_item(id: int, token: Token = Depends(oauth2_scheme)):
    return delete_item_by_id(id, token)