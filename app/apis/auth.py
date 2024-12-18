import boto3
from flask import redirect, request
from flask_restx import Namespace,Resource,fields
from services.auth_service import exchange_token, get_user
from secret import API_URL, APP_PORT, AWS_COGNITO_USER_POOL_CLIENT_ID, AWS_REGION, COGNITO_DOMAIN
SESSION_COOKIE_NAME_0 = "AWSELBAuthSessionCookie-0"
SESSION_COOKIE_NAME_1 = "AWSELBAuthSessionCookie-1"
api=Namespace("auth",path="/auth",description="Authentication operations")

cognito=boto3.client('cognito-idp',AWS_REGION)


@api.route("/login")
class Login(Resource):
    @api.doc('login via hosted ui')
    def get(self):
        return redirect(f"https://{COGNITO_DOMAIN}/login?&client_id={AWS_COGNITO_USER_POOL_CLIENT_ID}&redirect_uri={API_URL}/customer/auth/callback&response_type=code")
        
@api.route("/logout")
class SignOut(Resource):
    @api.doc("sign out")
    @api.response(301,"redirecting to cognito logout")
    def get(self):
        print("logging out")
        resp=redirect(f"https://{COGNITO_DOMAIN}/logout?&client_id={AWS_COGNITO_USER_POOL_CLIENT_ID}&redirect_uri={API_URL}/customer/auth/callback&response_type=code")
        resp.delete_cookie("access_token")
        resp.set_cookie(SESSION_COOKIE_NAME_0, "empty", max_age=-3600)
        resp.set_cookie(SESSION_COOKIE_NAME_1, "empty", max_age=-3600)
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
            token=exchange_token(request.args.get("code"))
            resp=redirect("/customer/ui/home") #TODO: change it later
            resp.set_cookie("access_token",token, secure=True, httponly=True)
            return resp
        else:
            return "code not returned",400
        
@api.route("/get_current_user") #this route can be used for testing
class GetCurrentUser(Resource):
    def get(self):
        if 'x-amzn-oidc-accesstoken' in request.headers:
            access_token = request.headers.get('x-amzn-oidc-accesstoken')
        elif "access_token" in request.cookies:
            access_token=request.cookies.get("access_token")
        else:
            return redirect("/auth/login")
        user=get_user(access_token)
        if user is None:
            return "invalid user",400
        else:
            return user,200