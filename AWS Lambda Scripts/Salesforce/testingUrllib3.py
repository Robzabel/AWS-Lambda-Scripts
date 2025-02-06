import urllib3
import json
from dotenv import load_dotenv
import os

load_dotenv() 

def sf_api_call(bearerToken):
    
    """
    This Function takes the bearer token then polls the Salesforce Account endpoint to retrieve a dictionary of all accounts and account IDs
    """
    #Salesforce Endpoint 
    instance_url = os.getenv('INSTANCE_URL') + "/services/data/v39.0/query/"
    
    #Pass the bearer token to the headers
    headers = {
        'Content-type': 'application/json',
        'Accept-Encoding': 'gzip',
        'Authorization': f'Bearer {bearerToken}'
    }

    #Use the paramaters to execute and SQL query on the salesforce DB
    paramaters = {'q': 'SELECT Id, Name FROM Account'}

    #Create the pool manager and try to send the request
    http = urllib3.PoolManager()
    try:
       
        response = http.request(
            method="GET", 
            url=instance_url, 
            headers=headers, 
            fields=paramaters
            )
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    #return a python dict of all account ID and Names
    return json.loads(response.data.decode("utf-8"))
    
   


print(sf_api_call("bearer token here "))