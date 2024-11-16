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
        return save_user_account(user)
    except Exception as e:
        print("Error getting user",e)
        return "aaa"


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
    try:
        auth_string = f"{AWS_COGNITO_USER_POOL_CLIENT_ID}:{AWS_COGNITO_USER_POOL_CLIENT_SECRET}"
        secret_base = base64.b64encode(auth_string.encode('utf-8')).decode()
        
        payload = {
            "grant_type": 'authorization_code',
            "client_id": AWS_COGNITO_USER_POOL_CLIENT_ID,
            "code": authorization_code,
            "redirect_uri": f"{API_URL}/customer/auth/callback"
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {secret_base}"
        }
        
        response = requests.post(
            f'https://{COGNITO_DOMAIN}/oauth2/token',
            data=payload,
            headers=headers
        )

        if response.status_code != 200:
            print(f"Error exchanging token: {response.text}")
            return None
            
        tokens = response.json()
        access_token = tokens.get("access_token")
        
        if not access_token:
            print("No access token in response")
            return None
            
        return access_token
        
    except Exception as e:
        print(f"Exception during token exchange: {str(e)}")
        return None
