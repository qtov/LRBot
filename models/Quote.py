import re
import nextcord
from settings import LR_URL
from dataclasses import dataclass
from nextcord.embeds import Embed


@dataclass
class Quote:
    """Format for the quote returned by LR's API."""
    id: str
    author: str
    anime: str
    quote: str
    image: str

    def __post_init__(self):
        # Remove <br>'s, there are some, in some quotes.
        self.quote = re.sub(r'<\s*br\s*/?>', '\n', self.quote)

    @property
    def embed(self) -> Embed:
        """Make an embed for the quote."""
        url = f"{LR_URL}/quotes/{self.id}"
        embed = nextcord.Embed(
            title=self.anime,
            description=self.quote,
            url=url,
        )
        embed.set_author(
            name=self.author,
            url=url,
        )
        embed.set_thumbnail(url=self.image)
        return embed
