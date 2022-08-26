from twitchio.ext import commands, pubsub, routines
from datetime import date, timedelta, datetime
from hypercorn.config import Config
from hypercorn.asyncio import serve
from quart import Quart, render_template, redirect, send_from_directory
from func import apology, change_reward_status
import asyncio
import requests
import twitchio
import os
import os.path
import json

import nest_asyncio

nest_asyncio.apply()

# import logging
# logging.basicConfig(filename="log_.txt", level=logging.DEBUG)
headers = {
    'Authorization': os.environ['OAUTH'],
    'Client-Id': os.environ['CLIENT_ID']
}

my_token = os.environ['MY_TOKEN']
client_id_2 = os.environ['CLIENT_ID_2']
channels = ['shakerz_92']
users_oauth_tokens = {}
users_channel_ids = {}
day_jsons = {}
lasts = {}
last_jsons = {}
nexts = {}
todays = {}
currents = {}
current_jsons = {}
for channel in channels:
    users_oauth_tokens[channel] = os.environ[f'{channel}_CHANNEL_TOKEN']
    users_channel_ids[channel] = int(
        requests.get('https://api.twitch.tv/helix/users?login=' + channel,
                     headers=headers).json()['data'][0]['id'])
    day_jsons[channel] = os.path.join(f'static/{channel}', 'day.json')
    lasts[channel] = os.path.join(f'static/{channel}', 'last.txt')
    last_jsons[channel] = os.path.join(f'static/{channel}', 'last.json')
    with open(day_jsons[channel], "r") as data:
        day = json.load(data)
    nexts[channel] = day['today']
    todays[channel] = datetime.strptime(nexts[channel],
                                        '%d/%m/%Y').strftime("%d_%m_%Y")

    currents[channel] = os.path.join(f'static/{channel}',
                                     f'spin_{todays[channel]}.txt')
    current_jsons[channel] = os.path.join(f'static/{channel}',
                                          f'spin_{todays[channel]}.json')

app = Quart(__name__)
isOn = False

# environment = Environment(
#     autoescape=select_autoescape()
# )


@app.route("/data/<channel>/<path:path>")
async def get_txt(channel, path):
    try:
        if not path.endswith('.txt'):
            raise FileNotFoundError
        with open(os.path.join(f'static/{channel}', path), "r") as f:
            content = f.read()
        return {"participants": content.strip().split('\n')}
    except FileNotFoundError:
        # raise ValueError('No such file')
        return await apology('FileNotFoundError', 500)


@app.route('/')
async def index():
    return 'What do you want here ?! 🙄'


@app.route("/static/<channel>/<path:path>")
async def static_dir(channel, path):
    return await send_from_directory(f"static/{channel}", path)


@app.route("/spin/<channel>/<path:path>")
async def spin(channel, path):
    data = await get_txt(channel, path)
    # print(data['participants'].strip().split('\n'))
    if not isinstance(data, tuple):
        return await render_template('last.html',
                                     title=path.replace('.txt', ''),
                                     data=data['participants'],
                                     channel=channel)
    else:
        return await apology('FileNotFoundError', 500)


@app.route("/spins/<path:path>")
async def spins(path):
    data = await get_txt(path)
    # print(data['participants'].strip().split('\n'))
    if not isinstance(data, tuple):
        return await render_template('spin.html',
                                     title=path.replace('.txt', ''),
                                     data=data['participants'])
    else:
        return redirect(f'/{path}', code=302)


@app.route("/test/<path:path>")
async def test(path):
    data = await get_txt(path)
    # print(data['participants'].strip().split('\n'))
    if not isinstance(data, tuple):
        return await render_template('last_2.html',
                                     title=path.replace('.txt', ''),
                                     data=data['participants'])
    else:
        return redirect(f'/{path}', code=302)


