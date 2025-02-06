"""
Author - Rob Zabel
Uses AWS Lambda to Poll the Cisco AMP API for new alerts. 
To make sure only the latest alerts are collected, a timestamp is retrieved from S3 for the start point. Alerts that occur after the start point are collected,formated
then sent to a Webex chat webhook which will allert engineers.
The timestamp of the last collected alert is the written back to the S3 bucket, ready for the next poll event.
"""

import os
import urllib3
import json
import datetime
import boto3
from dotenv import load_dotenv

def load_timestamps():
    """
    Grabs the timestamps from S3
    """ 
    #Use the Boto3 client to interact with S3
    s3 = boto3.client('s3')
    bucket_name = os.getenv('S3_BUCKET')
    object_key = os.getenv('S3_BUCKET_OBJECT')

    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        variable = response['Body'].read().decode('utf-8')
    
    except s3.exceptions.NoSuchKey:
        print("No Timestamps available")
    
    timestamps = eval(variable)#Change the string to a dict
    return timestamps
 
 
def save_timestamps(timestamps):
    """
    writes the timestamps to S3
    """ 
    #Use the Boto3 client to interact with S3
    s3 = boto3.client('s3')
    bucket_name = os.getenv('S3_BUCKET')
    object_key = os.getenv('S3_BUCKET_OBJECT')

    s3.put_object(Bucket=bucket_name, Key=object_key, Body=str(timestamps).encode('utf-8')) 
 

def webex_message(alert):
    """
    Takes the alert, formats the message then sends it to webex
    """
    # The API Endpoint for webex
    api_endpoint = os.getenv('API_ENDPOINT')#create message endpoint
    access_token = os.environ.get('WebexSecureEndpointBotToken') #secure endpoint bot access token

    # Set the headers for the request and provide access token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
        }

    #Grab variables for the Webex message from the AMP alerts
            #Grab variables for message
    EVENT_TYPE = alert['event_type']
    DATE_TIME = alert.get('date') if alert.get('date') else 'Unavailable'
    SEVERITY = alert.get('severity') if alert.get('severity') else 'Unavailable'
    DETECTION = alert.get('detection') if alert.get('detection') else 'Unavailable'
    DEVICE_DETAILS = alert.get('computer') if alert.get('computer') else 'Unavailable'
    CAUSE = alert.get('file') if alert.get('file') else 'Unavailable'
    DETECTION_DATA = alert.get('bp_data') if alert.get('bp_data') else 'Unavailable'

    MESSAGE = ""
    
    #Check what type of alert it is then structure message accordingly
    if alert['event_type'] == "Threat Detection":
        
        MESSAGE = f"""Alert From Cisco Secure Endpoint\
        \n##########################\nThere has been a {str.upper(EVENT_TYPE)} at {os.environ.get('CompanyName')}.\
        \nDate & Time - {DATE_TIME[:10]} {DATE_TIME[11:19]}\
        \nAlert Severity - {SEVERITY}\
        \nThreat detected - {DETECTION}
        \n\nAffected Device Details\
        \n##################\
        \nHostname - {DEVICE_DETAILS['hostname']}\
        \nNetwork Interfaces - {DEVICE_DETAILS['network_addresses']}\
        \nExternal IP - {DEVICE_DETAILS['external_ip']}
        \n\nRoot Cause of Alarm\
        \n################\
        \nApplication that deleted regestry object  - {DETECTION_DATA['details']['matched_activity']['events'][0]['registry:delete']['app'] or 'Unavailable'}\
        \nPath to applicatiopn  - {DETECTION_DATA['details']['matched_activity']['events'][0]['registry:delete']['app_path'] or 'Unavailable'}\
        \nRegistry Object Key  - {DETECTION_DATA['details']['matched_activity']['events'][0]['registry:delete']['key'] or 'Unavailable'}\
        \nUser that performed the task  - {DETECTION_DATA['details']['matched_activity']['events'][0]['registry:delete']['user'] or 'Unavailable'}\
        \n-------------------- End of Alert --------------------"""
    
    elif alert['event_type'] == "Threat Detected":
        
        MESSAGE = f"""Alert From Cisco Secure Endpoint\
        \n##########################\nThere has been a {str.upper(EVENT_TYPE)} at {os.environ.get('CompanyName')}.\
        \nDate & Time - {DATE_TIME[:10]} {DATE_TIME[11:19]}\
        \nAlert Severity - {SEVERITY}\
        \nThreat detected - {DETECTION}
        \n\nAffected Device Details\
        \n##################\
        \nHostname - {DEVICE_DETAILS['hostname']}\
        \nUser - {DEVICE_DETAILS['user']}\
        \nNetwork Interfaces - {DEVICE_DETAILS['network_addresses']}\
        \nExternal IP - {DEVICE_DETAILS['external_ip']}
        \n\nRoot Cause of Alarm\
        \n################\
        \nfilename - {CAUSE['file_name']}\
        \nFile Path - {CAUSE['file_path']}\
        \nFile hash - {CAUSE['identity']}\
        \nParent process - {CAUSE['parent']['file_name']}\
        \n-------------------- End of Alert --------------------"""
    
    elif alert['event_type'] == "Threat Quarantined":
        
        MESSAGE = f"""Alert From Cisco Secure Endpoint\
        \n##########################\nThere has been a {str.upper(EVENT_TYPE)} at {os.environ.get('CompanyName')}.\
        \nDate & Time - {DATE_TIME[:10]} {DATE_TIME[11:19]}\
        \nAlert Severity - {SEVERITY}\
        \n\nAffected Device Details\
        \n##################\
        \nHostname - {DEVICE_DETAILS['hostname']}\
        \nNetwork Interfaces - {DEVICE_DETAILS['network_addresses']}\
        \nExternal IP - {DEVICE_DETAILS['external_ip']}
        \n\nRoot Cause of Alarm\
        \n################\
        \nfile disposition - {CAUSE['disposition']}\
        \nFile hash - {CAUSE['identity']}\
        \n-------------------- End of Alert --------------------"""

    else:

        MESSAGE = f"""Alert From Cisco Secure Endpoint\
        \n##########################\nThere has been a {str.upper(EVENT_TYPE)} at {os.environ.get('CompanyName')}.\
        \nDate & Time - {DATE_TIME[:10]} {DATE_TIME[11:19]}\
        \nAlert Severity - {SEVERITY}\
        \nFailure reason - {alert['error']['description'] or 'Unavailable'}
        \n\nAffected Device Details\
        \n##################\
        \nHostname - {DEVICE_DETAILS['hostname']}\
        \nNetwork Interfaces - {DEVICE_DETAILS['network_addresses']}\
        \nExternal IP - {DEVICE_DETAILS['external_ip']}
        \n\nRoot Cause of Alarm\
        \n################\
        \nfile disposition - {CAUSE['disposition']}\
        \nFile hash - {CAUSE['identity']}\
        \n-------------------- End of Alert --------------------"""
    
    
    room_id = os.environ.get('WebexRoomID') # Webex room ID

    # Create the payload for the Webex API request
    payload = {
        'roomId': room_id,
        'text': MESSAGE
    }

    # Create a PoolManager object from urllib3
    http = urllib3.PoolManager()

    # Send the POST request with the data and headers
    response = http.request('POST', api_endpoint, body=json.dumps(payload), headers=headers)

    # Print the response from the webhook
    print(response.status)




