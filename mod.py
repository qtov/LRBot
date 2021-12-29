import nextcord
import asyncio
import httpx
from nextcord.ext import commands
from settings import API_URL
from resources import db, bot, logger
from utils import make_quote_embed


class Mod(commands.Cog):
    """Commands that only mods can access"""
    async def cog_check(self, ctx):
        """Hook for who can access commands in cog"""
        return ctx.author.guild_permissions.manage_messages

    async def get_quote(self, retries=500):
        """
        Get quote from API.
        If quote is in quotes db table, retry.

        Parameters:
            retries (int): how many retries to get a whitelisted quote.

        Returns:
            dict: the json returned by the API.

        Raises:
            httpx.RequestError: Exception while issuing request.
            httpx.HTTPStatusError: 400 and 500 response.
        """
        for retry in range(retries):
            async with httpx.AsyncClient() as http_client:
                r = await http_client.get(f'{API_URL}/random')
            r.raise_for_status()
            quote = r.json()
            res = await db.fetch_one(
                query=r'SELECT count(id) FROM quotes WHERE id=:id',
                values={'id': quote['id']},
            )
            # Quote not in db, break.
            if not res[0]:
                break
        return quote

    async def add_to_db(self, quote):
        """Add a quote to the quotes table in db"""
        await db.execute(
            query=r'INSERT INTO quotes (id) VALUES (:id)',
            values={'id': quote['id']},
        )

    async def qotd_put_quote(self, ctx, embed, emojis, message=None):
        if message is None:
            bot_msg = await ctx.send(embed=embed)
        else:
            bot_msg = message
            await asyncio.gather(
                bot_msg.clear_reactions(),
                bot_msg.edit(embed=embed),
            )

        # add emojis for commands
        tasks = (bot_msg.add_reaction(emoji) for emoji in emojis)
        await asyncio.gather(*tasks)
        return bot_msg

    async def qotd(self, ctx, channel: nextcord.TextChannel,
                   role: nextcord.Role = None, message: nextcord.message.Message = None):
        """
        Post the quote of the day in <channel>, optionally mentioning [role]
        ✅ - approve the quote and send it to channel + add it to the ignore list.
        🔄 - refresh quote.
        🚫 - refresh quote and add it to the ignore list.
        ❌ - cancel command.
        """
        async def send():
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

        async def refresh():
            await self.qotd(ctx, channel, role, bot_msg)

        async def refresh_ignore():
            await asyncio.gather(
                self.add_to_db(quote),
                self.qotd(ctx, channel, role, bot_msg),
            )

        async def cancel():
            await bot_msg.delete()

        reactions = {
            '✅': send,
            '🔄': refresh,
            '🚫': refresh_ignore,
            '❌': cancel,
        }
        emojis = reactions.keys()
        quote = await self.get_quote()
        embed = make_quote_embed(quote)
        bot_msg = await self.qotd_put_quote(ctx, embed, emojis, message)

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
                timeout=5*60,  # wait 5 minutes for a reaction, otherwise let it be.
                check=check,
            )
            await reactions[reaction.emoji]()
        except asyncio.TimeoutError:
            await asyncio.gather(
                bot_msg.clear_reactions(),
                bot_msg.edit(content='qotd timed out...', embed=None, delete_after=10*60),
            )

    @commands.command(name='qotd')
    async def qotd_wrapper(self, ctx, channel: nextcord.TextChannel,
            role: nextcord.Role = None):
        """Wrapper for qotd method."""
        await self.qotd(ctx, channel, role)

    @qotd_wrapper.error
    async def qotd_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('Please specify channel.\n`lr!help qtod` for more help.')
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send('There was an error, please try again later.')
            logger.warning(error)

    @qotd_wrapper.after_invoke
    async def qotd_after(self, ctx):
        # Remove message after everything is finished.
        await ctx.message.delete()
