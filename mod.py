import discord
import asyncio
import httpx
import json
from discord.ext import commands
from settings import API_URL, DEBUG
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
        return quote

    async def add_to_db(self, quote):
        await db.execute(
            query=r'INSERT INTO quotes (id) VALUES (:id)',
            values={'id': quote['id']},
        )

    @commands.command()
    async def qotd(self, ctx, channel: discord.TextChannel, role: discord.Role = None):
        """
        Post the quote of the day in <channel>, optionally mentioning [role]
        ✅ - approve the quote and send it to channel + add it to the ignore list.
        🔄 - refresh quote.
        🚫 - refresh quote and add it to the ignore list.
        ❌ - cancel command.
        """
        # async with db:
        quote = await self.get_quote(ctx)

        embed = make_quote_embed(quote)
        bot_msg = await ctx.send(embed=embed)

        # add emojis for commands
        emojis = ('✅', '🔄', '🚫', '❌')
        tasks = (bot_msg.add_reaction(emoji) for emoji in emojis)
        await asyncio.gather(*tasks)

        def check(reaction, user):
            if (
                reaction.message.id == bot_msg.id
                and user == ctx.author
                and reaction.emoji in emojis
            ):
                return True
            return False
        reaction, user = await bot.wait_for(
            'reaction_add',
            timeout=60*3,  # wait 3 minutes for a reaction, otherwise let it be.
            check=check,
        )
        
        if reaction.emoji == '✅':
            tasks = [
                self.add_to_db(quote),
                channel.send(embed=embed),
                bot_msg.delete(),
            ]

            if role:
                tasks.insert(2, channel.send(role.mention))

            await asyncio.gather(*tasks)
        elif reaction.emoji == '🔄':
            await asyncio.gather(
                bot_msg.delete(),
                self.qotd(ctx, channel, role),
            )
        elif reaction.emoji == '🚫':
            await asyncio.gather(
                self.add_to_db(quote),
                bot_msg.delete(),
                self.qotd(ctx, channel, role),
            )
        elif reaction.emoji == '❌':
            await bot_msg.delete()
        else:
            # Unlikely, but never impossible!
            await asyncio.gather(
                ctx.send("WELL... AREN'T YOU A SMARTYPANTS?!\n"),
                bot_msg.delete(),
            )

    @qotd.error
    async def qotd_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('Please specify channel.\n`lr!help qtod` for more help.')
        elif isinstance(error, (httpx.HTTPStatusError, httpx.RequestError)):
            await ctx.send('There was an error, please try again later.')
            print(error)

    @qotd.before_invoke
    async def qotd_before(self, ctx):
        DEBUG and print('Connecting to db.')
        await db.connect()

    @qotd.after_invoke
    async def qotd_after(self, ctx):
        DEBUG and print('Disconnecting from db')
        await db.disconnect()
