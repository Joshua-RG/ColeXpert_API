from sqlalchemy import DateTime, Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine

auctions = Table('auctions', meta,
                 Column("id", Integer, primary_key=True, index=True, autoincrement=True),
                 Column("name", String(255), nullable=False, unique=True),
                 Column("description", String(255), nullable=False),
                 Column("start_date", DateTime(timezone=True), nullable=True),
                 Column("end_date", DateTime(timezone=True), nullable=True),
                 Column("type", String(255), nullable=True),
                 Column("state", String(255), nullable=True),
                 Column("item_id", Integer, ForeignKey("items.id"), nullable=False))

meta.create_all(engine)