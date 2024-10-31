from sqlalchemy.orm import sessionmaker
from app.data.models import UserAccount
from db_engine import engine

Session = sessionmaker(bind=engine)
session = Session()

# Query users
# users = session.query(UserAccount).all()
# for user in users:
#     print(user.full_name, user.email)

# session.close()