class Bot(commands.Bot):
    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=os.environ['paperrocker'],
                         prefix=']',
                         initial_channels=list(set().union(
                             channels, ['shakerz_92', '0us5ama'])))

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        self.test.start('')
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        global nexts, todays, currents, current_jsons, isOn
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        msg = message.content.lower()
        msg_raw = message.content
        s = msg.split()
        s_raw = msg_raw.split()
        author = message.author.name
        mention = message.tags['display-name']
        channel_name = message.channel.name
        # self.channel = self.get_channel('shakerz_92')
        if s[0] == '!switch' and author in [channel_name, '0us5ama']:
            day_json = day_jsons[channel_name]
            last = lasts[channel_name]
            last_json = last_jsons[channel_name]
            current = currents[channel_name]
            current_json = current_jsons[channel_name]
            today = todays[channel_name]
            with open(day_json, "r") as data:
                day = json.load(data)
            day['today'] = (datetime.strptime(day['today'], '%d/%m/%Y') +
                            timedelta(days=1)).strftime("%d/%m/%Y")
            next = nexts[channel_name] = day['today']
            today = todays[channel_name] = datetime.strptime(
                next, '%d/%m/%Y').strftime("%d_%m_%Y")
            current = currents[channel_name] = os.path.join(
                f'static/{channel_name}', f'spin_{today}.txt')
            current_json = current_jsons[channel_name] = os.path.join(
                f'static/{channel_name}', f'spin_{today}.json')

            with open(day_json, "w") as data:
                json.dump(day, data)

            with open(last, "w") as f:
                pass
            with open(current, "a") as f:
                pass
            with open(current_json, "w") as f:
                f.write(json.dumps({}))

            await message.channel.send('switched to tomorrow')

            with open(os.path.join(f'static/{channel_name}', 'reward.json'),
                      "r") as data:
                data = json.load(data)
            reward_id = data['reward_id']

            with open(last_json, "r") as data:
                rewards = json.load(data)
            with open(last_json, "w") as f:
                f.write(json.dumps({}))
            rewards = rewards.values()
            # ids = [ reward['reward_id'] for reward in rewards if reward['reward_id']]
            users_oauth_token = users_oauth_tokens[channel_name]
            users_channel_id = users_channel_ids[channel_id]
            for reward in rewards:
                id = reward['reward_id']
                user = reward['user']
                if user == '0US5AMA':
                    change_reward_status(client_id_2, users_oauth_token,
                                         users_channel_id, reward_id, id,
                                         "CANCELED")
                else:
                    change_reward_status(client_id_2, users_oauth_token,
                                         users_channel_id, reward_id, id,
                                         "FULFILLED")
        elif s[0] in ['واسطة؟', 'واسطه؟'
                      ] and len(s) > 1 and author in [channel_name, '0us5ama']:
            user = s_raw[1].replace('@', '')
            try:
                resp = requests.get(
                    f'https://api.twitch.tv/helix/users?login={user}',
                    headers=headers).json()['data'][0]
                user_id = resp['id']
                user = resp['display_name']
            except (AttributeError, IndexError):
                return await message.channel.send('مين ذا؟')
            last = lasts[channel_name]
            last_json = last_jsons[channel_name]
            current = currents[channel_name]
            current_json = current_jsons[channel_name]
            with open(last_json, "r") as participants:
                users = json.load(participants)
            if not user_id in users.keys():
                with open(last, "a") as f:
                    f.write(user + '\n')
                with open(current, "a") as f:
                    f.write(user + '\n')
                participant = {
                    "user": user,
                    "reward_id": 0,
                    "time": 0,
                    "mode": 'cheat'
                }
                with open(current_json, 'r+') as data:
                    # First we load existing data into a dict.
                    try:
                        file_data = json.load(data)
                    except ValueError:
                        file_data = {}
                    # Join new_data with file_data inside emp_details
                    file_data[user_id] = participant
                    # Sets file's current position at offset.
                    data.seek(0)
                    # convert back to json.
                    json.dump(file_data, data, indent=4)
                with open(last_json, "w") as data:
                    json.dump(file_data, data, indent=4)
                await message.channel.send(f'{user} entered wastah!')
            else:
                await message.channel.send(f'{user} is already in, mayhtaj!')
        elif s[0] in ['!win'
                      ] and len(s) > 1 and author in [channel_name, '0us5ama']:
            user = s_raw[1].replace('@', '')

            try:
                resp = requests.get(
                    f'https://api.twitch.tv/helix/users?login={user}',
                    headers=headers).json()['data'][0]
                user_id = int(resp['id'])
                user = resp['display_name']
            except (AttributeError, IndexError, KeyError):
                return await message.channel.send('مين ذا؟')
            with open(
                    os.path.join(f'static/{channel_name}', 'black_list.json'),
                    "r") as data:
                black_list = json.load(data)
            if not user_id in black_list.values():
                black_list[user] = user_id
                with open(
                        os.path.join(f'static/{channel_name}',
                                     'black_list.json'), "w") as data:
                    json.dump(black_list, data, indent=4)
                await message.channel.send(f"{user} added to the winners' list"
                                           )
            else:
                await message.channel.send(f"{user} is already in the list")
        elif s[0] in ['براع؟'
                      ] and len(s) > 1 and author in [channel_name, '0us5ama']:
            user = s_raw[1].replace('@', '')
            try:
                resp = requests.get(
                    f'https://api.twitch.tv/helix/users?login={user}',
                    headers=headers).json()['data'][0]
                user_id = resp['id']
                user = resp['display_name']
            except (AttributeError, IndexError, KeyError):
                return await message.channel.send('مين ذا؟')
            last = lasts[channel_name]
            last_json = last_jsons[channel_name]
            current = currents[channel_name]
            current_json = current_jsons[channel_name]
            with open(last_json, "r") as participants:
                users = json.load(participants)
            if user_id in users.keys():
                if users[user_id]['mode'] == 'cheat':
                    file = open(last, "r")
                    data = file.read().strip().split('\n')
                    data.remove(users[user_id]['user'])
                    with open(current, "w") as f:
                        f.write('\n'.join(data) + '\n')
                    with open(last, "w") as f:
                        f.write('\n'.join(data) + '\n')
                    with open(current_json, "r") as data:
                        file_data = json.load(data)
                    with open(current_json, "w") as data:
                        del file_data[user_id]
                        json.dump(file_data, data, indent=4)
                    with open(last_json, "w") as data:
                        json.dump(file_data, data, indent=4)
                    await message.channel.send(f'{user} براااااااااااااع')
                else:
                    await message.channel.send(f'ما يمديك {user} دافع فلووس')
            else:
                await message.channel.send(f'{user} مو موجود أصلا Kappa')
        # elif msg == '!routines' and author in ['shakerz_92', '0us5ama']:
        #     isOn = not isOn
        #     outcome = 'working' if isOn else 'stopped'
        #     await message.channel.send(f'routines are now {outcome}')
        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...

        await self.handle_commands(message)

    @routines.routine(seconds=30)
    async def test(self, arg):
        global isOn
        if isOn:
            await self.get_channel('shakerz_92').send(f'Test {arg}')

    # @commands.command()
    # async def hello(self, ctx: commands.Context):
    #     # Here we have a command hello, we can invoke our command with our prefix and command name
    #     # e.g ?hello
    #     # We can also give our commands aliases (different names) to invoke with.

    #     # Send a hello back!
    #     # Sending a reply back to the channel is easy... Below is an example.
    #     await ctx.send(f'Hello {ctx.author.name}!')


