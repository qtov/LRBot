import httpx
import json
from discord.ext import commands
from settings import API_URL
from utils import make_quote_embed


class Quotes(commands.Cog):
    """Commands that deal with quotes"""
    @commands.command(name="random", aliases=['r', 'rand'])
    async def random(self, ctx):
        """Get a random quote"""
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/random')
        r.raise_for_status()
        quote = json.loads(r.text)
        embed = make_quote_embed(quote)
        await ctx.send(embed=embed)

    @random.error
    async def random_error(self, ctx, error):
        if isinstance(error, (httpx.HTTPStatusError, httpx.RequestError)):
            await ctx.send('There was an error, please try again later.')
            print(error)

    @commands.command(name="character", aliases=['c', 'char'])
    async def character(self, ctx, *, character):
        """Get a random quote of a character"""
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/character/{character}')
        r.raise_for_status()

        quote = json.loads(r.text)
        if 'id' not in quote:
            await ctx.send('No quote found.')
            return

        embed = make_quote_embed(quote)
        await ctx.send(embed=embed)

    @character.error
    async def character_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('Missing character name.\n`lr!help character` for more help.')
        elif isinstance(error, (httpx.HTTPStatusError, httpx.RequestError)):
            await ctx.send('There was an error, please try again later.')
            print(error)
