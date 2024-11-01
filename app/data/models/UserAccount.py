from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin
from . import Base

class UserAccount(Base,SerializerMixin):
    __tablename__ = 'UserAccount'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15))
    profile_image_url = Column(String(255))
    user_type = Column(Enum('admin', 'customer', 'staff'), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        data=super().to_dict
        data["user_type"]=str(self.user_type)
        return data