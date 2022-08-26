from datetime import date, timedelta, datetime
import requests
import json
import os

day_json = os.path.join('static', 'day.json')
last = os.path.join('static', 'last.txt')
last_json = os.path.join('static', 'last.json')

with open(day_json, "r") as data:
    day = json.load(data)
next = day['today']

today = datetime.strptime(next, '%d/%m/%Y').strftime("%d_%m_%Y")
current = os.path.join('static', f'spin_{today}.txt')
current_json = os.path.join('static', f'spin_{today}.json')
user = 'salma1023'
headers = {
    'Authorization': os.environ['OAUTH'],
    'Client-Id': os.environ['CLIENT_ID']}
try:
    resp = requests.get(f'https://api.twitch.tv/helix/users?login={user}', headers=headers).json()['data'][0]
    print(resp)
    user_id = resp['id']
    user = resp['display_name']
except (AttributeError, IndexError, KeyError):
    print('مين ذا؟')
with open(last_json, "r") as participants:
    users = json.load(participants)
if user_id in users.keys() and users[user_id]['mode'] == 'cheat':
    file = open(last, "r")
    data = file.read().strip().split('\n')
    remove = input('remove? ')
    if remove.lower() == 'yes':
        print(users[user_id]['user'])
        new = data
        new.remove(users[user_id]['user'])
        print(new)
        with open(current, "w") as f:
            f.write('\n'.join(new) + '\n')
        with open(current_json, "r") as data:
            file_data = json.load(data)
        with open(current_json, "w") as data:
            del file_data[user_id]
            # convert back to json.
            json.dump(file_data, data, indent = 4)
#     with open(last_json, "w") as data:
#         json.dump(file_data, data, indent = 4)
#     print(f'{user} entered wastah!')
# else:
#     print(f'{user} is already in, mayhtaj!')