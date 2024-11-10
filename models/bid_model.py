from sqlalchemy import DateTime, Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Float
from config.db import meta, engine

bids = Table('bids', meta,
             Column("id", Integer, primary_key=True, index=True, autoincrement=True),
             Column("amount", Float, nullable=False),
             Column("date", DateTime(timezone=True), nullable=False),
             Column("auction_id", Integer, ForeignKey("auctions.id"), nullable=False),
             Column("user_id", Integer, ForeignKey("users.id"), nullable=False))

meta.create_all(engine)