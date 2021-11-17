# emailToDiscordBot
Built for a use-case where I needed to post CME QuickStrike Block Trade alerts (https://cmegroup-sso.quikstrike.net/CME/BlockTradeAlerts.aspx) to a Discord server.

Workflow:
1) Sign up to CME using the link above (it's free) and select the asset types you want to receive alerts for
2) Enable the Gmail APi via https://console.cloud.google.com, generate credentials.json, etc. (see section below for more details)
3) Create a Discord bot via https://discord.com/developers (again, detailed guides available online)
4) Install Redis (used to publish data between the email "poller" and the Discord bot)
5) Set up a basic Redis installation
6) Make sure you're able to access emails (credentials.json, etc.) and that you're able to post to Discord (enter the bot's token and channel ID in the discord file)
7) Run both scripts indefinitely
8) ???
9) Profit!

Comments in the files explain what needs to be inserted where (channel ID, etc.)

**Gmail APi "troubleshooting"**
It took me a few tries to get the API working.

This article is a good, quick overview: https://www.javatpoint.com/gmail-api-in-python
If you are running the bot via a VPS, you will probably have issues getting the last step of the authorization to work. The following answer resolved this for me (in short, run the script locally the first time to generate a token file, then copy it over to your server): https://stackoverflow.com/questions/37201250/sending-email-via-gmail-python

Requirements:
- Python (I use 3.9)
- Redis
- Discord.py
- other libraries you'll find in the files - nothing crazy

Drawbacks / improvements:
- Polling Gmail every [x] seconds (10 in my case) isn't ideal. You can set up push alerts via Google Cloud, but I couldn't be bothered
- A never-ending loop in post_to_discord.py that checks for new Redis messages every [x] seconds (2 in my case) also isn't ideal, but is fine for me
