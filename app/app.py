import os
import boto3
from flask import Flask,jsonify, redirect, request, session
from flask_restx import Api

from apis import blueprint,api

def create_app():
    app = Flask(__name__)
    api.init_app(app)

    app.secret_key=os.environ["FLASK_SECRET_KEY"]
    app.config.update({
        "AWS_REGION":os.environ["AWS_REGION"],
        "AWS_COGNITO_USER_POOL_ID":os.environ["AWS_COGNITO_USER_POOL_ID"],
        "AWS_COGNITO_DOMAIN":os.environ["AWS_COGNITO_DOMAIN"],
        "AWS_COGNITO_USER_POOL_CLIENT_ID":os.environ["AWS_COGNITO_USER_POOL_CLIENT_ID"],
        "AWS_COGNITO_REFRESH_FLOW_ENABLED":True,
        "AWS_COGNITO_REFRESH_COOKIE_ENCRYPTED":True,
    })

    return app