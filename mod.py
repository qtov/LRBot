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
        r.raise_for_status()
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
        await db.connect()
        try:
            quote = await self.get_quote(ctx)
        finally:
            await db.disconnect()

        embed = make_quote_embed(quote)
        bot_msg = await ctx.send(embed=embed)

        # add emojis for commands
        await asyncio.gather(
            bot_msg.add_reaction('✅'),
            bot_msg.add_reaction('🔄'),
            bot_msg.add_reaction('❌'),
        )

        reaction, user = await bot.wait_for(
            'reaction_add',
            check=lambda reaction, user: reaction.message.id == bot_msg.id and user == ctx.author,
        )
        
        if reaction.emoji == '✅':
            await asyncio.gather(
                channel.send(embed=embed),
                channel.send(role.mention),
                bot_msg.delete(),
            )
        elif reaction.emoji == '🔄':
            await asyncio.gather(
                bot_msg.delete(),
                self.qotd(ctx, channel, role),
            )
        elif reaction.emoji == '❌':
            await bot_msg.delete()
        else:
            await ctx.send((
                "WELL AREN'T YOU A SMARTYPANTS?!\n"
                "Because of this the reactions won't trigger anymore, serves you right.\n"
                "It took me more to write this message than to put a while loop in, I won't do it."
            ))

    @qotd.error
    async def qotd_error(self, ctx, error):
        # TODO: Probably log this shit
        await ctx.send(str(error).capitalize())
