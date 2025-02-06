import urllib3
from dotenv import load_dotenv
import os
import json

load_dotenv()

def Oauth_Get_Token():
    """
    This function uses the API user credentials to generate and access token through 0auth2
    """
    # OAuth2 endpoints
    auth_url = os.getenv('endpoint')
    
    # Create a connection pool
    http = urllib3.PoolManager()

    # Construct the payload for the OAuth2 request
    payload = {
        "grant_type": "password",
        "client_id": os.getenv('CLIENT_ID'), # Consumer Key
        "client_secret": os.getenv('CLIENT_SECRET'), # Consumer Secret
        "username": os.getenv('USERNAME'), # The email you use to login
        "password": os.getenv('PASSWORD') # Concat your password and your security token
    }

    # Send the OAuth2 request
    response = http.request('POST', auth_url, fields=payload)

    # Read the response and extract the access token
    auth_data = json.loads(response.data.decode('utf-8'))
    access_token = auth_data['access_token']

    #return access_token
    return access_token