
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


r = redis.Redis()
p = r.pubsub()
p.subscribe('tradingview')


TOKEN = 'xxxxxxxxxxxxx' ################ ENTER BOT TOKEN HERE
bot = commands.Bot('!') # ! = PREFIX

# Change this to whatever seconds you want it to be
# Or delete this line and change the x value into a number on the @tasks.loop param.
x = 2

@tasks.loop(seconds=x)
async def send():

    """Sends something every x seconds"""    
    
    message = p.get_message()
    
    if message is not None and message['type'] == 'message':        
        rehydrated_df = pickle.loads(zlib.decompress(message['data']))
        print(rehydrated_df)
        tit = rehydrated_df.iloc[:1,0].values[0]
        rehydrated_df = rehydrated_df[1:]
        
        tbls = []
        row_len = 10
        for i in range((len(rehydrated_df)//row_len)+1):
            tbls.append(tabulate(rehydrated_df.iloc[i*row_len:(i*row_len+row_len), :], headers='keys', tablefmt='psql', showindex=False, numalign="right"))
                
        channel = bot.get_channel(99999999999999999) ################ ENTER BOT CHANNEL ID HERE
        for s in tbls:
            await channel.send('```'+'*'+tit+'*'+"\n"+s+ '```')


@send.before_loop
async def before():
    await bot.wait_until_ready()

send.start()
bot.run(TOKEN)