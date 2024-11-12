# modulos externos
from fastapi import HTTPException, status

from sqlalchemy import select

from datetime import datetime, timezone

# modulos internos
from config.db import conn

from models.auction_model import auctions
from models.user_model import users

from schemas.auction_schemas import AuctionResponse, AuctionRequest, AuctionUpdate
from schemas.payment_schemas import PaymentResponse, PaymentRequest
from schemas.auth_schemas import Token

from services.auth_services import read_access_token
from services.item_services import get_item_by_id
from services.payment_services import create_payment

def get_role(token: Token) -> str:
    token_data = read_access_token(token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token_data.role

def get_all_auctions(token: Token) -> list[AuctionResponse]:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = select(auctions)

    try:
        result = conn.execute(query).mappings().fetchall()
        auctions_db = []

        for auction in result:
            auction_db = AuctionResponse(
                id = auction["id"],
                name = auction["name"],
                description = auction["description"],
                start_date = auction["start_date"],
                end_date = auction["end_date"],
                type = auction["type"],
                state = auction["state"],
                item_name = get_item_by_id(auction["item_id"], token).name
            )
            auctions_db.append(auction_db)

        return auctions_db

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Auctions not found")

def get_auction_by_id(id: int, token: Token) -> AuctionResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = select(auctions).where(auctions.c.id == id)

    try:
        result = conn.execute(query).mappings().fetchone()
        auction_response = AuctionResponse(
            id = result["id"],
            name = result["name"],
            description = result["description"],
            start_date = result["start_date"],
            end_date = result["end_date"],
            type = result["type"],
            state = result["state"],
            item_name = get_item_by_id(result["item_id"], token).name
        )
        return auction_response
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Auction not found")

def create_auction(auction: AuctionRequest, token: Token) -> AuctionResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    now = datetime.now(timezone.utc)

    if auction.start_date < now or auction.end_date < now or auction.start_date > auction.end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dates")
    
    now_date = None
    if auction.state == "EN CURSO":
        now_date = now
    
    query = auctions.insert().values(
        name = auction.name,
        description = auction.description,
        start_date = auction.start_date if now_date is None else now_date,
        end_date = auction.end_date,
        type = auction.type,
        state = auction.state,
        item_id = auction.item_id
    )

    try:
        conn.execute(query)
        conn.commit()

        query2 = select(auctions).where(auctions.c.name == auction.name)
        auction_db = conn.execute(query2).fetchone()

        auction_response = AuctionResponse(
            id = auction_db.id,
            name = auction.name,
            description = auction.description,
            start_date = auction.start_date,
            end_date = auction.end_date,
            type = auction.type,
            state = auction.state,
            item_name = get_item_by_id(auction.item_id, token).name
        )
        return auction_response
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Auction not created")
    
def update_auction(id: int, auction: AuctionUpdate, token: Token) -> AuctionResponse:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    auction_db = conn.execute(select(auctions).where(auctions.c.id == id)).mappings().fetchone()
    if not auction_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
    
    item = get_item_by_id(auction_db.item_id, token)
    item_user_id = conn.execute(select(users).where(users.c.name == item.user_name)).fetchone().id
    if auction.state is not None and auction.state == "FINALIZADA" and auction_db.state == "EN CURSO":
        create_payment(PaymentRequest(item_id=auction_db.item_id, user_id=item_user_id), token)

    if auction.state is not None and auction.state == "EN CURSO" and auction_db.state == "FINALIZADA":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction already finished")
    
    start_date = auction_db.start_date

    if auction.state is not None and auction.state == "EN CURSO":
        start_date = datetime.now(timezone.utc)
    
    auction_updated = {
        "name": auction.name if auction.name else auction_db.name,
        "description": auction.description if auction.description else auction_db.description,
        "start_date": auction.start_date if auction.start_date else start_date,
        "end_date": auction.end_date if auction.end_date else auction_db.end_date,
        "type": auction.type if auction.type else auction_db.type,
        "state": auction.state if auction.state else auction_db.state,
        "item_id": auction.item_id if auction.item_id else auction_db.item_id
    }
    query = auctions.update().where(auctions.c.id == id).values(auction_updated)

    try:
        conn.execute(query)
        conn.commit()
        return get_auction_by_id(id, token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Auction not updated")

def delete_auction_by_id(id: int, token: Token) -> None:

    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    query = auctions.delete().where(auctions.c.id == id)

    try:
        conn.execute(query)
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Auction not deleted")