def poll_events():
    """
    Polls AMP API for the latest events based on the Event ID and time period set
    """
    # Cisco Secure Endpoint API endpoint
    API_ENDPOINT = 'https://api.eu.amp.cisco.com'

    # API credentials
    API_USERNAME = os.environ.get('APIKeyID')
    API_PASSWORD = os.environ.get('APIKeySecret')

    #A list of the events we are interested in seeing
    EVENT_ID = [
        553648222, #Threat Detection
        1090519054, #Threat Detected
        553648143, #Threat Quarantined
        2164260880, #Quarantine Failure
    ]
    # API endpoint to fetch events
    events_url = API_ENDPOINT + '/v1/events'

    #Pool manager to handle the requests
    http = urllib3.PoolManager()
 
    #Create a latest timestamp paramater for each ID so you can reference the last alert
    latest_timestamps = load_timestamps()
    day_amount = datetime.datetime.now() - datetime.timedelta(float(os.environ.get('Days'))) #Select the amount of days to look back
    date = day_amount.strftime('%Y-%m-%dT%H:%M:%S.%fZ') #the value expected is as string so convert it to include HMS
   
    #Cycle through the event IDs
    for i in EVENT_ID:
        #Create a try catch block so the function will handle errors gracefully
        try:    
            event_id = i #load event_id fron the EVENT_ID list
            # Create an HTTP basic authentication header
            auth_header = urllib3.util.make_headers(basic_auth=f'{API_USERNAME}:{API_PASSWORD}')

            # Set the query parameters 
            query_params= {}
            query_params["start_date"]= date
            query_params["event_type"]= event_id
            
            # Make a GET request to fetch events
            response = http.request(
                'GET',
                events_url,
                headers=auth_header,
                retries=False,
                timeout=urllib3.Timeout(connect=5.0, read=10.0),
                redirect=False,
                fields=query_params
            )
            response_json = json.loads(response.data.decode('utf-8')) #collect the response and change from bytes int UTF

            # Process the events
            if response_json.get('data'): #check that data was returned in the request
                events = response_json['data'] #create a variable to hold the data
                reverse_events = events[::-1] #reverse the events so that he earliest is seen first that way only the newest events will get past the timestamp
                for event in reverse_events: #cycle through the events one by one
                    
                    if event['timestamp'] > latest_timestamps[event['event_type']]: #check the timestamp to make sure you are not repeating alerts      
                            print(event) #print the alert
                            latest_timestamps[event['event_type']] = event['timestamp'] #update the timestamp
                            #Send the alert to Webex
                            webex_message(event)
                    else:
                        print("No New Alerts")

        #catch any acceptions and handle the errors so the function doesnt stop
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the error or retry if needed
    # Update the variable in S3
    save_timestamps(latest_timestamps)  


if __name__ == '__main__':
    # Start polling for events
    load_dotenv()
    poll_events()