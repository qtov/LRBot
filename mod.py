import discord
import asyncio
import httpx
import json
from discord.ext import commands
from settings import API_URL
from resources import db, bot
from utils import make_quote_embed


class Mod(commands.Cog):
    """Commands that only mods can access"""
    def __init__(self):
        pass

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.manage_messages

    # TODO: implement the check server-side when requesting quote.
    # Aka send a list of blacklisted????? eh, dunno think about it.
    async def get_quote(self, ctx):
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/random')
        if r.status_code != 200:
            return
        quote = json.loads(r.text)
        res = await db.fetch_one(
            query=r'SELECT count(id) FROM quotes WHERE id=:id',
            values={'id': quote['id']},
        )
        # Recurse and find another quote, unlikely, but who knows, lel.
        if res[0]:
            return await self.get_quote(ctx)
        await db.execute(
            query=r'INSERT INTO quotes (id) VALUES (:id)',
            values={'id': quote['id']},
        )
        return quote

    @commands.command()
    async def qotd(self, ctx, channel: discord.TextChannel, role: discord.Role):
        """Put the quote of the day"""
        if channel is None:
            await ctx.send("Please specify channel.")
            return
        await db.connect()
        try:
            quote = await self.get_quote(ctx)
        finally:
            await db.disconnect()

        # In case quote cannot be gotten.
        if quote is None:
            await ctx.send('Cannot get quote, request timed out.')
            return
        embed = make_quote_embed(quote)
        bot_msg = await ctx.send(embed=embed)

        # add emojis for commands
        await asyncio.gather(
            bot_msg.add_reaction('✅'),
            bot_msg.add_reaction('🔄'),
            bot_msg.add_reaction('❌'),
        )

        def check(reaction, user):
            return reaction.message.id == bot_msg.id and user == ctx.author
        reaction, user = await bot.wait_for('reaction_add', check=check)
        
        if reaction.emoji == '✅':
            await asyncio.gather(
                channel.send(embed=embed),
                channel.send(role.mention),
                bot_msg.delete(),
            )
        elif reaction.emoji == '🔄':
            asyncio.gather(
                bot_msg.delete(),
                self.qotd(ctx, channel, role),
            )
        elif reaction.emoji == '❌':
            await bot_msg.delete()
        else:
            await ctx.send("Didn't plan that, it won't care about your next reaction, lel")
