from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class DiningTable(Base):
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

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        result["table_type"]=str(self.table_type)
        return result

