import json
import httpx
import discord
from schemas.command import Command
from settings import DEBUG, TOKEN, PREFIX, client

async def send_random_quote(message):
    """
    Send to channel a random quote from less-real api.

    Parameters:
    message (discord.message.Message): message object send by on_message event.
    """
    async with httpx.AsyncClient() as http_client:
        r = await http_client.get('https://www.less-real.com/api/v1/')
    if r.status_code != 200:
        await message.channel.send('Cannot get quote, request timed out.')
        return
    # less-real returns a list of one quote.
    quote = json.loads(r.text)[0]
    embed = discord.Embed(
        title=quote['anime'],
        description=quote['quote'],
    )
    embed.set_author(
        name=quote['author'],
    )
    embed.set_thumbnail(url=quote['image'])
    await message.channel.send(embed=embed)


async def send_help(message):
    """
    Send to channel the help message.
    
    Parameters:
    message (discord.message.Message): message object send by on_message event.
    """
    embed = discord.Embed(
        title='Available commands',
    )
    for cmd, command in COMMANDS.items():
        embed.add_field(
            name=f"`{cmd}` (`{'`|`'.join(command.aliases)}`)",
            value=command.description,
            inline=False,
        )
    await message.channel.send(embed=embed)


@client.event
async def on_ready():
    """Print out when LRBot is Online"""
    print(f'{client.user} is Online!')


@client.event
async def on_message(message):
    """
    Run commands found in COMMANDS (ALIASES).
    If command is not found, send appropriate message.

    Parameters:
    message (discord.message.Message): message object send by on_message event.
    """
    if message.author == client.user:
        return
    if not message.content.startswith(PREFIX):
        return
    command = message.content[len(PREFIX):].strip()
    if command not in COMMANDS:
        if command not in ALIASES:
            await message.channel.send('Unknown command.')
            return
        command = ALIASES[command]

    if DEBUG: print(command)
    await COMMANDS[command].call(message)


def run():
    """Run bot"""
    client.run(TOKEN)


ALIASES = {
    'r': 'random',
    'rand': 'random',
    'h': 'help',
}

COMMANDS = {
    'help': Command(
        func=send_help,
        description='Outputs this help message',
    ),
    'random': Command(
        func=send_random_quote,
        description='Grabs a random quote from less-real',
    ),
}

# Populate alias list as it's not done by default by Command dataclass.
for alias, original in ALIASES.items():
    COMMANDS[original].aliases.append(alias)

if __name__ == '__main__':
    run()
