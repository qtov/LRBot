import pytest
from cogs.Quotes import Quotes


quotes = Quotes()


@pytest.mark.asyncio
async def test_random():
    for i in range(5):
        quote = await quotes.get_random_quote()
        assert quote is not None
        assert len(quote.quote) > 5


@pytest.mark.asyncio
async def test_character():
    quote = await quotes.get_character_quote('yagami')
    assert quote.author == 'Light Yagami'
    assert quote.anime == 'Death Note'
    assert len(quote.quote) > 5

    quote = await quotes.get_character_quote('lelouch')
    assert quote.author == 'Lelouch Lamperouge'
    assert quote.anime.startswith('Code Geass')
    assert len(quote.quote) > 5
