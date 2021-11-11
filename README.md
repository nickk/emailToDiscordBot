# emailToDiscordBot
Built for a use-case where I needed to post CME QuickStrike Block Trade alerts (https://cmegroup-sso.quikstrike.net/CME/BlockTradeAlerts.aspx) to a Discord server.

Workflow:
1) Sign up to CME using the link above (it's free) and select the asset types you want to receive alerts for
2) Enable the Gmail APi via https://console.cloud.google.com, generate credentials.json, etc. (Google for detailed guides)
3) Create a Discord bot via https://discord.com/developers (again, detailed guides available online)
4) Install Redis (used to publish data between the email "poller" and the Discord bot)
5) Set up a basic Redis installation
6) Make sure you're able to access emails (credentials.json, etc.) and that you're able to post to Discord (enter the bot's token and channel ID in the discord file)
7) Run both scripts indefinitely
8) ???
9) Profit!

Comments in the files explain what needs to be inserted where (channel ID, etc.)
