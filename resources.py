import discord
from discord.ext import commands
import TenGiphPy
from settings import PREFIX, TENOR_TOKEN, DESCRIPTION

tenor = TenGiphPy.Tenor(token=TENOR_TOKEN)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION,
                   intents=intents)
