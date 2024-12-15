from sqlalchemy import Column, Enum, Integer, String, Text, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base
from enum import Enum as PyEnum

class FoodCategoryEnum(PyEnum):
    PORTUGUESE = "Portuguese"
    TURKISH = "Turkish"
    ITALIAN = "Italian"
    BURGER = "Burger"
    JAPANESE = "Japanese"
    CHINESE = "Chinese"
    INDIAN = "Indian"
    THAI = "Thai"
    MEXICAN = "Mexican"
    GREEK = "Greek"
    LEBANESE = "Lebanese"
    FRENCH = "French"
    SPANISH = "Spanish"
    KOREAN = "Korean"
    VIETNAMESE = "Vietnamese"
    SUSHI = "Sushi"
    VEGETARIAN = "Vegetarian"
    VEGAN = "Vegan"
    FAST_FOOD = "Fast Food"
    PIZZERIA = "Pizzeria"
    BARBECUE = "Barbecue"
    STEAKHOUSE = "Steakhouse"
    CREPERIE = "Creperie"
    CAJUN = "Cajun"
    TUNISIAN = "Tunisian"
    MOROCCAN = "Moroccan"
    AFRICAN = "African"
    ORIENTAL = "Oriental"
    BRAZILIAN = "Brazilian"
    AMERICAN = "American"
    FUSION = "Fusion"
    STREET_FOOD = "Street Food"
    BISTRO = "Bistro"
    SANDWICH_SHOP = "Sandwich Shop"
    SEAFOOD = "Seafood"
    TAPAS = "Tapas"
    RACLETTE_FONDUE = "Raclette/Fondue"


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
    food_category = Column(Enum(FoodCategoryEnum))

    dining_tables = relationship("DiningTable", back_populates="restaurant",lazy="joined")

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key in ['created_date', 'updated_date']:
            if key in result and result[key] is not None:
                result[key] = result[key].isoformat()
        for key in ['location_latitude', 'location_longitude']:
            if key in result and result[key] is not None:
                result[key] = float(result[key])
        result['food_category'] = result['food_category'].value
        return result