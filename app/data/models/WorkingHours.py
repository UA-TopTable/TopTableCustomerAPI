from sqlalchemy import Column, Integer, Enum, Time, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base
Base = declarative_base()

class WorkingHours(Base):
    __tablename__ = 'WorkingHours'

    id = Column(Integer, primary_key=True, autoincrement=True)
    day_of_week = Column(Enum('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'), nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    restaurant_id = Column(Integer, ForeignKey('Restaurant.id'), nullable=False)

    __table_args__ = (
        CheckConstraint('closing_time > opening_time'),
    )