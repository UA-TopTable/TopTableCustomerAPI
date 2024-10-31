from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Reservation(Base):
    __tablename__ = 'Reservation'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('UserAccount.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('Restaurant.id'), nullable=False)
    dining_table_id = Column(Integer, ForeignKey('DiningTable.id'), nullable=False)
    number_of_people = Column(Integer, nullable=False)
    reservation_start_time = Column(DateTime, nullable=False)
    reservation_end_time = Column(DateTime, nullable=False)
    status = Column(Enum('pending', 'confirmed', 'cancelled'), nullable=False)
    special_requests = Column(Text)
    reservation_code = Column(String(10), unique=True, nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('number_of_people > 0'),
        CheckConstraint('reservation_end_time > reservation_start_time'),
    )