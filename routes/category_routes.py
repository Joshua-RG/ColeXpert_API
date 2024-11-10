# modulos externos
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# modulos internos
from schemas.category_schemas import CategoryResponse, CategoryRequest
from schemas.auth_schemas import Token

from services.category_services import get_all_categories, get_category_by_id, create_category, update_category, delete_category_by_id

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/")
def get_categories(token: Token = Depends(oauth2_scheme)):
    return get_all_categories(token)

@router.get("/{id}")
def get_category(id: int, token: Token = Depends(oauth2_scheme)):
    return get_category_by_id(id, token)

@router.post("/")
def post_category(category: CategoryRequest, token: Token = Depends(oauth2_scheme)):
    return create_category(category, token)

@router.put("/{id}")
def put_category(id: int, category: CategoryRequest, token: Token = Depends(oauth2_scheme)):
    return update_category(id, category, token)

@router.delete("/{id}")
def delete_category(id: int, token: Token = Depends(oauth2_scheme)):
    return delete_category_by_id(id, token)