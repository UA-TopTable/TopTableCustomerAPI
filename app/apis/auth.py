import os
import boto3
from flask import current_app, jsonify, request
from flask_restx import Namespace,Resource,fields

api=Namespace("auth",path="/api/v1/auth", description="Authentication operations")

cognito=boto3.client('cognito-idp',os.environ["AWS_REGION"])

new_request_metadata_model=api.model("new_request_metadata",{
    "DeviceKey":fields.String,
    "DeviceGroupKey":fields.String
})

login_response_model=api.model("login_response",{
    "AccessToken":fields.String(),
    "ExpiresIn":fields.Integer(),
    "TokenType":fields.String(),
    "RefreshToken":fields.String(),
    "IdToken":fields.String(),
    "NewDeviceMetadata":fields.Nested(new_request_metadata_model)
})

@api.route("/log_in")
class Login(Resource):
    @api.doc('login')
    @api.expect(api.model('Login', {
        "email": fields.String(required=True),
        "password": fields.String(required=True)
    }), validate=True)
    @api.response(200,description="success",model=login_response_model)
    @api.response(400,"wrong response body")
    @api.response(401,"wrong email/password")
    def post(self):
        try:
            data=request.json
            email=data.get("email")
            password=data.get("password")
            print(email,password)
            response=cognito.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME":email,
                    "PASSWORD":password
                },
                ClientId=current_app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"]
            )
            return jsonify(response.get("AuthenticationResult"),200)
        except KeyError:
            print(response)
            return "Incorrect input",401
        except cognito.exceptions.NotAuthorizedException:
            return "Wrong username/password",401
        
@api.route("/sign_up")
class SignUp(Resource):
    @api.doc("sign up")
    @api.expect({
        "email":fields.String(required=True),
        "password":fields.String(required=True),
        "name":fields.String(required=True),
        "phone_number":fields.String(required=True)
    },validate=True)
    @api.response(201,"user created")
    @api.response(400,"wrong body")
    @api.response(409,"username already exists")
    def post(self):
        try:
            data=request.json
            email=data.get("email")
            password=data.get("password")
            name=data.get("name")
            phone_number=data.get("phone_number")

            cognito.sign_up(
                ClientId=current_app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"],
                Username=email,
                Password=password,
                UserAttributes=[
                    {
                        "Name": "name",
                        "Value":name
                    },
                    {
                        "Name": "phone_number",
                        "Value":phone_number
                    }
                ]
            )
            return "User created. Confirm registration via email"
        except KeyError:
            return "Wrong Body",400
        except cognito.exceptions.UsernameExistsException:
            return "Username already exists",409
        
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
            cognito.confirm_sign_up(
                ClientId=current_app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"],
                Username=email,
                ConfirmationCode=confirmation_code
            )
            return "user confirmed",200
        except KeyError:
            return "Wrong body",400
        except cognito.exceptions.CodeMismatchException:
            return "Wrong confirmation code",400
        except cognito.exceptions.ExpiredCodeException:
            return "Confirmation code expired",410
        
@api.route("/sign_out")
class SignOut(Resource):
    @api.doc("sign out")
    @api.expect({
        "access_token":fields.String(required=True)
    },validate=True)
    @api.response(200,"sign out successful")
    @api.response(400,"Wrong body")
    @api.response(401,"invalid access token")
    def post(self):
        try:
            data=request.json
            access_token=data.get("access_token")
            cognito.global_sign_out(AccessToken=access_token)
            return "signed out successful",200
        except KeyError:
            return "Wrong body",400
        except cognito.exceptions.NotAuthorizedException:
            return "Invalid access token",401