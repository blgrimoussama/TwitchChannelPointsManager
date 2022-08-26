import requests
import os
import json

client_id_2 = os.environ['CLIENT_ID_2']
users_oauth_token = os.environ['CHANNEL_TOKEN']

channel = 'Shakerz_92'

headers = {'Authorization': os.environ['OAUTH'],
           'Client-Id': os.environ['CLIENT_ID']}

users_channel_id = int(requests.get(
    'https://api.twitch.tv/helix/users?login=' + channel, headers=headers).json()['data'][0]['id'])

headers_2 = {'Client-Id': client_id_2, 
           'Authorization': 'Bearer ' + users_oauth_token, 
           'Content-type': 'application/json'}

# raw_data = '{"title":"سحب على 10 دولار", "cost": 3000}'
raw_data = '{"title": "براااااااااع", "cost": 30000}'
broadcaster_id = users_channel_id

r = requests.post(
    f'https://api.twitch.tv/helix/channel_points/custom_rewards?broadcaster_id={broadcaster_id}',
    headers=headers_2, data=raw_data.encode('utf-8'))
print(r.content)
with open('reward.json', "w") as data:
    json.dump(r.content.decode('utf-8'), data, indent=4)
