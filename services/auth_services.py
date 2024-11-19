# modulos externos
import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from passlib.context import CryptContext

# modulos internos
from config.db import get_db
from models.user_model import users
from schemas.user_schemas import UserLogin, UserResponse, UserRequest
from schemas.auth_schemas import Token

SECRET_KEY = "6484e5ac05dedf7949f015c1bb9478bf8f2087dc3bf3b54a9c696b8a3c166be87a1582096e7a93431ee7240e8e2a2d3e971c775da7bf9885cd9ea77a46b8fbba"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 420

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(user: UserLogin):
    with get_db() as db:
        try:
            query = select(users).where(users.c.email == user.email)
            user_db = db.execute(query).fetchone()
            if not user_db:
                return False
            if not verify_password(user.password, user_db.password):
                return False
            return user_db
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def login_user(user: UserLogin) -> Token:
    user_db = authenticate_user(user)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user_db.email})

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user_db.id,
        user_name=user_db.name,
        user_email=user_db.email,
        user_role=user_db.role,
        user_img=user_db.img
    )

def read_access_token(token: str) -> UserResponse:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not validate credentials: {str(e)}")
    
    with get_db() as db:
        try:
            query = select(users).where(users.c.email == email)
            user_db = db.execute(query).fetchone()
            if not user_db:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
            return UserResponse(
                id=user_db.id,
                name=user_db.name,
                email=user_db.email,
                adress=user_db.adress,
                role=user_db.role,
                phone=user_db.phone,
                img=user_db.img
            )
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def create_user(user: UserRequest) -> UserResponse:
    hashed_password = hash_password(user.password)
    with get_db() as db:
        try:
            new_user = {
                "name": user.name,
                "email": user.email,
                "password": hashed_password,
                "role": "USER",
                "adress": user.adress,
                "phone": user.phone,
                "created_at": datetime.now(),
                "img": user.img
            }
            result = db.execute(users.insert().values(new_user))
            db.commit()

            user_id = result.inserted_primary_key[0]
            return UserResponse(
                id=user_id,
                name=user.name,
                email=user.email,
                adress=user.adress,
                role="USER",
                phone=user.phone,
                img=user.img
            )
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Could not create user: {str(e)}")