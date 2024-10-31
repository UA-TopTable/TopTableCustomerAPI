host = 'database-es-toptable.ctiwaku0ozg4.us-east-1.rds.amazonaws.com'
port = 3306
user = 'admin'
password = 'ES2024Hello?'
database = 'toptable'

host = 'localhost'
port = 3306
user = 'root'
password = 'admin123'
database = 'toptable'

DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"