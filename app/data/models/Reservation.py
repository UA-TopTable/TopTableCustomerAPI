from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base


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

    dining_table=relationship("DiningTable",back_populates="reservations",lazy="joined")

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key in ['reservation_start_time', 'reservation_end_time', 'created_date', 'updated_date']:
            if key in result and result[key] is not None:
                result[key] = result[key].isoformat()
        return result