import httpx
from nextcord.ext import commands
from nextcord.ext.commands.context import Context
from settings import API_URL
from resources import logger
from models.Quote import Quote


class Quotes(commands.Cog):
    """Commands that deal with quotes"""
    @commands.command(name="random", aliases=['rand'])
    async def random(self, ctx: Context) -> None:
        """Get a random quote from LR and send it."""
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/random')
        r.raise_for_status()
        quote = Quote(**r.json())
        await ctx.send(embed=quote.embed)

    @random.error
    async def random_error(self, ctx: Context, error: commands.errors.CommandError) -> None:
        """Exception handler for the random command."""
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send('There was an error, please try again later.')
            logger.info(error)

    @commands.command(name="character", aliases=['char'])
    async def character(self, ctx: Context, *, character: str) -> None:
        """Get a random quote of a character and send it."""
        async with httpx.AsyncClient() as http_client:
            r = await http_client.get(f'{API_URL}/character/{character}')
        r.raise_for_status()

        quote_json = r.json()
        if 'id' not in quote_json:
            await ctx.send('No quote found.')
            return

        quote = Quote(**quote_json)
        await ctx.send(embed=quote.embed)

    @character.error
    async def character_error(self, ctx: Context, error: commands.errors.CommandError) -> None:
        """Exception handler for the character command."""
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('Missing character name.\n`lr!help character` for more help.')
        elif isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send('There was an error, please try again later.')
            logger.warning(error)
