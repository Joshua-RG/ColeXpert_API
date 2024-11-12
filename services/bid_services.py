# modulos externos
from fastapi import HTTPException, status

from sqlalchemy import select

from datetime import datetime

# modulos internos
from config.db import conn

from models.bid_model import bids
from models.user_model import users

from schemas.bid_schemas import BidResponse, BidRequest, BidUpdate
from schemas.auth_schemas import Token
from schemas.user_schemas import UserResponse
from schemas.item_schemas import ItemUpdate

from services.auth_services import read_access_token
from services.auction_services import get_auction_by_id
from services.user_services import get_user_by_id
from services.item_services import get_item_id_by_name, get_item_by_id, update_item

def get_role(token: Token) -> str:
    token_data = read_access_token(token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token_data.role

def get_all_bids(token: Token) -> list[BidResponse]:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = select(bids)

    try:
        result = conn.execute(query).mappings().fetchall()
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

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Bids not found")

def get_bid_by_id(id: int, token: Token) -> BidResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = select(bids).where(bids.c.id == id)

    try:
        result = conn.execute(query).mappings().fetchone()
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"bid with id {id} not found")
        
        bid_db = BidResponse(
            id = result["id"],
            amount = result["amount"],
            date = result["date"],
            auction_name = get_auction_by_id(result["auction_id"], token).name,
            user_name = get_user_by_id(result["user_id"]).name
        )

        return bid_db

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"bid with id {id} not found")

def create_bid(bid: BidRequest, token: Token) -> BidResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    token_email = read_access_token(token).email
    user = conn.execute(select(users).where(users.c.email == token_email)).mappings().fetchone()

    item_name = get_auction_by_id(bid.auction_id, token).item_name
    item_id = get_item_id_by_name(item_name)
    
    query = bids.insert().values(
        amount = bid.amount,
        date = datetime.now(),
        auction_id = bid.auction_id,
        user_id = user["id"]
    )

    try:
        conn.execute(query)
        conn.commit()

        final_price = float(get_item_by_id(item_id, token).final_price) + bid.amount
        update_item(item_id, ItemUpdate(final_price = final_price, user_id = user["id"]), token)
        print("final_price", final_price)
        print("user_id", user["id"])

        bid_response = BidResponse(
            amount = bid.amount,
            date = datetime.now(),
            auction_name = get_auction_by_id(bid.auction_id, token).name,
            user_name = user["name"]
        )
        return bid_response

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="bid not created")

def update_bid(id: int, bid: BidUpdate, token: Token) -> BidResponse:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    bid_db = conn.execute(select(bids).where(bids.c.id == id)).mappings().fetchone()
    if not bid_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="bid not found")
    
    bid_updated = {
        "amount": bid.amount if bid.amount else bid_db.amount,
        "date": bid.date if bid.date else bid_db.date,
        "auction_id": bid.auction_id if bid.auction_id else bid_db.auction_id,
        "user_id": bid.user_id if bid.user_id else bid_db.user_id
    }
    query = bids.update().where(bids.c.id == id).values(bid_updated)

    try:
        conn.execute(query)
        conn.commit()
        return get_bid_by_id(id, token)
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="bid not updated")

def delete_bid_by_id(id: int, token: Token) -> None:

    role = get_role(token)
    if not role or role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = bids.delete().where(bids.c.id == id)

    try:
        conn.execute(query)
        conn.commit()
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="bid not deleted")
