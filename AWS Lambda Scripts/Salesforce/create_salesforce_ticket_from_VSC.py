import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()


def Oauth_token():
    """
    Create Access token through Oauth2 protocol
    """
    params = {
        "grant_type": "password",
        "client_id": os.getenv('SF_CLIENT_ID'), # Consumer Key
        "client_secret": os.getenv('SF_CLIENT_SECRET'), # Consumer Secret
        "username": os.getenv('SF_USERNAME'), # The email you use to login
        "password": os.getenv('SF_PASSWORD') # Password for salesforce account
    }
    r = requests.post(os.getenv('SF_AUTH_API'), params=params)
    return r.json().get("access_token")


def sf_api_call(action, parameters, instance_url, access_token):
    """"
    Make a request to get all Accounts and Account IDs
    """
    headers = {
        'Content-type': 'application/json',
        'Accept-Encoding': 'gzip',
        'Authorization': f'Bearer {access_token}'
    }
    
    r = requests.get(instance_url+action, headers=headers, params=parameters, timeout=30)
    return r.json()
   
def account_id(account_name, account_id_list):
    """
    Return the ID of the Supplied Account
    """
    for key, values in account_id_list.items():
        if account_name in values:
            return key

def create_ticket(account_id, access_token):
    """
    Use the API to create a Salesforce Ticket
    """
    data = {
        "AccountId": f"{account_id}",
        "Status": "SOC",
        "Origin": "API",
        "Ticket_Category__c": "AlienVault",
        "Subject": "Testing From Rob's VSC",
        "Priority": "P1-high",
        "OwnerId": f"{os.getenv('OWNER_ID')}",
        "Description": "Testing Ticket",
        "RecordTypeId": f"{os.getenv('RECORD_TYPE_ID')}"
        }
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    url = os.getenv('INSTANCE_URL') + "/services/data/v38.0/sobjects/Case/"
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.status_code)
    print(r.reason)
    print(r.text)

if __name__ == '__main__':

    access_token = Oauth_token()
    instance_url = os.getenv("INSTANCE_URL")

    data = (json.dumps(sf_api_call('/services/data/v39.0/query/', {'q': 'SELECT Id, Name FROM Account'}, instance_url, access_token), indent=2))

    sf_account_id = []
    sf_account_name = []

    account_id_list = json.loads(data)

    for value in account_id_list['records']:
        sf_account_id.append(value['Id'])
        sf_account_name.append(value['Name'])
    
    account_id_list = dict(zip(sf_account_id,sf_account_name))
    account_name = os.getenv('ACCOUNT_NAME')
    account_id = account_id(account_name, account_id_list)

    create_ticket(account_id, access_token)

