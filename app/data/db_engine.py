from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from db_secrets import DATABASE_URL

Base = declarative_base(DATABASE_URL)
engine = create_engine()
Base.metadata.create_all(engine)