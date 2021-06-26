import json
import httpx
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from settings import (
    PREFIX, DISCORD_TOKEN, ACTIVITY_NAME, ACTIVITY_TYPE, LR_URL, API_URL
)
from resources import bot
from mod import Mod
from quotes import Quotes
try:
    import uvloop
except ModuleNotFoundError:
    print('[*] Running without `uvloop`')
    uvloop = ...

if uvloop is not ...:
    uvloop.install()


@bot.event
async def on_ready():
    """Print out when LRBot is Online"""
    print(f'{bot.user} is Online!')
    activity = discord.Activity(name=ACTIVITY_NAME,
                                type=ACTIVITY_TYPE)
    await bot.change_presence(activity=activity)


@bot.event
async def on_message(message):
    """Run appropriate commands."""
    if message.author == bot.user:
        return
    if not message.content.startswith(PREFIX):
        if message.author.id == 173054058624450561:
            if message.content.startswith('!lrbot'):
                msg = message.content[6:]
                await message.delete()
                await message.channel.send(msg)
        return
    await bot.process_commands(message)


def run():
    """Run bot"""
    bot.add_cog(Mod())
    bot.add_cog(Quotes())
    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    run()
