# modulos externos
from fastapi import HTTPException, status

from sqlalchemy import select

from datetime import datetime

# modulos internos
from config.db import conn

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
    
    query = select(payments)

    try:
        result = conn.execute(query).mappings().fetchall()
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

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Payments not found")
    
def get_payment_by_id(id: int, token: Token) -> PaymentResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = select(payments).where(payments.c.id == id)

    try:
        result = conn.execute(query).mappings().fetchone()
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

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Payment not found")

def create_payment(payment: PaymentRequest, token: Token) -> PaymentResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    item = get_item_by_id(payment.item_id, token)
    
    query = payments.insert().values(
        amount = item.final_price,
        method = "PAYPAL",
        date = datetime.now(),
        state = "PENDING",
        item_id = payment.item_id,
        user_id = payment.user_id
    )

    try:
        conn.execute(query)
        conn.commit()

        payment_response = PaymentResponse(
            amount = item.final_price,
            method = "PAYPAL",
            date = datetime.now(),
            state = "PENDING",
            item_name = get_item_by_id(payment.item_id, token).name,
            user_name = get_user_by_id(payment.user_id).name
        )
        return payment_response

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Payment not created")
    
def update_payment(id: int, payment: PaymentUpdate, token: Token) -> PaymentResponse:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    payment_db = conn.execute(select(payments).where(payments.c.id == id)).mappings().fetchone()
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

    try:
        conn.execute(query)
        conn.commit()
        return get_payment_by_id(id, token)
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Payment not updated")   

def delete_payment_by_id(id: int, token: Token) -> None:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = payments.delete().where(payments.c.id == id)

    try:
        conn.execute(query)
        conn.commit()
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Payment not deleted")
