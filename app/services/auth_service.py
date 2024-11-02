import os
import boto3
from flask import current_app
import requests

from secret import TOKEN_URL
from data.models import UserAccount
from services.db_service import get_user_by_email


cognito=boto3.client('cognito-idp',os.environ["AWS_REGION"])

#lazy create: the user is added to the database the first time it is needed
def get_user(authorization_token):
    try:
        response=cognito.get_user(AccessToken=authorization_token)
        email=response["Username"]
        user=get_user_by_email(email)

        if user is None:
            name=None
            phone_number=None
            for attr in response["UserAttributes"]:
                if attr["Name"]=="name":
                    name=attr["Value"]
                elif attr["Name"]=="phone_number":
                    phone_number=attr["Value"]

            user=UserAccount(full_name=name,email=email,phone=phone_number,password_hash="something")  

        return user
    except cognito.exceptions.ResourceNotFoundException:
        return None

def exchange_token(authorization_code):
    token_endpoint = TOKEN_URL
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    body = {
        'grant_type': 'authorization_code',
        'client_id': os.environ["AWS_COGNITO_USER_POOL_CLIENT_ID"],
        'code': authorization_code,
        'redirect_uri': TO
    }
