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

# raw_data = '{"title":"سحب على 10 دولار", "cost": 3001}'
raw_data = '{"is_paused": true, "is_enabled": false}'
broadcaster_id = users_channel_id
id = 'c37b4c24-89f3-4966-85ec-900e1e0afd0f'
id_2 = 'cc499b66-b155-4d65-8842-e990f6b40d3b'
r = requests.patch(
f'https://api.twitch.tv/helix/channel_points/custom_rewards?broadcaster_id={broadcaster_id}&id={id_2}',
    headers=headers_2, data=raw_data)
print(r.content)
