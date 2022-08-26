import requests, json, os

headers = {
    'Authorization': os.environ['OAUTH'],
    'Client-Id': os.environ['CLIENT_ID']
}

channel = 'shakerz_92'
broadcaster_id = int(
    requests.get('https://api.twitch.tv/helix/users?login=' + channel,
                 headers=headers).json()['data'][0]['id'])

reward_id = '2ea13608-4e4c-4934-a5cc-ebefe5e1a410'
reward_id_2 = 'd6cd3231-fca4-4530-8206-2c1b9b16450e'

headers_2 = headers = {
    'Client-Id': os.environ['CLIENT_ID_2'],
    'Authorization': f"Bearer {os.environ['shakerz_92_CHANNEL_TOKEN']}",
    'Content-type': 'application/json'
}

params = {
    'broadcaster_id': broadcaster_id,
    'reward_id': reward_id,
    'status': "UNFULFILLED",
    'first': 30,
    'after': None
}

data = requests.get(
    'https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions',
    headers=headers,
    params=params).json()

with open('z_3.json', "a") as f:
    json.dump(data, f, indent=4)
