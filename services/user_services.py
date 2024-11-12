# modulos externos
from fastapi import HTTPException, status

from sqlalchemy import select

from passlib.context import CryptContext

from datetime import datetime

# modulos internos
from config.db import conn

from models.user_model import users

from schemas.user_schemas import UserResponse, UserRequest, UserUpdate
from schemas.auth_schemas import Token

from services.auth_services import read_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def is_admin(token: Token) -> bool:
    token_data = read_access_token(token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if token_data.role != "ADMIN":
        return False
    return True

def get_all_users(token: Token) -> list[UserResponse]:

    if not is_admin(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    query = select(users)

    try:
        result = conn.execute(query).mappings().fetchall()
        users_db = [
            UserResponse(
                id = user["id"],
                name = user["name"],
                email = user["email"],
                adress = user["adress"],
                role = user["role"],
                phone = user["phone"],
                img = user["img"],
            ) for user in result
        ]
        return users_db
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Users not found {str(e)}")
    
def create_admin(user: UserRequest, token: Token) -> UserResponse:

    if not is_admin(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    hashed_password = hash_password(user.password)
    query = users.insert().values(
        name = user.name,
        email = user.email,
        password = hashed_password,
        role = "ADMIN",
        adress = user.adress,
        phone = user.phone,
        created_at = datetime.now(),
        img = user.img
    )

    try:
        conn.execute(query)
        conn.commit()

        query2 = select(users).where(users.c.email == user.email)
        user_db = conn.execute(query2).fetchone()

        return UserResponse(
            id=user_db.id,
            name=user.name,
            email=user.email,
            adress=user.adress,
            role="ADMIN",
            phone=user.phone,
            img=user.img
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"User not created {str(e)}")
    
def get_user_by_id(id: int) -> UserResponse:

    query = select(users).where(users.c.id == id)

    try:
        result = conn.execute(query).mappings().fetchone()
        user_db = UserResponse(
            id = result["id"],
            name = result["name"],
            email = result["email"],
            adress = result["adress"],
            role = result["role"],
            phone = result["phone"],
            img = result["img"]
        )

        return user_db
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"User not found")

def update_user(id: int, user: UserUpdate, token: Token) -> UserResponse:

    if not is_admin(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    user_db = conn.execute(select(users).where(users.c.id == id)).mappings().fetchone()
    if not user_db:
        raise ValueError("User not found")
    
    user_updated = {
        "name": user_db["name"] if user.name is None else user.name,
        "email": user_db["email"] if user.email is None else user.email,
        "password": user_db["password"] if user.password is None else hash_password(user.password),
        "adress": user_db["adress"] if user.adress is None else user.adress,
        "phone": user_db["phone"] if user.phone is None else user.phone,
        "img": user_db["img"] if user.img is None else user.img
    }

    query = users.update().where(users.c.id == id).values(user_updated)

    try:
        conn.execute(query)
        conn.commit()
        return get_user_by_id(id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"User not updated")
    
def delete_user_by_id(id: int, token: Token) -> None:

    if not is_admin(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    query = users.delete().where(users.c.id == id)

    try:
        conn.execute(query)
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"User not deleted")