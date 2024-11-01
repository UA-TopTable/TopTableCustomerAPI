from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base


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

    dining_tables = relationship("DiningTable", back_populates="restaurant",lazy="joined")

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key in ['created_date', 'updated_date']:
            if key in result and result[key] is not None:
                result[key] = result[key].isoformat()
        for key in ['location_latitude', 'location_longitude']:
            if key in result and result[key] is not None:
                result[key] = float(result[key])
        return result