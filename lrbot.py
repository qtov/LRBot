import discord
import asyncio
from settings import (
    PREFIX, DISCORD_TOKEN, ACTIVITY_NAME, ACTIVITY_TYPE
)
from resources import bot, db
from mod import Mod
from quotes import Quotes
try:
    import uvloop
except ModuleNotFoundError:
    print('[*] Running without `uvloop`')
    uvloop = ...

if uvloop is not ...:
    uvloop.install()


async def make_db_schema():
    async with db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INT PRIMARY KEY,
                postedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')


@bot.event
async def on_ready():
    """Print out when LRBot is Online"""
    db_task = asyncio.create_task(make_db_schema())
    print(f'{bot.user} is Online!')
    activity = discord.Activity(name=ACTIVITY_NAME,
                                type=ACTIVITY_TYPE)
    await bot.change_presence(activity=activity)
    await db_task


@bot.event
async def on_message(message):
    """Run appropriate commands."""
    if message.author == bot.user:
        return
    if not message.content.startswith(PREFIX):
        return
    await bot.process_commands(message)


if __name__ == '__main__':
    bot.add_cog(Mod())
    bot.add_cog(Quotes())
    bot.run(DISCORD_TOKEN)
