import os
import boto3
from moto import mock_aws
import pytest

#Note: as I need to use a real instance, I won't auto-test registration success and email verification, but have confirmed it manually

def test_login_and_sign_out_success(client):
    
    response=client.post("/api/v1/auth/log_in",json={
        "email":"johndoe@gmail.com",
        "password":"Password!123"
    })

    assert response.status_code==200

    access_token=response.json[0]["AccessToken"]

    #will have to log_out in the same test because I need the accessToken

    response=client.post("/api/v1/auth/sign_out",json={
        "access_token":access_token
    })

    assert response.status_code==200

def test_login_wrong_credentials(client):
    response=client.post("/api/v1/auth/log_in",json={
        "email":"johndoe@gmail.com",
        "password":"WrongPassword!123"
    })

    assert response.status_code==401

def test_register_taken(client):
    response=client.post("/api/v1/auth/sign_up",json={
        "email":"johndoe@gmail.com",
        "password":"RandomPassword!123",
        "name":"John Doe",
        "phone_number":"+351123456789"
    })

    assert response.status_code==409