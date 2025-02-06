

import urllib3
import json
from dotenv import load_dotenv
import os


def sf_api_call(bearerToken):
    load_dotenv()
    """
    This Function takes the bearer token then polls the Salesforce Account endpoint to retrieve a dictionary of all accounts and account IDs
    """
    instance_url = os.getenv('ACCOUNT_API')
    
    headers = {
        'Content-type': 'application/json',
        'Accept-Encoding': 'gzip',
        'Authorization': f'Bearer {bearerToken}'
    }

    paramaters = {'q': 'SELECT Id, Name FROM Account'}

    http = urllib3.PoolManager()
    try:
       
        response = http.request(
            method="GET", 
            url=instance_url, 
            headers=headers, 
            params=paramaters
            )
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    return json.loads(response.data.decode("utf-8"))





salesforce_account_id = []
salesforce_account_name = []
accounts = sf_api_call(bearerToken)
for value in accounts['records']:
    sf_account_id.append(value['Id'])
    sf_account_name.append(value['Name'])
object_id_match = dict(zip(sf_account_id,sf_account_name))
print(object_id_match)