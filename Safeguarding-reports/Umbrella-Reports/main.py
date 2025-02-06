#This script creates a safeguarding report in HTML format by querying Umbrella and Meraki APIs
#This function can be run locally only 
#Author Rob Zabel

from datetime import datetime as dt
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import jinja2
import requests
import json
import os

load_dotenv()

def poll_umbrella():
    """
    Poll the Umbrella Reporting API to get blocked activty
    """
    # OAuth2 endpoint and Credentials
    auth_url = os.getenv('UMBRELLA_AUTH_URL')
    client_id = os.getenv('UMBRELLA_CLIENT_ID')
    client_secret = os.getenv('UMBRELLA_CLIENT_SECRET')

    #Send basic auth request to get bearer token
    r = requests.get(auth_url, auth=(client_id, client_secret))

    #Extract access token from the response
    access_token = r.json()['access_token']

    #set the headers with the bearer token
    headers = {
        'Content-type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    #Provide paramaters for the report search
    params = { 
        'from': '-48hours',
        'to': 'now',
        'limit': 200,
        'verdict': 'blocked',
        'categories' : [40,64,161,166,170,121,176,204,44,30,197,174,10,122,166,13]
    }
    #send a request to get activity
    r = requests.get(os.environ.get('REPORTING_URL'), params=params, headers=headers)
    
    #Return a JSON object of the Umbrella report data in the form of a Python dictionary
    return json.loads(r.text)

def get_user_info(umbrella_data):
    """
    Takes a list of private IPs from Umbrella response, calls the Meraki API and returns a JSON object of the private IP to username Mappings 
    """
    #Set Global variables
    SERIAL = os.getenv('MERAKI_SERIAL_NUMBER') #This needs to be the serial number of the Meraki MX
    API_KEY = os.getenv('MERAKI_API_KEY') #this needs to be a meraki admin's API Key, currently set to Rob's
    URL = os.getenv('MERAKI_URL') + f"/devices/{SERIAL}/clients" #Create the full URL 
    NETWORK_ID = os.getenv('MERAKI_NETWORK_ID') #The network ID pulled from Meraki

    #Add authentication to the header
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }

    #Pull all clients on the MX
    meraki_data = requests.get(URL, headers=headers)
    
    #Only want details of users we can identify 
    alerts = []
    for meraki in meraki_data.json():   #iterate through each result in the merki data set     
        for umbrella in umbrella_data:  #iterate through each result in the umberlla data
            if meraki['ip'] == umbrella['internalip']: #compare the internal IP to see if they match. If they dont, using the same meraki result, compare the next Umbrella result
                CLIENT_URL = os.getenv('MERAKI_URL') + f"/networks/{NETWORK_ID}/clients/{meraki['id']}"#if the IPs match make another call to the meraki api using the user ID 
                r = requests.get(CLIENT_URL, headers=headers)
                meraki_username_request = r.json()#return the full user details from the meraki request
                meraki_username = meraki_username_request.get('user') if meraki_username_request.get('user') else "Unavailable"#from the full details grab the username
                alerts.append(
                    {"blocked_domain" : umbrella.get('domain'), "date": umbrella.get('date'), "time" :umbrella.get('time'), "internal_ip": umbrella.get('internalip'), "hostname": meraki.get('dhcpHostname') or "No Hostname Available", "description" : meraki.get('description')or "No Description Available", "user" : meraki_username, "reason":umbrella['policycategories'][0]['label']}
                    )#set variables for the fields of the report
                umbrella_data.remove(umbrella)#remove this item from the umbrella data so it is not checked again
    #return the name to username mappings
    return alerts
    
def create_html(blocked_domains):
    """
    Creates a new report if it is the first run of the day
    """

    #Load the HTML template file
    template = jinja2.Environment(loader=jinja2.FileSystemLoader("/home/rob/AWSLambdaScripts/Umbrella-Reports/templates")).get_template("index.html")
   
    #Data to be rendered
    date = dt.now().strftime('%d-%m-%Y')
    information = sorted(blocked_domains, key=lambda x:x['time'], reverse=True)

    #Create context variable to be overlayed to the HTML file
    context = {
        "customer_name" :"Customer name",
        "blocked_domain": information,
        "date_of_report" : date 
        
    }
    #Render the information to the file
    reportText = template.render(context)
    #write the data to the file
    with open(f"/home/rob/AWSLambdaScripts/Umbrella-Reports/reports/umbrella_report {dt.now().date()}.html", mode='w') as f:
        f.write(reportText)


def append_html(blocked_domains):
    """
    Appends information to the report if it is the same day
    """
    #Open the file with Beautiful soup
    with open(f"/home/rob/AWSLambdaScripts/Umbrella-Reports/reports/umbrella_report {dt.now().date()}.html",'r') as f:
        soup = BeautifulSoup(f, "html.parser")
    
    #sort the info into date order
    information = sorted(blocked_domains, key=lambda x:x['time'])
    # Find the table by its id
    table = soup.find('table', {'id': 'data_table'})

    #create the table structure
    new_row = soup.new_tag('tr')
    new_blocked_domain = soup.new_tag('td')
    new_reason = soup.new_tag('td')
    new_internal_ip = soup.new_tag('td')
    new_hostname = soup.new_tag('td')
    new_description = soup.new_tag('td')
    new_user = soup.new_tag('td')
    new_date = soup.new_tag('td')
    new_time = soup.new_tag('td')
    
    for item in information:
        #add data to table structure
        new_blocked_domain.string = item.get('blocked_domain')
        new_reason.string = item.get('reason')
        new_internal_ip.string = item.get('internal_ip')
        new_hostname.string = item.get('hostname')
        new_description.string = item.get('description')
        new_user.string = item.get('user') 
        new_date.string = item.get('date')
        new_time.string = item.get('time')
        #add data to table
        new_row.append(new_blocked_domain)
        new_row.append(new_reason)
        new_row.append(new_internal_ip)
        new_row.append(new_hostname)
        new_row.append(new_description)
        new_row.append(new_user)
        new_row.append(new_date)
        new_row.append(new_time)
        #add table data to the HTML
        table.insert(1,new_row)

    with open(f"/home/rob/AWSLambdaScripts/Umbrella-Reports/reports/umbrella_report {dt.now().date()}.html",'w') as f:   
        f.write(str(soup.prettify()))


if __name__ == '__main__':
    try:
        umbrella_data = poll_umbrella()
    except Exception as e:
        print(e)
    try:
        blocked_domains = (get_user_info(umbrella_data['data']))
    except Exception as e:
        print(e)
    create_html(blocked_domains)#Used for testing if a document has not been created yet
    #if (dt.now().hour == 00): #if its 12:00 AM, the start of a new day, run the whole document
     #   create_html(blocked_domains)
    #else: # if its not the start of a new day, append the info to the table
     #   append_html(blocked_domains)
    