client = twitchio.Client(token=my_token)
# print(dir(twitchio.Client))
# channels = ['shakerz_92']
# twitchio.Client.join_channels(channels)
client.pubsub = pubsub.PubSubPool(client)


@client.event()
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    pass  # do stuff on bit redemptions


@client.event()
async def event_pubsub_channel_points(
        event: pubsub.PubSubChannelPointsMessage):
    global next
    # event.fulfill()
    # print(dir(event))
    # print(event.status)
    # print(event.user)
    user = event.user.name
    print(event.reward.title, user)
    reward_id = event.reward.id
    channel_name = requests.get(
        f'https://api.twitch.tv/helix/users?id={event.channel_id}',
        headers=headers).json()['data'][0]['login']
    with open(os.path.join(f'static/{channel_name}', 'reward.json'),
              "r") as data:
        reward = json.load(data)
    if event.reward.title == reward['title']:
        reward_id = event.reward.id
        id = event.id
        user_id = event.user.id
        with open(last_jsons[channel_name], "r") as participants:
            users = json.load(participants)
        # with open(os.path.join('static', 'black_list.json'), "r") as data:
        #     black_list = json.load(data)
        if not str(user_id) in users.keys():
            with open(lasts[channel_name], "a") as f:
                f.write(user + '\n')
            with open(currents[channel_name], "a") as g:
                g.write(user + '\n')
            participant = {
                "user": user,
                "reward_id": id,
                "time": str(event.timestamp),
                "mode": 'normal'
            }
            with open(current_jsons[channel_name], "r+") as data:
                try:
                    file_data = json.load(data)
                except ValueError:
                    file_data = {}
                file_data[user_id] = participant
                # Sets file's current position at offset.
                data.seek(0)
                # convert back to json.
                json.dump(file_data, data, indent=4)
            with open(last_jsons[channel_name], "w") as data:
                json.dump(file_data, data, indent=4)
        else:
            change_reward_status(client_id_2, users_oauth_tokens[channel_name],
                                 users_channel_ids[channel_name], reward_id,
                                 id, "CANCELED")


async def main():
    topics = [
        pubsub.channel_points(
            users_oauth_tokens[channel])[users_channel_ids[channel]]
        for channel in channels
    ]
    await client.pubsub.subscribe_topics(topics)
    await client.start()
    print(f'connected to {channel}')


client.loop.create_task(main())

loop = asyncio.get_event_loop()
loop_1 = asyncio.get_event_loop()
config = Config()
config.bind = ['0.0.0.0:8080']
# def debug(text):
#     print(text)
#     return ''
# environment.filters['debug'] = debug
loop.create_task(serve(app, config))
bot = Bot()
bot.pubsub_client = client
bot.run()

# bot.run() is blocking and will stop execution of any below code here until stopped or closed.
