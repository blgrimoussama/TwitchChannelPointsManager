import requests, json, os
headers = {'Authorization': os.environ['OAUTH'],
           'Client-Id': os.environ['CLIENT_ID']
          }

channel = 'shakerz_92'
broadcaster_id = int(requests.get(
    'https://api.twitch.tv/helix/users?login=' + channel, headers=headers).json()['data'][0]['id'])

reward_id_2 = '2ea13608-4e4c-4934-a5cc-ebefe5e1a410'
reward_id = 'd6cd3231-fca4-4530-8206-2c1b9b16450e'

headers_2 = headers = {'Client-Id': os.environ['CLIENT_ID_2'], 
                   'Authorization': 'Bearer ' + os.environ['shakerz_92_CHANNEL_TOKEN'], 
                   'Content-type': 'application/json'}

# id = '6cf6eaef-99c6-4286-a8fc-36dd971f4047'

params = {'broadcaster_id' : broadcaster_id}
          # 'after': "eyJiIjpudWxsLCJhIjp7IkN1cnNvciI6ImV5SmphR0Z1Ym1Wc1gybGtJam9pTlRFMU5qVTRNellpTENKamNtVmhkR1ZrWDJSaGRHVWlPaUl5TURJeUxUQTRMVEEwVkRBMU9qUTBPalUxTGpFME5UazBOekU1T1ZvaUxDSnBaQ0k2SWpCbE5qSXlZalJrTFdWbE1qZ3ROR0V4TUMwNVlqSmxMVEF6WWpsaU4yWXpNRE5sWXlKOSJ9fQ"}

data = requests.get(
    'https://api.twitch.tv/helix/predictions', headers=headers, params=params).json()

with open('prediction_13.json', "a") as f:
    json.dump(data, f, indent = 4)

titles = {}
for prediction in data['data']:
    if 'تبرع' in prediction['title']:
        with open('prediction_13.txt', "a") as f:
            f.write(prediction['title'] + '\n')
        outcomes = []
        for outcome in prediction['outcomes']:
            if not '10' in outcome['title']:
                outcomes.append(outcome)
        titles[prediction['title']] = {'outcome': outcomes, 'created_at': prediction['created_at']}

with open('prediction_outcomes_13.json', "a") as f:
    json.dump(titles, f, indent = 4)