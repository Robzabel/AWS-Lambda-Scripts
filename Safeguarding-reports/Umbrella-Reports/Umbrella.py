import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()


def poll_umbrella():
    """
    Poll the Umbrella Reporting API to ger blocked activty
    """
    # OAuth2 endpoint and Credentials
    auth_url = os.getenv('UMBRELLA_AUTH_URL')
    client_id = os.getenv('UMBRELLA_CLIENT_ID')
    client_secret = os.getenv('UMBRELLA_CLIENT_SECRET')

    #Send basic auth request to get bearer token
    r = requests.get(auth_url, auth=(client_id, client_secret))

    #Extract access token from the response
    access_token = r.json()['access_token']
    
    #set the headers with the bearer token
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    #Provide paramaters for the report search
    params = { 
        'from': '-1hours',
        'to': 'now',
        'limit': 100,
        'verdict': 'blocked'
    }
    #send a request to get activity
    r = requests.get(os.environ.get('REPORTING_URL'), params=params, headers=headers)

    
    with open(f"./reports/umbrella_json.json", mode='w') as f:
        f.write(r.text)
    
    #Return a JSON object of the Umbrella report data
    return json.loads(r.text)


if __name__ == '__main__':
    print(json.dumps(poll_umbrella()))