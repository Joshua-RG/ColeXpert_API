# modulos externos
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# modulos internos
from schemas.payment_schemas import PaymentResponse, PaymentRequest, PaymentUpdate
from schemas.auth_schemas import Token

from services.payment_services import get_all_payments, create_payment, get_payment_by_id, update_payment, delete_payment_by_id

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/")
def get_payments(token: Token = Depends(oauth2_scheme)):
    return get_all_payments(token)

@router.get("/{id}")
def get_payment(id: int, token: Token = Depends(oauth2_scheme)):
    return get_payment_by_id(id, token)

@router.post("/")
def post_payment(payment: PaymentRequest, token: Token = Depends(oauth2_scheme)):
    return create_payment(payment, token)

@router.put("/{id}")
def put_payment(id: int, payment: PaymentUpdate, token: Token = Depends(oauth2_scheme)):
    return update_payment(id, payment, token)

@router.delete("/{id}")
def delete_payment(id: int, token: Token = Depends(oauth2_scheme)):
    return delete_payment_by_id(id, token)