import os
from flask import Flask

app = Flask(__name__)

app.config.update({
    'AWS_REGION':os.environ['AWS_REGION'],
    'AWS_COGNITO_USER_POOL_ID':os.environ['AWS_COGNITO_USER_POOL_ID'],
    'AWS_COGNITO_DOMAIN':os.environ['AWS_COGNITO_DOMAIN'],
    'AWS_COGNITO_USER_POOL_CLIENT_ID':os.environ['AWS_COGNITO_USER_POOL_CLIENT_ID'],
    'AWS_COGNITO_REDIRECT_URL':'localhost:5000/redirect'
})