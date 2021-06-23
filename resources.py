import discord
from discord.ext import commands
import TenGiphPy
from settings import PREFIX, TENOR_TOKEN, DESCRIPTION

tenor = TenGiphPy.Tenor(token=TENOR_TOKEN)

intents = discord.Intents.default()
intents.members = True

help_command = commands.DefaultHelpCommand(no_category='Commands')
bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION,
                   intents=intents, help_command=help_command)
