import os
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN", "BLAH.us-east-1.amazoncognito.com")
AWS_COGNITO_USER_POOL_CLIENT_ID = os.getenv("COGNITO_USER_POOL_CLIENT_ID", "IDX")
AWS_COGNITO_USER_POOL_CLIENT_SECRET = os.getenv("COGNITO_USER_POOL_CLIENT_SECRET", "SECRE13T")
API_URL = os.getenv("API_URL", "http://localhost:5000")
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "test")
APP_PORT = os.getenv("PORT", 5000)