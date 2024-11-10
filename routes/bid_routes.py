# modulos externos
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# modelos internos
from schemas.bid_schemas import BidResponse, BidRequest, BidUpdate
from schemas.auth_schemas import Token

from services.bid_services import get_all_bids, get_bid_by_id, create_bid, update_bid, delete_bid_by_id

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/")
def get_bids(token: Token = Depends(oauth2_scheme)):
    return get_all_bids(token)

@router.get("/{id}")
def get_bid(id: int, token: Token = Depends(oauth2_scheme)):
    return get_bid_by_id(id, token)

@router.post("/")
def post_bid(bid: BidRequest, token: Token = Depends(oauth2_scheme)):
    return create_bid(bid, token)

@router.put("/{id}")
def put_bid(id: int, bid: BidUpdate, token: Token = Depends(oauth2_scheme)):
    return update_bid(id, bid, token)

@router.delete("/{id}")
def delete_bid(id: int, token: Token = Depends(oauth2_scheme)):
    return delete_bid_by_id(id, token)