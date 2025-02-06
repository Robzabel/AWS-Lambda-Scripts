import requests
import os


"""
Request HTTP options:
"""
r = requests.get('https://api.github.com/events')
r = requests.post('https://httpbin.org/post', data={'key': 'value'})
r = requests.put('https://httpbin.org/put', data={'key': 'value'})
r = requests.delete('https://httpbin.org/delete')


"""
Passing paramaters in the URL:
The PARAMS dictionary is passed to the target URL. This is the same as adding paramaters after the ? in a regular HTTP request
"""
#Paramaters are passed as Python dictionaries
payload ={'key1': 'value1', 'key2': 'value2'}
r = requests.get('https://httpbin.org/get', params=payload)
#You can also add multiple vlaues to a single key:
payload = {'key1': 'value1', 'key2': ['value2', 'value3']}


"""
Custom Headers:
Metadata details are passed in the request header
"""
#Headers are passed as dictionaries
url = 'https://api.github.com/some/endpoint'
headers = {'user-agent': 'my-app/0.0.1'}
r = requests.get(url, headers=headers)

#Content type is passed in the headers of a request, this specifies what kind of data is contained in the request.
#The most common content type header is for a json payload:
headers = {"Content-type": "application/json"}


"""
Authentication:
Most APIs will require a form of authentication
"""
#Basic Authentication can be done by importing the module and explicitly creating a variable or it can be passed in line:
from requests.auth import HTTPBasicAuth
basic = HTTPBasicAuth('user', 'pass')
requests.get('https://httpbin.org/basic-auth/user/pass', auth=basic)
#Or
requests.get('https://httpbin.org/basic-auth/user/pass', auth=('user', 'pass'))

#When it comes to Oauth2, there are some extra steps needed to authenticate:
#Firstly you need to pass the API key and Vaule as the basic authentication above. This will respond with an access token
auth_url = os.getenv('ENDPOINT_URL')
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
r = requests.get(auth_url, auth=(client_id, client_secret))
access_token = r.json()['access_token']
#Secondly, you needd to pass the bearer token in the header of each subsequent requset
headers = {
    'Content-type': 'application/json',
    'Authorization': f'Bearer {access_token}'
}



"""
Post requests with data:
We can post data to an endpoint (sometimes we need to encode it specifically)
"""
#Typically you want to send form-encoded data like an HTML form, to do this just pass a dictionary to the data argument
payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.post('https://httpbin.org/post', data=payload)
#You can pass multiple values in the payload:
payload_dict = {'key1': ['value1', 'value2']}
r2 = requests.post('https://httpbin.org/post', data=payload_dict)



"""
Response objects:
"""
#Requests automatically decodes response content, this can be changed with:
r.encoding = 'utf-8'

#To get a string format of the entire response json, use text:
r.text 

#response content can be retrieved in bytes:
r.content

#JSON content can be retrieved and converted to python code with:
r.json()

#return the status code of the request:
r.status_code

#return session cookie:
r.cookies['example_cookie_name']