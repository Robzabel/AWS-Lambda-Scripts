import os
import urllib3
import json
from dotenv import load_dotenv

load_dotenv()

#Get the .env info
S1_API_KEY = f"{os.getenv('API_KEY')}"
BASE_URL = f"{os.getenv('BASE_URL')}"
#Add the API endpoint to the URL
USERS_URL = BASE_URL + "/web/api/v2.1/cloud-detection/alerts"
#Create Authentication Headers
headers = {
    'Authorization': f'ApiToken {S1_API_KEY}',
}

query_params= {}
query_params["limit"]= 20
#query_params["resolved"]= False

#Create pool manager
http = urllib3.PoolManager()
#Send the request to the API
response = http.request(
    'GET',
    USERS_URL,
    headers=headers,
    retries=False,
    timeout=urllib3.Timeout(connect=5.0, read=10.0),
    redirect=False,
    fields=query_params
)
#decode the bytes response to utf
#response_json = json.loads(response.data.decode('utf-8'))

print(response.data.decode('utf-8'))