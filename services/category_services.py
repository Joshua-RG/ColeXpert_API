# modulos externos
from fastapi import HTTPException, status

from sqlalchemy import select

# modulos internos
from config.db import conn

from models.category_model import categories

from schemas.category_schemas import CategoryResponse, CategoryRequest
from schemas.auth_schemas import Token

from services.auth_services import read_access_token

def get_role(token: Token) -> str:
    token_data = read_access_token(token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token_data.role

def get_all_categories(token: Token) -> list[CategoryResponse]:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = select(categories)

    try:
        result = conn.execute(query).mappings().fetchall()
        categories_db = [
            CategoryResponse(
                id = category["id"],
                name = category["name"]
            ) for category in result
        ]
        return categories_db
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Categories not found {e}")
    
def get_category_by_id(id: int, token: Token) -> CategoryResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = select(categories).where(categories.c.id == id)

    try:
        result = conn.execute(query).mappings().fetchone()
        category_db = CategoryResponse(
            id = result["id"],
            name = result["name"]
        )
        return category_db
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Category not found")
    
def create_category(category: CategoryRequest, token: Token) -> CategoryResponse:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = categories.insert().values(
        name = category.name
    )

    try:
        conn.execute(query)
        conn.commit()

        query2 = select(categories).where(categories.c.name == category.name)
        category_db = conn.execute(query2).fetchone()

        return CategoryResponse(
            id = category_db.id,
            name = category_db.name
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Category not created")
    
def update_category(id: int, category: CategoryRequest, token: Token) -> CategoryResponse:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    category_db = conn.execute(select(categories).where(categories.c.id == id)).mappings().fetchone()
    if not category_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    query = categories.update().where(categories.c.id == id).values({
        "name": category.name
    })

    try:
        conn.execute(query)
        conn.commit()

        return get_category_by_id(id, token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Category not updated")
    
def delete_category_by_id(id: int, token: Token) -> None:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = categories.delete().where(categories.c.id == id)

    try:
        conn.execute(query)
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Category not deleted")