import os
user = os.getenv("DB_USER", "admin")
password = os.getenv("DB_PASSWD", "admin123")
host = os.getenv("DB_HOST", "toptable-rds.c5uwuy0ymmo8.us-east-1.rds.amazonaws.com")
port = int(os.getenv("DB_PORT", 3306))
database = os.getenv("DB_NAME", "toptable")
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"