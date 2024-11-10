from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta, engine

categories = Table('categories', meta,
                   Column("id", Integer, primary_key=True, index=True, autoincrement=True),
                   Column("name", String(255), unique=True, nullable=False))

meta.create_all(engine)