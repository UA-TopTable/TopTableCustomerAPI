from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from . import Base

class UserAccount(Base):
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

    def as_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key in ['created_date', 'updated_date']:
            if key in result and result[key] is not None:
                result[key] = result[key].isoformat()
        return result