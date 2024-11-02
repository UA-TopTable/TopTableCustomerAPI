import os
import boto3
from flask import current_app, jsonify, redirect, request, url_for
from flask_restx import Namespace,Resource,fields
from .ui import ConfirmRegistration
from services.auth_service import confirm_sign_up
from secret import AWS_COGNITO_HOSTED_URL,API_URL

api=Namespace("auth",description="Authentication operations")

cognito=boto3.client('cognito-idp',os.environ["AWS_REGION"])

@api.route("/log_in")
class Login(Resource):
    @api.doc('login via hosted ui')
    def get(self):
        return redirect(f"{AWS_COGNITO_HOSTED_URL}&redirect_uri={API_URL}/api/v1/redirect")
        
@api.route("/sign_out")
class SignOut(Resource):
    @api.doc("sign out")
    @api.response(301,"redirecting to home page")
    def post(self):
        resp=redirect("/")
        resp.delete_cookie("access_token")
        return resp


@api.route("/sign_up/confirm")
class ConfirmSignUp(Resource):
    @api.doc("confirm sign up")
    @api.expect({
        "email":fields.String(required=True),
        "confirmation_code":fields.String(required=True)
    },validate=True)
    @api.response(200,"user confirmed")
    @api.response(400,"wrong body")
    @api.response(400,"wrong confirmation code")
    @api.response(410,"confirmation code expired")
    def post(self):
        try:
            data=request.json
            email=data.get("email")
            confirmation_code=data.get("confirmation_code")
            confirm_sign_up(email,confirmation_code)
            return "user confirmed",200
        except KeyError:
            return "Wrong body",400
        except cognito.exceptions.CodeMismatchException:
            return "Wrong confirmation code",400
        except cognito.exceptions.ExpiredCodeException:
            return "Confirmation code expired",410
        
@api.route("/redirect")
class Redirect(Resource):
    @api.expect({
        "code":fields.String(required=True)
    })
    @api.response(400,"code not returned")
    @api.response(301,"redirect to home page")
    def get(self):
        if "code" in request.args:
            resp=redirect(url_for(ConfirmRegistration))
            resp.set_cookie("access_token",request.args.get("code"),httponly=True,secure=True)
            return resp
        else:
            return "code not returned",400