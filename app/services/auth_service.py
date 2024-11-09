import base64
import requests

from secret import API_URL, AWS_COGNITO_USER_POOL_CLIENT_ID, AWS_COGNITO_USER_POOL_CLIENT_SECRET, AWS_REGION, COGNITO_DOMAIN
from data.models.UserAccount import UserAccount
from services.db_service import save_user_account, get_user_by_email

#lazy create: the user is added to the database the first time it is needed
def get_user(access_token):
    name=None
    phone_number=None
    email=None
    
    try:
        response = get_user_details_from_cognito(access_token)
        print('response getuser from cognito oauth2/userInfo', response)
        name = response.get('name')
        email = response.get('email')
        uid  = response.get('sub')
        phone_number = response.get('phone_number')
        user=get_user_by_email(email)
        user={"full_name":name,"email":email,"phone":phone_number,"password_hash":"something"}
        return save_user_account(user), 200
    except Exception as e:
        print("Error getting user",e)
        return None, 400


def get_user_details_from_cognito(access_token):
    url = f"https://{COGNITO_DOMAIN}/oauth2/userInfo"
    headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "Authorization": f"Bearer {access_token}",
        "Accept": "*/*",
        "Host": COGNITO_DOMAIN,
        "Accept-Encoding": "gzip, deflate, br",
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print('User Info:', user_info)
        return user_info
    else:
        print('Error fetching user info:', response.text)
        return None
    
def exchange_token(authorization_code):
    message = bytes(f"{AWS_COGNITO_USER_POOL_CLIENT_ID}:{AWS_COGNITO_USER_POOL_CLIENT_SECRET}",'utf-8')
    secret_hash = base64.b64encode(message).decode()
    payload = {
        "grant_type": 'authorization_code',
        "client_id": AWS_COGNITO_USER_POOL_CLIENT_ID,
        "code": authorization_code,
        "redirect_uri": f"{API_URL}/auth/callback"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {secret_hash}"}
           
    response = requests.post(f'https://{COGNITO_DOMAIN}/oauth2/token', params=payload, headers=headers)
    print(response.json())
    if response.status_code==200:
        tokens = response.json()
        return tokens.get("access_token")
    else:
        return None
