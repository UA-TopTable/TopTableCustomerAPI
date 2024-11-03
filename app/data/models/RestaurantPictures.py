from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class RestaurantPictures(Base):
    __tablename__ = 'RestaurantPictures'

    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(Text)
    restaurant_id = Column(Integer, ForeignKey('Restaurant.id'), nullable=False)

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return result

