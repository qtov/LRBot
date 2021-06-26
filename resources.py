import discord
import TenGiphPy
from databases import Database
from discord.ext import commands
from settings import PREFIX, TENOR_TOKEN, DESCRIPTION


tenor = TenGiphPy.Tenor(token=TENOR_TOKEN)

intents = discord.Intents.default()
intents.members = True

db = Database('sqlite:///data.db')

bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION,
                   intents=intents)
