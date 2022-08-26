from twitchio.ext import commands, pubsub, routines
from keep_alive import keep_alive
from datetime import date, timedelta, datetime
import requests
import twitchio
import os
import os.path
import json

my_token = os.environ['MY_TOKEN']
users_oauth_token = os.environ['CHANNEL_TOKEN']
channel = 'Shakerz_92'

headers = {'Authorization': os.environ['OAUTH'],
           'Client-Id': os.environ['CLIENT_ID']}
users_channel_id = int(requests.get(
    'https://api.twitch.tv/helix/users?login=' + channel, headers=headers).json()['data'][0]['id'])

isOn = False

with open('day.json', "r") as data:
    day = json.load(data)
# next = datetime.strptime(day['today'], '%d/%m/%Y')
next = day['today']


class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        super().__init__(token=os.environ['paperrocker'], prefix='?', initial_channels=['shakerz_92', '0us5ama'])

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        self.test.start('')
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        global next, isOn
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        msg = message.content.lower()
        s = msg.split()
        author = message.author.name
        self.channel = self.get_channel('shakerz_92')
        
        if s[0] == '!switch' and author in ['shakerz_92', '0us5ama']:
            with open('day.json', "r") as data:
                day = json.load(data)
            day['today'] = (datetime.strptime(day['today'], '%d/%m/%Y') + timedelta(days=1)).strftime("%d/%m/%Y")
            next = day['today']
            print(next)
            print(day)
            with open('day.json', "w") as data:
                json.dump(day, data)
            await message.channel.send('switched to tomorrow')
        if msg == '!routines' and author in ['shakerz_92', '0us5ama']:
            isOn = not isOn
            outcome = 'working' if isOn else 'stopped'
            await message.channel.send(f'routines are now {outcome}')
        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        
        await self.handle_commands(message)

    @routines.routine(seconds=30)
    async def test(self, arg):
        global isOn 
        if isOn:
            await self.get_channel('shakerz_92').send(f'Test {arg}')
            print('test')


    @commands.command()
    async def hello(self, ctx: commands.Context):
        # Here we have a command hello, we can invoke our command with our prefix and command name
        # e.g ?hello
        # We can also give our commands aliases (different names) to invoke with.

        # Send a hello back!
        # Sending a reply back to the channel is easy... Below is an example.
        await ctx.send(f'Hello {ctx.author.name}!')
    
    

client = twitchio.Client(token=my_token)
# print(dir(twitchio.Client))
# channels = ['shakerz_92']
# twitchio.Client.join_channels(channels)
client.pubsub = pubsub.PubSubPool(client)

@client.event()
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    pass  # do stuff on bit redemptions

@client.event()
async def event_message(self, message): # : twitchio.Message):
    print(message)


@client.event()
async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
    global next
    # event.fulfill()
    # print(dir(event))
    # print(event.status)
    print(event.reward.title)
    # print(event.user)
    
    user = event.user.name
    
    today = datetime.strptime(next, '%d/%m/%Y').strftime("%d_%m_%Y")
    print(today)
    if event.reward.title == 'سحب على 10 دولار':
        try:
            fil = open(f'spin_{today}.txt')
        except FileNotFoundError:
            with open(f'spin_{today}.txt', 'a') as fil:
                pass
        fil = open(f'spin_{today}.txt')
        if not '\n' + user + '\n' in '\n' + fil.read():
            fil.close()
            with open(f'spin_{today}.txt', 'a') as f:
                f.write(user + '\n')
    # twitchio.CustomRewardRedemption(users_oauth_token)


async def main():
    topics = [
        pubsub.channel_points(users_oauth_token)[users_channel_id]
    ]
    await client.pubsub.subscribe_topics(topics)
    await client.start()
    print(f'connected to {channel}')

client.loop.create_task(main())
keep_alive()
bot = Bot()
bot.pubsub_client = client
bot.run()

# bot.run() is blocking and will stop execution of any below code here until stopped or closed.