# modulos externos
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# modulos internos
from config.db import get_db
from models.bid_model import bids
from models.user_model import users
from schemas.bid_schemas import BidResponse, BidRequest, BidUpdate
from schemas.auth_schemas import Token
from schemas.item_schemas import ItemUpdate
from services.auth_services import read_access_token
from services.auction_services import get_auction_by_id
from services.user_services import get_user_by_id
from services.item_services import get_item_id_by_name, get_item_by_id, update_item

def get_role(token: Token) -> str:
    with get_db() as db:
        token_data = read_access_token(token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return token_data.role

def get_all_bids(token: Token) -> list[BidResponse]:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            query = select(bids)
            result = db.execute(query).mappings().all()
            bids_db = []

            for bid in result:
                bid_db = BidResponse(
                    id = bid["id"],
                    amount = bid["amount"],
                    date = bid["date"],
                    auction_name = get_auction_by_id(bid["auction_id"], token).name,
                    user_name = get_user_by_id(bid["user_id"]).name
                )
                bids_db.append(bid_db)

            return bids_db

        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_bid_by_id(id: int, token: Token) -> BidResponse:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            query = select(bids).where(bids.c.id == id)
            result = db.execute(query).mappings().first()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bid with id {id} not found")
            
            bid_db = BidResponse(
                id = result["id"],
                amount = result["amount"],
                date = result["date"],
                auction_name = get_auction_by_id(result["auction_id"], token).name,
                user_name = get_user_by_id(result["user_id"]).name
            )

            return bid_db

        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def create_bid(bid: BidRequest, token: Token) -> BidResponse:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            token_email = read_access_token(token).email
            user = db.execute(select(users).where(users.c.email == token_email)).mappings().first()

            item_name = get_auction_by_id(bid.auction_id, token).item_name
            item_id = get_item_id_by_name(item_name)
            
            new_bid = {
                "amount": bid.amount,
                "date": datetime.now(),
                "auction_id": bid.auction_id,
                "user_id": user["id"]
            }
            
            result = db.execute(bids.insert().values(new_bid))
            db.commit()

            bid_id = result.inserted_primary_key[0]

            final_price = float(get_item_by_id(item_id, token).final_price) + bid.amount
            update_item(item_id, ItemUpdate(final_price=final_price, user_id=user["id"]), token)

            bid_response = BidResponse(
                id = bid_id,
                amount = bid.amount,
                date = datetime.now(),
                auction_name = get_auction_by_id(bid.auction_id, token).name,
                user_name = user["name"]
            )
            return bid_response

        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def update_bid(id: int, bid: BidUpdate, token: Token) -> BidResponse:
    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            bid_db = db.execute(select(bids).where(bids.c.id == id)).mappings().first()
            if not bid_db:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bid not found")
            
            bid_updated = {
                "amount": bid.amount or bid_db["amount"],
                "date": bid.date or bid_db["date"],
                "auction_id": bid.auction_id or bid_db["auction_id"],
                "user_id": bid.user_id or bid_db["user_id"]
            }
            db.execute(bids.update().where(bids.c.id == id).values(bid_updated))
            db.commit()
            return get_bid_by_id(id, token)
        
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def delete_bid_by_id(id: int, token: Token) -> None:
    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            db.execute(bids.delete().where(bids.c.id == id))
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")