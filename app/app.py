import os
import secrets
from flask import Flask,jsonify, redirect, session, url_for

from flask_cognito_lib import CognitoAuth
from flask_cognito_lib.decorators import (
    auth_required,
    cognito_login,
    cognito_login_callback,
    cognito_logout,
    cognito_refresh_callback,
)

app = Flask(__name__)

app.secret_key=secrets.token_urlsafe(16)


app.config.update({
    "AWS_REGION":os.environ["AWS_REGION"],
    "AWS_COGNITO_USER_POOL_ID":os.environ["AWS_COGNITO_USER_POOL_ID"],
    "AWS_COGNITO_DOMAIN":os.environ["AWS_COGNITO_DOMAIN"],
    "AWS_COGNITO_USER_POOL_CLIENT_ID":os.environ["AWS_COGNITO_USER_POOL_CLIENT_ID"],
    "AWS_COGNITO_USER_POOL_CLIENT_SECRET":os.environ["AWS_COGNITO_USER_POOL_CLIENT_SECRET"],
    "AWS_COGNITO_REDIRECT_URL":"http://localhost:5000/redirect",
    "AWS_COGNITO_LOGOUT_URL":"http://localhost:5000/logout/redirect",
    "AWS_COGNITO_REFRESH_FLOW_ENABLED":True,
    "AWS_COGNITO_REFRESH_COOKIE_ENCRYPTED":True,
})

auth = CognitoAuth(app)

@app.route("/")
def home_page():
    return "Hello, world"

#just here temporarily to showcase need for authentication
@app.route("/protected")
@auth_required()
def get_user_details():
    return jsonify(session)

@app.route("/login")
@cognito_login
def login():
    pass

@app.route("/redirect")
@cognito_login_callback
def redirect():
    return redirect("/")

@app.route("/refresh", methods=["POST"])
@cognito_refresh_callback
def refresh():
    pass


@app.route("/logout")
@cognito_logout
def logout():
    pass

@app.route("/logout/redirect")
def logout_redirect():
    return redirect("/")