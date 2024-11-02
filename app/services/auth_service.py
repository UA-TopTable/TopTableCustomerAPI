import os
import boto3
from flask import current_app


cognito=boto3.client('cognito-idp',os.environ["AWS_REGION"])

def confirm_sign_up(email,confirmation_code):
    return cognito.confirm_sign_up(
        ClientId=current_app.config["AWS_COGNITO_USER_POOL_CLIENT_ID"],
        Username=email,
        ConfirmationCode=confirmation_code
    )