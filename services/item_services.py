# modulos externos
from fastapi import HTTPException, status

from sqlalchemy import select

from datetime import datetime

# modulos internos
from config.db import conn

from models.item_model import items

from schemas.item_schemas import ItemResponse, ItemRequest, ItemUpdate
from schemas.auth_schemas import Token

from services.auth_services import read_access_token
from services.category_services import get_category_by_id
from services.user_services import get_user_by_id

def get_role(token: Token) -> str:
    token_data = read_access_token(token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token_data.role

def get_all_items(token: Token) -> list[ItemResponse]:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = select(items)

    try:
        result = conn.execute(query).mappings().fetchall()
        items_db = []

        for item in result:
            category = get_category_by_id(item["category_id"], token)
            user = get_user_by_id(item["user_id"]) if item["user_id"] else None
            item_db = ItemResponse(
                id = item["id"],
                name = item["name"],
                description = item["description"],
                img = item["img"],
                init_price = item["init_price"],
                final_price = item["final_price"],
                category_name = category.name,
                user_name = user.name if user else None
            )
            items_db.append(item_db)

        return items_db
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Items not found{e}")
    
def get_item_by_id(id: int, token: Token) -> ItemResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = select(items).where(items.c.id == id)

    try:
        result = conn.execute(query).mappings().fetchone()
        item_db = ItemResponse(
            id = result["id"],
            name = result["name"],
            description = result["description"],
            img = result["img"],
            init_price = result["init_price"],
            final_price = result["final_price"],
            category_name = get_category_by_id(result["category_id"], token).name,
            user_name = get_user_by_id(result["user_id"]).name if result["user_id"] else None
        )
        return item_db
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Item not found{e}")

def get_item_id_by_name(name: str) -> int:
    
        query = select(items).where(items.c.name == name)
    
        try:
            result = conn.execute(query).mappings().fetchone()
            return result["id"]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Item not found{e}")

def create_item(item: ItemRequest, token: Token) -> ItemResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = items.insert().values(
        name = item.name,
        description = item.description,
        img = item.img,
        created_at = datetime.now(),
        init_price = item.init_price,
        final_price = item.init_price,
        category_id = item.category_id,
        user_id = item.user_id
    )

    try:
        conn.execute(query)
        conn.commit()

        query2 = select(items).where(items.c.name == item.name)
        item_db = conn.execute(query2).fetchone()

        item_db = ItemResponse(
            id = item_db.id,
            name = item.name,
            description = item.description,
            img = item.img,
            init_price = item.init_price,
            final_price = item_db.final_price,
            category_name = get_category_by_id(item.category_id, token).name,
            user_name = get_user_by_id(item.user_id).name if item.user_id else None
        )
        return item_db
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Item not created")
    
def update_item(id: int, item: ItemUpdate, token: Token) -> ItemResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    item_db = conn.execute(select(items).where(items.c.id == id)).mappings().fetchone()
    if not item_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    item_updated = {
        "name": item.name if item.name else item_db["name"],
        "description": item.description if item.description else item_db["description"],
        "img": item.img if item.img else item_db["img"],
        "final_price": item.final_price if item.final_price else item_db["final_price"],
        "category_id": item.category_id if item.category_id else item_db["category_id"],
        "user_id": item.user_id if item.user_id else item_db["user_id"]
    }
    query = items.update().where(items.c.id == id).values(item_updated)

    try:
        conn.execute(query)
        conn.commit()
        return get_item_by_id(id, token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Item not updated")

def delete_item_by_id(id: int, token: Token) -> None:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = items.delete().where(items.c.id == id)

    try:
        conn.execute(query)
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Item not deleted")