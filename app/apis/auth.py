import os
import boto3
from flask import current_app, jsonify, redirect, request, url_for
from flask_restx import Namespace,Resource,fields
from services.auth_service import get_user
from secret import AWS_COGNITO_HOSTED_URL,API_URL

api=Namespace("auth",path="/api/v1/auth",description="Authentication operations")

cognito=boto3.client('cognito-idp',os.environ["AWS_REGION"])

@api.route("/login")
class Login(Resource):
    @api.doc('login via hosted ui')
    def get(self):
        return redirect(f"{AWS_COGNITO_HOSTED_URL}&redirect_uri={API_URL}/api/v1/auth/redirect")
        
@api.route("/sign_out")
class SignOut(Resource):
    @api.doc("sign out")
    @api.response(301,"redirecting to home page")
    def post(self):
        resp=redirect("/") #TODO: change to restaurant home page (when we have one)
        resp.delete_cookie("access_token")
        return resp
        
@api.route("/redirect")
class Redirect(Resource):
    @api.expect({
        "code":fields.String(required=True)
    })
    @api.response(400,"code not returned")
    @api.response(301,"redirect to home page")
    def get(self):
        if "code" in request.args:
            resp=redirect("/") #TODO: change to restaurant home page (when we have one)
            resp.set_cookie("access_token",request.args.get("code"),httponly=True,secure=True)
            return resp
        else:
            return "code not returned",400
        
@api.route("/get_current_user") #this route can be used for testing
class GetCurrentUser(Resource):
    def get(self):
        if "access_token" not in request.cookies:
            return redirect("/api/v1/auth/login")
        else:
            access_token=request.cookies.get("access_token")
            return get_user(access_token)