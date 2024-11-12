from sqlalchemy import DateTime, Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Float, Text
from sqlalchemy.sql import func
from config.db import meta, engine

items = Table('items', meta,
              Column("id", Integer, primary_key=True, index=True, autoincrement=True),
              Column("name", String(255), nullable=False, unique=True),
              Column("description", String(255), nullable=False),
              Column("img", Text, nullable=True),
              Column("created_at", DateTime(timezone=True), server_default=func.now()),
              Column("init_price", Float, nullable=False),
              Column("final_price", Float, nullable=True),
              Column("category_id", Integer, ForeignKey("categories.id"), nullable=False),
              Column("user_id", Integer, ForeignKey("users.id"), nullable=True))

meta.create_all(engine)