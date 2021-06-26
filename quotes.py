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
        print(quote)
        embed = make_quote_embed(quote)
        await ctx.send(embed=embed)

    @random.error
    async def random_error(self, ctx, error):
        await ctx.send(str(error).capitalize())

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
        await ctx.send(str(error).capitalize() + '\n`lr!help character` for more help.')
