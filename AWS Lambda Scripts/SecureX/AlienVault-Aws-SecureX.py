import os
import json 
import urllib3
from dotenv import load_dotenv
import os

load_dotenv()

def get_alert_details(event):
    """
    This function parses the Alien Vault Alert and creates the message to be sent to Secure X
    """
    # Extract the SNS message from the Lambda event and turn it to a python Dictionary
    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    
    #Switch case statement to match the subdomain to the salesforce account name
    match sns_message['x_att_tenant_subdomain']:
        case "something":
            company_name = "something"
       
    
    #Convert the Priority so SalesForce can understand 
    if sns_message['priority_label'] == "high":
        priority_label = "P1 - Critical"
    elif sns_message['priority_label'] == "medium":
        priority_label = "P2 - High"
    else:
        priority_label = "P3 - Normal"

    #Replace any backslashes otherwise SecureX cannot parse the JSON
    try:
        user_name = sns_message['events'][0]['message']['source_username']
        if "\\" in user_name:
            user_name = user_name.replace("\\","-")
    except Exception as e:
        print("There is no username")
        user_name = "Unavailable"
    
    """if sns_message['events'][0]['message']['source_username']:
        user_name = sns_message['events'][0]['message']['source_username']
        if "\\" in user_name:
            user_name = user_name.replace("\\","-")
    else:
        user_name = "Unavailable"""

    #Get the rest of the values you want to use in the ticket
    rule_method = sns_message.get('rule_method') if sns_message.get('rule_method') else "Unavailable"
    rule_strategy = sns_message.get('rule_strategy') if  sns_message.get('rule_strategy') else "Unavailable"
    rule_attack_technique =  sns_message.get('rule_attack_technique') if sns_message.get('rule_attack_technique') else "Unavailable"
    rule_intent = sns_message.get('rule_intent') if sns_message.get('rule_intent') else "Unavailable"
   

    #Create the payload of of the values and their key mappings
    payload = {
        'company_name' : company_name,
        'rule_strategy': rule_strategy,
        'rule_method': rule_method,
        'priority_label': priority_label,
        'rule_attack_technique': rule_attack_technique,
        'rule_intent': rule_intent,
        'user_name': user_name,
    }
    return json.dumps(payload)



def webhook(payload):
    """
    This Function Sends the message to Secure X and checks for errors
    """
    #URL of the webhook with API key
    webhook_url = os.getenv('SECUREX_WEBHOOK_URL')
    
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
    #need to add code to send a message into salesforce or webex if the request fails


