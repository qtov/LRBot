import discord
from settings import LR_URL

def make_quote_embed(quote):
    """
    Make an embed for a quote.

    parameters:
    quote: quote object returned from API.
        'id': int|str, quote id for linkining
        'author: str, author name
        'image': str, link to image of character face
        'anime': str, anime name
        'quote': str, quote
    """
    url = f"{LR_URL}/quotes/{quote['id']}"
    embed = discord.Embed(
        title=quote['anime'],
        description=quote['quote'],
        url=url,
    )
    embed.set_author(
        name=quote['author'],
        url=url,
    )
    embed.set_thumbnail(url=quote['image'])
    return embed
