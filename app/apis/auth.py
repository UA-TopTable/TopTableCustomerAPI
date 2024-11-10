import boto3
from flask import redirect, request
from flask_restx import Namespace,Resource,fields
from services.auth_service import exchange_token, get_user
from secret import API_URL, AWS_COGNITO_USER_POOL_CLIENT_ID, AWS_REGION, COGNITO_DOMAIN

api=Namespace("auth",path="/auth",description="Authentication operations")

cognito=boto3.client('cognito-idp',AWS_REGION)

@api.route("/login")
class Login(Resource):
    @api.doc('login via hosted ui')
    def get(self):
        return redirect(f"https://{COGNITO_DOMAIN}/login?&client_id={AWS_COGNITO_USER_POOL_CLIENT_ID}&redirect_uri={API_URL}/auth/callback&response_type=code")
        
@api.route("/sign_out")
class SignOut(Resource):
    @api.doc("sign out")
    @api.response(301,"redirecting to home page")
    def post(self):
        resp=redirect("/") #TODO: change to restaurant home page (when we have one)
        resp.delete_cookie("access_token")
        return resp
        
@api.route("/callback")
class Redirect(Resource):
    @api.expect({
        "code":fields.String(required=True)
    })
    @api.response(400,"code not returned")
    @api.response(500,"error exchanging token")
    @api.response(301,"redirect to home page")
    def get(self):
        if "code" in request.args:
            print('code',request.args.get("code") )
            token=exchange_token(request.args.get("code"))
            resp=redirect("/") #TODO: change it later
            resp.set_cookie("access_token",token)
            return resp
        else:
            return "code not returned",400
        
@api.route("/get_current_user") #this route can be used for testing
class GetCurrentUser(Resource):
    def get(self):
        if "access_token" not in request.cookies:
            return redirect("/auth/login")
        else:
            access_token=request.cookies.get("access_token")
            if(access_token is None):
                return "no access token",400
            return get_user(access_token)