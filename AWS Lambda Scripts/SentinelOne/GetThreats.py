import os
import urllib3
import json
from dotenv import load_dotenv

load_dotenv()

def getThreats():
    """
    Polls the S1 API to fetch all unresolved alerts 
    """
    #Get the .env info
    S1_API_KEY = f"{os.getenv('API_KEY')}"
    BASE_URL = f"{os.getenv('BASE_URL')}"
    #Add the API endpoint to the URL
    THREATS_URL = BASE_URL + "/web/api/v2.1/threats"
    #Create Authentication Headers
    headers = {
        'Authorization': f'ApiToken {S1_API_KEY}',
    }

    query_params= {}
    #query_params["resolved"]= False

    #Create pool manager
    http = urllib3.PoolManager()
    #Send the request to the API
    response = http.request(
        'GET',
        THREATS_URL,
        headers=headers,
        retries=False,
        timeout=urllib3.Timeout(connect=5.0, read=10.0),
        redirect=False,
        fields=query_params
    )
    #decode the bytes response to utf and then into python from json
    response_json = json.loads(response.data.decode('utf-8'))
    return response_json
  

def getPayload(threat):
    """
    Received a list of threats and extracts the information for the ticket message 
    """ 
    company_name = threat.get('agentRealtimeInfo').get('siteName') or "Unavailable"
    match company_name:
        case "something":
            company_name = "something"
     

    if threat['threatInfo']['confidenceLevel'] == "malicious":
        priority_label = "P1 - Critical"
    elif threat['threatInfo']['confidenceLevel'] == "suspicious":
        priority_label = "P2 - High"
    else:
        priority_label = "P3 - Normal"


    payload = {
    'company_name' : company_name,
    'user_name' : threat.get('agentDetectionInfo').get('agentLastLoggedInUserName') or "Unavailable",
    'Device_ID': threat.get('agentRealtimeInfo').get('agentComputerName') or "Unavailable",
    'group_name' : threat.get('agentRealtimeInfo').get('groupName') or "Unavailable",
    'classification': threat.get('threatInfo').get('classification') or "Unavailable",
    'Certificate_ID': threat.get('threatInfo').get('certificateId') or "Unavailable",
    'Device_IPs': str(threat.get('agentRealtimeInfo').get('networkInterfaces')[0]['inet']) or "Unavailable",
    'priority_label': priority_label,
    'file_hash': threat.get('threatInfo').get('sha1') or "Unavailable",
    }
    return json.dumps(payload)




if __name__ == "__main__":
    Threats = getThreats()
    WEBHOOK_URL = f"{os.getenv('WEBHOOK_URL')}"
    for threat in Threats['data']:
        payload = getPayload(threat)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        http = urllib3.PoolManager(headers=headers)
        response = http.request(
            'POST', 
            WEBHOOK_URL, 
            body=payload
            )
        if response.status == 202:
            print("Alarm processed successfully")
        else:
            print(f'Error sending payload to Cisco SecureX Workflow. Status code: {response.status}')
            print(response.data)