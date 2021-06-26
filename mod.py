import httpx
import discord
import json
from discord.ext import commands
from quotes import Quotes
from settings import API_URL, LR_URL
from utils import make_quote_embed

class Mod(commands.Cog):
    """Commands that only mods can access"""
    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.manage_messages

    @commands.command()
    async def qotd(self, ctx):
        """Put the quote of the day (mod only)"""
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/random')
        if r.status_code != 200:
            await ctx.send('Cannot get quote, request timed out.')
            return
        quote = json.loads(r.text)
        embed = make_quote_embed(quote)
        await ctx.send(embed=embed)
        await ctx.message.delete()
