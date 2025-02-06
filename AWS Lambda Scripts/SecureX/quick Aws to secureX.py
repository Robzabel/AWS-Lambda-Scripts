import urllib3
import json
from dotenv import load_dotenv
import os

load_dotenv()

webhook_url = os.getenv('SECUREX_WEBHOOK_URL')

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
http = urllib3.PoolManager(headers=headers)

payload = {"body":"test"}

response = http.request('POST', webhook_url, body=json.dumps(payload))
print(response.status)
print(response.data)