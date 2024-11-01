from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from data.db_secrets import user,password,host,port,database


from .models import Base,UserAccount,WorkingHours,Restaurant,Reservation,DiningTable

DATABASE_URL=f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)