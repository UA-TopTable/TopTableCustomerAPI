from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from . import Base


class DiningTable(Base,SerializerMixin):
    __tablename__ = 'DiningTable'

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text)
    table_number = Column(String(3), nullable=False)
    number_of_seats = Column(Integer, nullable=False)
    table_type = Column(Enum('indoor', 'outdoor'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('Restaurant.id'), nullable=False)

    restaurant = relationship("Restaurant", back_populates="dining_tables",lazy="joined")
    reservations = relationship("Reservation", back_populates="dining_table",lazy="joined")

    serialize_rules=("-reservations.dining_tables",)

    def to_dict(self):
        data=super().to_dict()
        data["table_type"]=str(self.table_type)
        return data

