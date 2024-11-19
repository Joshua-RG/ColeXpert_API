# modulos externos
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

# modulos internos
from config.db import get_db
from models.category_model import categories
from schemas.category_schemas import CategoryResponse, CategoryRequest
from schemas.auth_schemas import Token
from services.auth_services import read_access_token

def get_role(token: Token) -> str:
    with get_db() as db:
        token_data = read_access_token(token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return token_data.role

def get_all_categories(token: Token) -> list[CategoryResponse]:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            query = select(categories)
            result = db.execute(query).mappings().all()
            categories_db = [
                CategoryResponse(
                    id = category["id"],
                    name = category["name"]
                ) for category in result
            ]
            return categories_db
        
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
def get_category_by_id(id: int, token: Token) -> CategoryResponse:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            query = select(categories).where(categories.c.id == id)
            result = db.execute(query).mappings().first()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
            
            category_db = CategoryResponse(
                id = result["id"],
                name = result["name"]
            )
            return category_db
        
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
def create_category(category: CategoryRequest, token: Token) -> CategoryResponse:
    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            new_category = {
                "name": category.name
            }
            result = db.execute(categories.insert().values(new_category))
            db.commit()

            category_id = result.inserted_primary_key[0]
            return CategoryResponse(
                id = category_id,
                name = category.name
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
def update_category(id: int, category: CategoryRequest, token: Token) -> CategoryResponse:
    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            category_db = db.execute(select(categories).where(categories.c.id == id)).mappings().first()
            if not category_db:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
            
            db.execute(categories.update().where(categories.c.id == id).values({"name": category.name}))
            db.commit()

            return get_category_by_id(id, token)
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
def delete_category_by_id(id: int, token: Token) -> None:
    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            db.execute(categories.delete().where(categories.c.id == id))
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")