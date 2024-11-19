# modulos externos
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

# modulos internos
from config.db import get_db
from models.auction_model import auctions
from models.user_model import users
from schemas.auction_schemas import AuctionResponse, AuctionRequest, AuctionUpdate
from schemas.payment_schemas import PaymentRequest
from schemas.auth_schemas import Token
from services.auth_services import read_access_token
from services.item_services import get_item_by_id
from services.payment_services import create_payment

def get_role(token: Token) -> str:
    with get_db() as db:
        token_data = read_access_token(token)
        if not token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return token_data.role

def get_all_auctions(token: Token) -> list[AuctionResponse]:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            query = select(auctions)
            result = db.execute(query).mappings().all()
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

        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def get_auction_by_id(id: int, token: Token) -> AuctionResponse:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            query = select(auctions).where(auctions.c.id == id)
            result = db.execute(query).mappings().first()
            if not result:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
            
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
        
        except SQLAlchemyError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def create_auction(auction: AuctionRequest, token: Token) -> AuctionResponse:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    now = datetime.now(timezone.utc)

    if auction.start_date < now or auction.end_date < now or auction.start_date > auction.end_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dates")
    
    now_date = now if auction.state == "EN CURSO" else None
    
    with get_db() as db:
        try:
            new_auction = {
                "name": auction.name,
                "description": auction.description,
                "start_date": auction.start_date if now_date is None else now_date,
                "end_date": auction.end_date,
                "type": auction.type,
                "state": auction.state,
                "item_id": auction.item_id
            }
            
            result = db.execute(auctions.insert().values(new_auction))
            db.commit()

            auction_id = result.inserted_primary_key[0]
            auction_response = AuctionResponse(
                id = auction_id,
                name = auction.name,
                description = auction.description,
                start_date = auction.start_date,
                end_date = auction.end_date,
                type = auction.type,
                state = auction.state,
                item_name = get_item_by_id(auction.item_id, token).name
            )
            return auction_response
        
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def update_auction(id: int, auction: AuctionUpdate, token: Token) -> AuctionResponse:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            auction_db = db.execute(select(auctions).where(auctions.c.id == id)).mappings().first()
            if not auction_db:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
            
            item = get_item_by_id(auction_db["item_id"], token)
            item_user_id = db.execute(select(users).where(users.c.name == item.user_name)).first().id
            if auction.state == "FINALIZADA" and auction_db["state"] == "EN CURSO":
                create_payment(PaymentRequest(item_id=auction_db["item_id"], user_id=item_user_id), token)

            if auction.state == "EN CURSO" and auction_db["state"] == "FINALIZADA":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction already finished")
            
            start_date = datetime.now(timezone.utc) if auction.state == "EN CURSO" else auction_db["start_date"]
            
            auction_updated = {
                "name": auction.name or auction_db["name"],
                "description": auction.description or auction_db["description"],
                "start_date": auction.start_date or start_date,
                "end_date": auction.end_date or auction_db["end_date"],
                "type": auction.type or auction_db["type"],
                "state": auction.state or auction_db["state"],
                "item_id": auction.item_id or auction_db["item_id"]
            }
            db.execute(auctions.update().where(auctions.c.id == id).values(auction_updated))
            db.commit()
            return get_auction_by_id(id, token)
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")

def delete_auction_by_id(id: int, token: Token) -> None:
    role = get_role(token)
    if not role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    
    with get_db() as db:
        try:
            db.execute(auctions.delete().where(auctions.c.id == id))
            db.commit()
        except SQLAlchemyError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")