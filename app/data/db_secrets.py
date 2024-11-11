import os
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWD", "xxxx")
host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", 3306))
database = os.getenv("DB_NAME", "toptable")
DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"