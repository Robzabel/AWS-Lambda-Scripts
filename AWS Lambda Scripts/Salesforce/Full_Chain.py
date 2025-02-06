import urllib3
import json
from dotenv import load_dotenv
import os

""" 
To Do:
 - Change the create ticket function to use Urllib3 instead of requests
 - convert the try catch block from the webhook function into the create ticket function
 - test from VSC
 - Convert the code to run from AWS Lambda 
"""


event = ""#replace with SNS JSON

load_dotenv()
def Oauth_Get_Token():
    """
    This function uses the API user credentials to generate and access token
    """
    # OAuth2 endpoints
    auth_url = os.getenv('SF_AUTH_API')
    
    # Create a connection pool
    http = urllib3.PoolManager()

    # Construct the payload for the OAuth2 request
    payload = {
        "grant_type": "password",
        "client_id": os.getenv('SF_CLIENT_ID'), # Consumer Key
        "client_secret": os.getenv('SF_CLIENT_SECRET'), # Consumer Secret
        "username": os.getenv('SF_USERNAME'), # The email you use to login
        "password": os.getenv('SF_PASSWORD') # Concat your password and your security token
    }

    # Send the OAuth2 request
    response = http.request('POST', auth_url, fields=payload)

    # Read the response and extract the access token
    auth_data = json.loads(response.data.decode('utf-8'))
    access_token = auth_data['access_token']

    #return access_token
    return access_token


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


def get_customer_id(account_dict, customer):
    """
    This function uses the account ID/Name dictionary to find the customer ID 
    """
    for key, values in account_dict.items():#Iterates through customer ID/Name mappings to find the ID for the customer name provided
        if customer in values:  
            return key
        

def get_customer_name(event):
    """
    This function parses the Alien Vault Alert and grabs the customer name
    """
    # Extract the SNS message from the Lambda event and turn it to a python Dictionary
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    
    #Switch case statement to match the subdomain to the salesforce account name
    match sns_message['x_att_tenant_subdomain']:
        case "something":
            company_name = "something"
        

def get_alert_priority(event):
    """
    This function parses the Alien Vault Alert to extract the details
    """
    # Extract the SNS message from the Lambda event and turn it to a python Dictionary
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    
    #Convert the Priority so SalesForce can understand 
    if sns_message['priority_label'] == "high":
        priority_label = "P1 - Critical"
    elif sns_message['priority_label'] == "medium":
        priority_label = "P2 - High"
    else:
        priority_label = "P3 - Normal"
    return priority_label

    
def get_alert_payload(event):
    """
    This function parses the Alien Vault Alert to extract the details
    """
    # Extract the SNS message from the Lambda event and turn it to a python Dictionary
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])

    """#Replace any backslashes otherwise SecureX cannot parse the JSON
    try:
        user_name = sns_message['events'][0]['message']['source_username']
        if "\\" in user_name:
            user_name = user_name.replace("\\","-")
    except Exception as e:
        print("There is no username")
        user_name = "Unavailable"""

    #Get the rest of the values you want to use in the ticket
    rule_method = sns_message.get('rule_method') if sns_message.get('rule_method') else "Unavailable"
    rule_strategy = sns_message.get('rule_strategy') if  sns_message.get('rule_strategy') else "Unavailable"
    rule_attack_technique =  sns_message.get('rule_attack_technique') if sns_message.get('rule_attack_technique') else "Unavailable"
    rule_intent = sns_message.get('rule_intent') if sns_message.get('rule_intent') else "Unavailable"
    user_name = sns_message.get('source_username') if sns_message.get('source_username') else "Unavailable"
    
    #Create the payload of of the values and their key mappings
    payload = {
        'rule_strategy': rule_strategy,
        'rule_method': rule_method,
        'rule_attack_technique': rule_attack_technique,
        'rule_intent': rule_intent,
        'user_name': user_name,
    }
    return payload


def create_ticket(account_id, access_token, priority, payload):
    """
    Use the API to create a Salesforce Ticket
    """
    data = {
        "AccountId": f"{account_id}",
        "Status": "SOC",
        "Origin": "API",
        "Ticket_Category__c": "AlienVault",
        "Subject": f"{payload['rule_strategy']}",
        "Priority": f"{priority}",
        "OwnerId": f"{os.getenv('OWNER_ID')}",
        "Description": payload,
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



#def lambda_handler(event, context):
if __name__ == "__main__":
    #Get the Bearer token
    auth_token = Oauth_Get_Token()
    
    #Get the account ID and name mappings in list format
    accounts = sf_api_call(auth_token)

    #rearrange the list to make a dictionary
    salesforce_account_id = []
    salesforce_account_name = []

    #Populate the lists with the Account names and IDs
    for value in accounts['records']:
        salesforce_account_id .append(value['Id'])
        salesforce_account_name.append(value['Name'])
    
    #Create a new dictonary from the two account name and ID lists
    account_dict = dict(zip(salesforce_account_id,salesforce_account_name))

    #Grab customer name from the event
    customer = get_customer_name(event)

    #Pass customer name to function to search and return the account ID
    account_id = get_customer_id(account_dict, customer )

    #Get the priority of the alert
    priority = get_alert_priority(event)

    #Parse alarm to create ticket description
    description = get_alert_payload(event)

    #create the Ticket
    create_ticket(account_id, auth_token, priority, description)



def webhook(payload):
    """
    This Function Sends the message to Secure X and checks for errors
    """
    #URL of the webhook with API key
    webhook_url = os.environ.get('SECUREX_URL')
    
    #Set up the headers for the API endpoint
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }
    #Create the Pool manager and pass the headers variable
    http = urllib3.PoolManager(headers=headers)
    #Send the request and handle any errors
    try:
        response = http.request(
            'POST', 
            webhook_url, 
            body=payload
            )
        if response.status == 202:
            print("Alarm processed successfully")
        else:
            print(f'Error sending payload to Cisco SecureX Workflow. Status code: {response.status}')
            print(response.data)
            
            payload = {
                'response_status': response.status,
                'error_reason': response.data
            }
            
            ERROR_URL = os.environ.get('ERROR_URL')
            error_response = http.request(
                'POST', 
                url=ERROR_URL, 
                body=json.dumps(payload)
            )
            print(f"Error message sent to SecureX with response code: {error_response.status}")
    except urllib3.exceptions.RequestException as e:
        print(f'Error sending payload to Cisco SecureX Workflow: {str(e)}')     


def lambda_handler(event, context):
    #Extract ticket information
    payload = get_alert_details(event)
    #Send the info to webex
    webhook(payload)
    print(payload)
    print(event)
  

