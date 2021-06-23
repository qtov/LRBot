import json
import httpx
import discord
from discord.ext import commands
from settings import (
    PREFIX, DISCORD_TOKEN, ACTIVITY_NAME, ACTIVITY_TYPE, LR_URL, API_URL
)
from resources import bot
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
        return
    await bot.process_commands(message)


# TODO: move to different file once more Cogs are introduced.
class Quotes(commands.Cog):
    """Commands that deal with quotes"""

    def make_quote_embed(self, quote):
        """
        Make an embed for a quote.

        parameters:
        quote: quote object returned from API.
            'id': int|str, quote id for linkining
            'author: str, author name
            'image': str, link to image of character face
            'anime': str, anime name
            'quote': str, quote
        """
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
        return embed

    @commands.command(aliases=['r', 'rand'])
    async def random(self, ctx):
        """Get a random quote"""
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/random')
        if r.status_code != 200:
            await ctx.send('Cannot get quote, request timed out.')
            return
        quote = json.loads(r.text)
        embed = self.make_quote_embed(quote)
        await ctx.send(embed=embed)

    @commands.command(aliases=['c', 'char'])
    async def character(self, ctx, *, character):
        """Get a random quote of a character"""
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/character/{character}')
        if r.status_code != 200:
            await ctx.send('Cannot get quote, request timed out.')
            return
        quote = json.loads(r.text)
        if 'id' not in quote:
            await ctx.send('No quote found.')
            return
        embed = self.make_quote_embed(quote)
        await ctx.send(embed=embed)
    

def run():
    """Run bot"""
    bot.add_cog(Quotes())
    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    run()
