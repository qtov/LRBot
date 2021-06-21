import json
import httpx
import discord
from schemas.command import Command
from settings import (
    DEBUG, TOKEN, PREFIX, ACTIVITY_NAME, ACTIVITY_TYPE, LR_URL, API_URL
)
from resources import client, tenor
try:
    import uvloop
except ModuleNotFoundError:
    print('[*] Running without `uvloop`')
    uvloop = ...

if uvloop is not ...:
    uvloop.install()


async def send_random_quote(message, args=None):
    """
    Send to channel a random quote from less-real api.

    Parameters:
    message (discord.message.Message): message object send by on_message event.
    """
    async with httpx.AsyncClient() as http_client:
        r = await http_client.get(f'{API_URL}/random')
    if r.status_code != 200:
        await message.channel.send('Cannot get quote, request timed out.')
        return
    # less-real returns a list of one quote.
    quote = json.loads(r.text)
    url = f"{LR_URL}/quotes/{quote['id']}"
    embed = discord.Embed(
        title=quote['anime'],
        description=quote['quote'],
        url=url,
    )
    embed.set_author(
        name=quote['author'],
        url=url,
    )
    embed.set_thumbnail(url=quote['image'])
    await message.channel.send(embed=embed)


async def send_character_quote(message, args=None):
    """
    Send to channel a random quote of a character from less-real api.

    Parameters:
    message (discord.message.Message): message object send by on_message event.
    """
    character = ' '.join(args)
    async with httpx.AsyncClient() as http_client:
        r = await http_client.get(f'{API_URL}/character/{character}')
    if r.status_code != 200:
        await message.channel.send('Cannot get quote, request timed out.')
        return
    # less-real returns a list of one quote.
    quote = json.loads(r.text)
    if 'id' not in quote:
        await message.channel.send('No quote found.')
        return
    url = f"{LR_URL}/quotes/{quote['id']}"
    embed = discord.Embed(
        title=quote['anime'],
        description=quote['quote'],
        url=url,
    )
    embed.set_author(
        name=quote['author'],
        url=url,
    )
    embed.set_thumbnail(url=quote['image'])
    await message.channel.send(embed=embed)


async def send_help(message, args=None):
    """
    Send to channel the help message.
    
    Parameters:
    message (discord.message.Message): message object send by on_message event.
    """
    embed = discord.Embed(
        title='Available commands',
    )
    for cmd, command in COMMANDS.items():
        name = f"`{cmd}` (`{'`|`'.join(command.aliases)}`)"
        if command.args is not None:
            name += f' {command.args}'
        embed.add_field(
            name=name,
            value=command.description,
            inline=False,
        )
    await message.channel.send(embed=embed)


@client.event
async def on_ready():
    """Print out when LRBot is Online"""
    print(f'{client.user} is Online!')
    activity = discord.Activity(name='lr!help',
                                type=discord.ActivityType.listening)
    await client.change_presence(activity=activity)


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
    split_command = message.content[len(PREFIX):].split(' ')
    command = split_command[0]
    args = split_command[1:]
    if command not in COMMANDS:
        if command not in ALIASES:
            await message.channel.send((
                'Unknown command.\n'
                f'Use `{PREFIX}help` for a list of available commands.'
            ))
            return
        command = ALIASES[command]

    if DEBUG: print(command)
    await COMMANDS[command].call(message, args)


def run():
    """Run bot"""
    client.run(TOKEN)


ALIASES = {
    'r': 'random',
    'rand': 'random',
    'h': 'help',
    'c': 'character',
    'char': 'character',
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
    'character': Command(
        func=send_character_quote,
        args='<character>',
        description='Grabs a random character quote from less-real',
    ),
}

# Populate alias list.
for alias, original in ALIASES.items():
    COMMANDS[original].aliases.append(alias)

if __name__ == '__main__':
    run()
