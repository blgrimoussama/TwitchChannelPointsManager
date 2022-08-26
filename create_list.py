import json, requests, os

list = [
    'mohannd__', 'lYASERl', 'alkenali', 'Amj4do', 'Abumunir', 'Kipoi',
    'Mc_brro', 'F7g_', 'SweetHanin', 'loobs7', 'Oshow', 'aziz_black',
    'SSNz_92', 'Amj4do', 'DreamVX', 'Fatalframer_q8', 'Klopiski_pie',
    'Irampage88', 'iMorrii', '1Marcelin1', 'khaled004', 'tariqtop', 'f1ix_1',
    'JnrDragon2', 'Hussain149'
]

headers = {
    'Authorization': os.environ['OAUTH'],
    'Client-Id': os.environ['CLIENT_ID']
}
dict = {}

for element in list:
    try:
        user_id = int(
            requests.get('https://api.twitch.tv/helix/users?login=' + element,
                         headers=headers).json()['data'][0]['id'])
    except (IndexError, KeyError):
        user_id = 0
    dict[element] = user_id
with open(os.path.join('static', 'black_list.json'), "a") as data:
    json.dump(dict, data, indent=4)
