import httpx
import json
from discord.ext import commands
from settings import API_URL
from utils import make_quote_embed


class Quotes(commands.Cog):
    """Commands that deal with quotes"""
    @commands.command(aliases=['r', 'rand'])
    async def random(self, ctx):
        """Get a random quote"""
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/random')
        if r.status_code != 200:
            await ctx.send('Cannot get quote, request timed out.')
            return
        quote = json.loads(r.text)
        print(quote)
        embed = make_quote_embed(quote)
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
        embed = make_quote_embed(quote)
        await ctx.send(embed=embed)
