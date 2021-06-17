# LRBot
A bot made for [https://less-real.com](https://less-real.com)'s [Discord channel](https://discord.com/invite/3Zd46Uc).  
Invite link: [https://discord.com/api/oauth2/authorize?client_id=841746412705546280&permissions=149504&scope=bot](https://discord.com/api/oauth2/authorize?client_id=841746412705546280&permissions=149504&scope=bot)

Default prefix: `lr!`  
## Available commands:
- `help` (`h`) - Outputs all available commands.
- `random` (`r`|`rand`) - Grabs a random quote from [less-real's API](https://www.less-real.com/api/v1/)

## Deploying
Required `Python3.7+`. Tested on `Python3.9`.

1. [OPTIONAL] Create venv and activate it.
    1. `python -m venv venv`
    2. `source venv/bin/activate` (Linux) or `venv\Scripts\activate.bat` (Windows)
2. Install requirements: `pip install -r requirements.txt`
3. Create an `.env` file at the root of the project and add the following: 
    1. `DISCORD_TOKEN` equal to the discord token of your application ([https://discord.com/developers/applications](https://discord.com/developers/applications))
    2. `TENOR_TOKEN` equal to the tenor token associated to your account ([https://tenor.com/gifapi](https://tenor.com/gifapi))
4. `python lrbot.py`
