from sqlalchemy import DateTime, Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, Text
from sqlalchemy.sql import func
from config.db import meta, engine

users = Table('users', meta, 
              Column("id", Integer, primary_key=True, index=True, autoincrement=True),
              Column("name", String(100), nullable=False),
              Column("email", String(100), unique=True, nullable=False),
              Column("password", String(255), nullable=False),
              Column("role", String(50), nullable=False),
              Column("adress", String(255), nullable=True),
              Column("phone", String(15), nullable=True),
              Column("created_at", DateTime(timezone=True), server_default=func.now()),
              Column("img", Text(length=4294967295), nullable=True))

meta.create_all(engine)