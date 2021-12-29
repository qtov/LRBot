import re
import nextcord
from dataclasses import dataclass
from nextcord.embeds import Embed
from typing import Optional
from settings import LR_URL


@dataclass
class Quote:
    """Format for the quote returned by LR's API."""
    id: str
    author: str
    anime: str
    quote: str
    image: str
    label: Optional[str] = None
    distance: Optional[int] = None

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
