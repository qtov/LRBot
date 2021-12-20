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
        """Hook for who can access commands in cog"""
        return ctx.author.guild_permissions.manage_messages

    # TODO: implement the check server-side when requesting quote.
    # Aka send a list of blacklisted????? eh, dunno think about it.
    async def get_quote(self, ctx):
        """
        Get quote from API.
        If quote is in quotes db table, retry.

        Returns:
            dict: the json returned by the API.

        Raises:
            httpx.RequestError: Exception while issuing request.
            httpx.HTTPStatusError: 400 and 500 response.
        """
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/random')
        r.raise_for_status()
        quote = json.loads(r.text)
        res = await db.fetch_one(
            query=r'SELECT count(id) FROM quotes WHERE id=:id',
            values={'id': quote['id']},
        )
        # Recurse and find another quote if found in table.
        if res[0]:
            return await self.get_quote(ctx)
        return quote

    async def add_to_db(self, quote):
        """Add a quote to the quotes table in db"""
        await db.execute(
            query=r'INSERT INTO quotes (id) VALUES (:id)',
            values={'id': quote['id']},
        )

    @commands.command()
    async def qotd(self, ctx, channel: discord.TextChannel,
                   role: discord.Role = None, message: discord.message.Message = None):
        """
        Post the quote of the day in <channel>, optionally mentioning [role]
        ✅ - approve the quote and send it to channel + add it to the ignore list.
        🔄 - refresh quote.
        🚫 - refresh quote and add it to the ignore list.
        ❌ - cancel command.
        """
        quote = await self.get_quote(ctx)

        embed = make_quote_embed(quote)
        if message is None:
            bot_msg = await ctx.send(embed=embed)
        else:
            bot_msg = message
            await bot_msg.clear_reactions()
            await bot_msg.edit(embed=embed)

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
        try:
            reaction, user = await bot.wait_for(
                'reaction_add',
                timeout=60*3,  # wait 3 minutes for a reaction, otherwise let it be.
                check=check,
            )
        except asyncio.TimeoutError:
            await asyncio.gather(
                bot_msg.clear_reactions(),
                bot_msg.edit(content='Timed out...', embed=None, delete_after=60),
            )
        
        if reaction.emoji == '✅':
            tasks = [
                self.add_to_db(quote),
                bot_msg.delete(),
            ]

            if role:
                send_task = channel.send(role.mention, embed=embed)
            else:
                send_task = channel.send(embed=embed)
            tasks.append(send_task)

            await asyncio.gather(*tasks)
        elif reaction.emoji == '🔄':
            await self.qotd(ctx, channel, role, bot_msg),
        elif reaction.emoji == '🚫':
            await asyncio.gather(
                self.add_to_db(quote),
                self.qotd(ctx, channel, role, bot_msg),
            )
        elif reaction.emoji == '❌':
            await bot_msg.delete()
        else:
            # Unlikely, but not impossible!
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

    @qotd.after_invoke
    async def qotd_after(self, ctx):
        # Remove message after everything is finished.
        await ctx.message.delete()
