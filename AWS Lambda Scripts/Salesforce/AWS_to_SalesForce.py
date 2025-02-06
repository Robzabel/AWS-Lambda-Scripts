import json
import urllib3
from dotenv import load_dotenv
import os
import requests

def auth_token():
    params = {
    "grant_type": "password",
    "client_id": os.getenv('SF_CLIENT_ID'), # Consumer Key
    "client_secret": os.getenv('SF_CLIENT_SECRET'), # Consumer Secret
    "username": os.getenv('SF_USERNAME'), # The email you use to login
    "password": os.getenv('SF_PASSWORD') # Concat your password and your security token
    }
    r = requests.post(os.getenv('SF_AUTH_API'))
    access_token = r.json().get("access_token")
    instance_url = r.json().get("instance_url")
    print(access_token)




def lambda_handler(event, context):
    
    
    
    load_dotenv()
    
    
    
    
    # Define Salesforce API endpoint and access token
    url = os.getenv('SF_CASE_ENDPOINT')
    access_token = "YOUR_ACCESS_TOKEN"

    # Define the case details to be created
    case_data = {
        "Subject": "New Case",
        "Description": "This is a new case created via API.",
        "Status": "New"
        # Add any other required fields or custom fields
    }

    # Convert case data to JSON
    case_json = json.dumps(case_data)

    # Set headers for the request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Create a connection pool
    http = urllib3.PoolManager()

    # Send the POST request to create a new case
    response = http.request(
        method="POST",
        url=url,
        headers=headers,
        body=case_json.encode("utf-8")
    )

    if response.status == 201:
        return {
            "statusCode": response.status,
            "body": "New case created successfully."
        }
    else:
        return {
            "statusCode": response.status,
            "body": "Failed to create a new case."
        }

