from twitchio.ext import commands, pubsub
from keep_alive import keep_alive
from datetime import date
import requests
import twitchio
import os
import os.path

my_token = os.environ['MY_TOKEN']
users_oauth_token = os.environ['CHANNEL_TOKEN']
channel = 'Shakerz_92'

headers = {'Authorization': os.environ['OAUTH'],
           'Client-Id': os.environ['CLIENT_ID']}
users_channel_id = int(requests.get(
    'https://api.twitch.tv/helix/users?login=' + channel, headers=headers).json()['data'][0]['id'])


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
    # event.fulfill()
    # print(dir(event))
    # print(event.status)
    print(event.reward.title)
    # print(event.user)
    
    user = event.user.name
    
    today = date.today().strftime("%d_%m_%Y")
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
client.loop.run_forever()
