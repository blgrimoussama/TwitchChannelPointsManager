from config import CLIENT_ID, CLIENT_SECRET
from requests import request
import json

url = "https://id.twitch.tv/oauth2/token"

data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": 'client_credentials'
}

response = request('POST', url, auth=(CLIENT_ID, CLIENT_SECRET), data=data)

code_json = response.json()
# print(json.dumps(code_json, indent=4))

AOUTH = f'Bearer {code_json["access_token"]}'
print(AOUTH)
