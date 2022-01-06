import nextcord
import asyncio
import httpx
from nextcord.ext import commands
from nextcord.ext.commands.context import Context
from nextcord.message import Message
from collections.abc import KeysView
from settings import API_URL
from resources import db, bot, logger
from models.Quote import Quote


class Mod(commands.Cog):
    """Commands that only mods can access"""
    async def cog_check(self, ctx: Context) -> bool:
        """Hook for who can access commands in cog"""
        return ctx.author.guild_permissions.manage_messages

    async def get_random_quote(self, retries: int = 50) -> Quote:
        """
        Get quote from API.
        If quote is in quotes db table, retry.

        Parameters:
            retries: how many retries to get a whitelisted quote.

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
            quote = Quote(**r.json())
            res = await db.fetch_one(
                query=r'SELECT count(id) FROM quotes WHERE id=:id',
                values={'id': quote.id},
            )
            # Quote not in db, break.
            if not res[0]:
                break
        return quote

    async def get_quote(self, qid: int) -> Quote:
        """
        Get quote from API based on its id. (qid).
        """
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/quote/{qid}')
        r.raise_for_status()
        quote = Quote(**r.json())
        return quote

    async def add_to_db(self, quote: Quote) -> None:
        """Add a quote to the quotes table in db"""
        await db.execute(
            query=r'INSERT INTO quotes (id) VALUES (:id)',
            values={'id': quote.id},
        )

    async def qotd_put_quote(self, ctx: Context, quote: Quote,
                             emojis: KeysView, message: Message = None) -> Message:
        if message is None:
            bot_msg = await ctx.send(embed=quote.embed)
        else:
            bot_msg = message
            await asyncio.gather(
                bot_msg.clear_reactions(),
                bot_msg.edit(embed=quote.embed),
            )

        # add emojis for commands
        tasks = (bot_msg.add_reaction(emoji) for emoji in emojis)
        await asyncio.gather(*tasks)
        return bot_msg

    @commands.command(name='qotd')
    async def qotd_wrapper(self, ctx: Context, channel: nextcord.TextChannel,
                           role: nextcord.Role = None) -> None:
        """
        Post the quote of the day in <channel>, optionally mentioning [role]
        ✅ - approve the quote and send it to channel + add it to the ignore list.
        🔄 - refresh quote.
        🚫 - refresh quote and add it to the ignore list.
        ❌ - cancel command.
        """
        await self.qotd(ctx, channel, role)

    @commands.command(name='quoteid', aliases=['qid'])
    async def quoteid(self, ctx: Context, qid: int, channel: nextcord.TextChannel,
                      role: nextcord.Role = None) -> None:
        """Send quote to channel based on its id."""
        quote = await self.get_quote(qid)
        mention = role.mention if role is not None else None
        await channel.send(mention, embed=quote.embed)

    @quoteid.after_invoke
    async def quoteid_after(self, ctx: Context) -> None:
        """Delete mod command."""
        await ctx.message.delete()

    async def qotd(self, ctx, channel: nextcord.TextChannel,
                   role: nextcord.Role = None, message: Message = None) -> None:
        """
        Post the quote of the day in <channel>, optionally mentioning [role]
        ✅ - approve the quote and send it to channel + add it to the ignore list.
        🔄 - refresh quote.
        🚫 - refresh quote and add it to the ignore list.
        ❌ - cancel command.
        """
        async def send() -> None:
            tasks = [
                self.add_to_db(quote),
                bot_msg.delete(),
            ]

            if role:
                send_task = channel.send(role.mention, embed=quote.embed)
            else:
                send_task = channel.send(embed=quote.embed)
            tasks.append(send_task)
            await asyncio.gather(*tasks)

        async def refresh() -> None:
            await self.qotd(ctx, channel, role, bot_msg)

        async def refresh_ignore() -> None:
            await asyncio.gather(
                self.add_to_db(quote),
                self.qotd(ctx, channel, role, bot_msg),
            )

        async def cancel() -> None:
            await bot_msg.delete()

        reactions = {
            '✅': send,
            '🔄': refresh,
            '🚫': refresh_ignore,
            '❌': cancel,
        }
        emojis = reactions.keys()
        quote = await self.get_random_quote()
        bot_msg = await self.qotd_put_quote(ctx, quote, emojis, message)

        def check(reaction: nextcord.reaction.Reaction, user: nextcord.member.Member):
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
        except asyncio.TimeoutError:
            await asyncio.gather(
                bot_msg.clear_reactions(),
                bot_msg.edit(content='qotd timed out...', embed=None, delete_after=10*60),
            )
            return
        # Do action.
        await reactions[reaction.emoji]()

    @qotd_wrapper.error
    async def qotd_error(self, ctx: Context, error: commands.errors.CommandError) -> None:
        """Exception handler for the qotd command."""
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('Please specify channel.\n`lr!help qtod` for more help.')
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send('There was an error, please try again later.')
            logger.warning(error)

    @qotd_wrapper.after_invoke
    async def qotd_after(self, ctx: Context) -> None:
        """Remove message after everything is finished."""
        await ctx.message.delete()
