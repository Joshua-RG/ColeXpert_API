# modulos externos
from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from datetime import datetime

# modulos internos
from config.db import get_db

from models.payment_model import payments

from schemas.payment_schemas import PaymentResponse, PaymentRequest, PaymentUpdate
from schemas.auth_schemas import Token

from services.auth_services import read_access_token
from services.item_services import get_item_by_id
from services.user_services import get_user_by_id

def get_role(token: Token) -> str:
    token_data = read_access_token(token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token_data.role

def get_all_payments(token: Token) -> list[PaymentResponse]:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            query = select(payments)

            result = db.execute(query).mappings().fetchall()
            payments_db = []

            for payment in result:
                payment_db = PaymentResponse(
                    id = payment["id"],
                    amount = payment["amount"],
                    method = payment["method"],
                    date = payment["date"],
                    state = payment["state"],
                    item_name = get_item_by_id(payment["item_id"], token).name,
                    user_name = get_user_by_id(payment["user_id"]).name
                )
                payments_db.append(payment_db)

            return payments_db

        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
def get_payment_by_id(id: int, token: Token) -> PaymentResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
    
            query = select(payments).where(payments.c.id == id)
            result = db.execute(query).mappings().fetchone()
            payment_db = PaymentResponse(
                id = result["id"],
                amount = result["amount"],
                method = result["method"],
                date = result["date"],
                state = result["state"],
                item_name = get_item_by_id(result["item_id"], token).name,
                user_name = get_user_by_id(result["user_id"]).name
            )
            return payment_db

        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def create_payment(payment: PaymentRequest, token: Token) -> PaymentResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            item = get_item_by_id(payment.item_id, token)
    
            query = payments.insert().values(
                amount = item.final_price,
                method = "PAYPAL",
                date = datetime.now(),
                state = "PENDING",
                item_id = payment.item_id,
                user_id = payment.user_id
            )
            db.execute(query)
            db.commit()

            payment_response = PaymentResponse(
                amount = item.final_price,
                method = "PAYPAL",
                date = datetime.now(),
                state = "PENDING",
                item_name = get_item_by_id(payment.item_id, token).name,
                user_name = get_user_by_id(payment.user_id).name
            )
            return payment_response

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    
def update_payment(id: int, payment: PaymentUpdate, token: Token) -> PaymentResponse:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
    
            payment_db = db.execute(select(payments).where(payments.c.id == id)).mappings().fetchone()
            if not payment_db:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
            amount = None
            if payment.item_id:
                amount = get_item_by_id(payment.item_id, token).final_price
    
    
            payment_updated = {
                "amount": payment.amount if amount else payment_db.amount,
                "date": payment.date if payment.date else payment_db.date,
                "state": payment.state if payment.state else payment_db.state,
                "item_id": payment.item_id if payment.item_id else payment_db.item_id,
                "user_id": payment.user_id if payment.user_id else payment_db.user_id
            }
            query = payments.update().where(payments.c.id == id).values(payment_updated)
            
            db.execute(query)
            db.commit()
            return get_payment_by_id(id, token)
    
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def delete_payment_by_id(id: int, token: Token) -> None:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            query = payments.delete().where(payments.c.id == id)

            db.execute(query)
            db.commit()
    
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")