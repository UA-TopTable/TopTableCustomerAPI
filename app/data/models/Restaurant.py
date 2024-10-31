from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'Restaurant'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    location_address = Column(String(255))
    location_latitude = Column(DECIMAL(10, 8), nullable=False)
    location_longitude = Column(DECIMAL(11, 8), nullable=False)
    restaurant_image = Column(String(255))
    time_zone = Column(String(50))
    owner_user_id = Column(Integer, ForeignKey('UserAccount.id'))
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())