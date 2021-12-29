# LRBot
A bot made for [https://less-real.com](https://less-real.com)'s [Discord channel](https://discord.com/invite/3Zd46Uc).  
Invite link: [https://discord.com/api/oauth2/authorize?client_id=841746412705546280&permissions=223296&scope=bot](https://discord.com/api/oauth2/authorize?client_id=841746412705546280&permissions=223296&scope=bot)

Default prefix: `lr!`  
## Available commands:
- `help` - Outputs all available commands.
- `random` - Grabs a random quote from the API.
- `character <character>` - Grab a random quote from a character from the API.
- `qotd <channel> [<role>]` - Grab a random quote, using ✅(accept), 🔄(refresh), 🚫(refresh + blacklist), ❌(cancel) to post to channel and mention role.

## Deploying
Required `Python3.7+`. Tested on `Python3.9`.

1. [**OPTIONAL**] Create venv and activate it.
    1. `python -m venv venv`
    2. `source venv/bin/activate` (Linux) or `venv\Scripts\activate.bat` (Windows)
2. Install requirements: `pip install -r requirements.txt`
3. Create an `.env` file at the root of the project and add the following: 
    1. `DISCORD_TOKEN` equal to the discord token of your application ([https://discord.com/developers/applications](https://discord.com/developers/applications))
4. `python lrbot.py`
