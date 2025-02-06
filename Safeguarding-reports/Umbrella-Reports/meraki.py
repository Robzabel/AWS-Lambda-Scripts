from dotenv import load_dotenv
import requests
import os

"""
Queries the Meraki API and returns client data
"""

load_dotenv()
#Set Global variables
SERIAL = os.getenv('MERAKI_SERIAL_NUMBER') #This needs to be the serial number of the Meraki MX
API_KEY = os.getenv('MERAKI_API_KEY') #this needs to be a meraki admin's API Key, currently set to Rob's
URL = os.getenv('MERAKI_URL') + f"/devices/{SERIAL}/clients"

#Add authentication to the header
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

#Pull all clients on the MX
meraki_data = requests.get(URL, headers=headers)
#save the Meraki data to a file
with open(f"./reports/meraki data.json", mode='w') as f:
    f.write(meraki_data.text)

#Find the ID of a client from the report and add it here to make another API call for full details of the device
client_id = ""
CLIENT_URL = os.getenv('ERAKI_NETWORK_ID') + f"{client_id}" 
r = requests.get(CLIENT_URL, headers=headers)

print(r.text)