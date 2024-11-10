# modulos externos
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

# modulos internos
from schemas.auction_schemas import AuctionResponse, AuctionRequest, AuctionUpdate
from schemas.auth_schemas import Token

from services.auction_services import get_all_auctions, create_auction, get_auction_by_id, update_auction, delete_auction_by_id

router = APIRouter()    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/")
def get_auctions(token: Token = Depends(oauth2_scheme)):
    return get_all_auctions(token)

@router.get("/{id}")
def get_auction(id: int, token: Token = Depends(oauth2_scheme)):
    return get_auction_by_id(id, token)

@router.post("/")
def post_auction(auction: AuctionRequest, token: Token = Depends(oauth2_scheme)):
    return create_auction(auction, token)

@router.put("/{id}")
def put_auction(id: int, auction: AuctionUpdate, token: Token = Depends(oauth2_scheme)):
    return update_auction(id, auction, token)

@router.delete("/{id}")
def delete_auction(id: int, token: Token = Depends(oauth2_scheme)):
    return delete_auction_by_id(id, token)