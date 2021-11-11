
import nest_asyncio
nest_asyncio.apply()
import discord
from discord.ext import tasks
from discord.ext import commands, tasks
import redis, json
import pickle
import zlib
import pandas as pd
from tabulate import tabulate


# connect to Redis and subscribe to tradingview messages
r = redis.Redis()
p = r.pubsub()
p.subscribe('tradingview')

### INSERT YOUR BOT TOKEN HERE
TOKEN = 'xxxx'
bot = commands.Bot('!') 

# Change this to whatever seconds you want it to be
x = 2

@tasks.loop(seconds=x)
async def send():

    """Sends something every x seconds"""    
    
    message = p.get_message()
    if message is not None and message['type'] == 'message':        
        rehydrated_df = pickle.loads(zlib.decompress(message['data']))

        # due to the Discord 2000 character limit, I split the table into 10 rows each
        tbls = []
        row_len = 10
        for i in range((len(rehydrated_df)//row_len)+1):
            tbls.append(tabulate(rehydrated_df.iloc[i*row_len:(i*row_len+row_len), :], headers='keys', tablefmt='psql', showindex=False, numalign="right"))
                
        channel = bot.get_channel(1010101010101) #INSER Channel ID HERE 
        for s in tbls:
            await channel.send('```'+s+ '```')


@send.before_loop
async def before():
    await bot.wait_until_ready()

send.start()
bot.run(TOKEN)